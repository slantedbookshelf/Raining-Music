# -*- coding: utf-8 -*-
"""
Batch fetch artist avatars from NetEase Cloud Music, upload to MinIO,
and generate SQL to update tb_artist.avatar.
Skips id 2 (何真真) and 30 (张杰) — already done by user.
"""
import json
import re
import sys
import time
import io
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from minio import Minio
from minio.error import S3Error
from PIL import Image

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}
HEADERS = {"Referer": "https://music.163.com", **UA}

MYSQL = r"C:/Program Files/MySQL/MySQL Server 8.0/bin/mysql.exe"
LIST_FILE = r"D:/Files/WorkSpace/vibe-coding/vibe-music-master/vibe-music-master/vibe-music-client/.workbuddy/artists_list.tsv"
SQL_OUT = r"D:/Files/WorkSpace/vibe-coding/vibe-music-master/vibe-music-master/vibe-music-client/.workbuddy/avatar_updates.sql"
REPORT_OUT = r"D:/Files/WorkSpace/vibe-coding/vibe-music-master/vibe-music-master/vibe-music-client/.workbuddy/avatar_report.json"

MINIO_ENDPOINT = "localhost:9095"
MINIO_ACCESS = "minioadmin"
MINIO_SECRET = "minioadmin"
BUCKET = "vibe-music-data"
PREFIX = "artists"

SKIP_IDS = {2, 30}
NETEASE_DISABLED = False

SEARCH_URL = "http://music.163.com/api/search/get/web"
HEADERS = {"Referer": "http://music.163.com", "User-Agent": "Mozilla/5.0"}

minio_client = Minio(MINIO_ENDPOINT, access_key=MINIO_ACCESS, secret_key=MINIO_SECRET, secure=False)


def clean_name(name: str) -> str:
    """Remove junk like '(???)', trailing ?, garbled chars."""
    n = name.strip()
    n = re.sub(r"[（(][^)）]*[?？?][^)）]*[)）]", "", n)  # parens containing ?
    n = re.sub(r"[?？]+$", "", n).strip()  # trailing ?
    return n


def query_candidates(name: str) -> list:
    """Generate search query variants, best first."""
    cands = []
    cleaned = clean_name(name)
    if cleaned:
        cands.append(cleaned)
    # strip any parenthetical suffix: 'IU (아이유)' -> 'IU'
    no_paren = re.sub(r"[（(].*", "", name).strip()
    if no_paren and no_paren not in cands:
        cands.append(no_paren)
    return cands


def name_key(s: str) -> str:
    return re.sub(r"[^a-z0-9\u4e00-\u9fff]", "", s.lower())


def match_ok(query: str, artist: dict) -> bool:
    """Check the netease result plausibly matches the query name."""
    q = name_key(query)
    if not q:
        return False
    candidates = [artist.get("name", "")]
    candidates += artist.get("alias") or []
    candidates += artist.get("transNames") or []
    if artist.get("trans"):
        candidates.append(artist["trans"])
    for c in candidates:
        c = name_key(c or "")
        if not c:
            continue
        if c == q or q in c or c in q:
            return True
        # allow partial overlap for cleaned names (e.g. 'IU')
        if len(q) >= 2 and (q.startswith(c) or c.startswith(q)) and len(c) >= 2:
            return True
    return False


def search_artist(name: str):
    """Returns (artist_dict|None, rate_limited: bool)."""
    for attempt in range(2):
        rl = False
        for q in query_candidates(name):
            try:
                r = requests.get(SEARCH_URL, params={"s": q, "type": 100, "limit": 5},
                                 headers=HEADERS, timeout=15)
                r.raise_for_status()
                data = r.json()
                if data.get("code") == 405:
                    rl = True
                    break
                artists = (data.get("result") or {}).get("artists") or []
                if artists:
                    for a in artists:
                        if match_ok(name, a):
                            return a, False
                    return artists[0], False
            except Exception:
                pass
            time.sleep(1.2)
        if rl:
            return None, True
        time.sleep(2)
    return None, False


BING_HEADERS = {**UA, "Referer": "https://cn.bing.com/"}


def bing_image_urls(query: str, n: int = 8) -> list:
    """Scrape direct image URLs from Bing image search."""
    try:
        r = requests.get("https://cn.bing.com/images/search",
                         params={"q": query, "form": "HDRSC2", "first": "1"},
                         headers=BING_HEADERS, timeout=15)
        r.raise_for_status()
        urls = re.findall(r'murl&quot;:&quot;(.*?)&quot;', r.text)
        # dedupe, keep http(s)
        seen, out = set(), []
        for u in urls:
            u = u.replace("\\u002f", "/")
            if u.startswith("http") and u not in seen:
                seen.add(u)
                out.append(u)
            if len(out) >= n:
                break
        return out
    except Exception as e:
        print(f"  bing search failed ({query}): {e}", flush=True)
        return []


def validate_image(data: bytes, min_side: int = 150) -> bool:
    try:
        img = Image.open(io.BytesIO(data))
        img.verify()
        img = Image.open(io.BytesIO(data))
        w, h = img.size
        return w >= min_side and h >= min_side and len(data) >= 5000
    except Exception:
        return False


def download_from_bing(name: str):
    for u in bing_image_urls(f"{name} 歌手"):
        try:
            r = requests.get(u, headers=BING_HEADERS, timeout=15)
            if r.status_code != 200:
                continue
            data = r.content
            ct = r.headers.get("content-type", "")
            if not ct.startswith("image/") and not u.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                continue
            if not validate_image(data):
                continue
            return data
        except Exception:
            continue
    return None


def download_image(pic_url: str):
    url = pic_url.replace("http://", "https://") + "?param=500y500"
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    ct = r.headers.get("content-type", "")
    data = r.content
    if not ct.startswith("image/") or len(data) < 5000:
        raise ValueError(f"bad image: ct={ct}, size={len(data)}")
    return data, ct


def process_artist(artist_id: int, name: str, netease_ok: bool = True):
    cname = clean_name(name)
    if not cname:
        return {"id": artist_id, "name": name, "status": "skip_empty_name"}
    try:
        img_data = None
        source = None
        netease_name = None
        if netease_ok:
            result, rl = search_artist(cname)
            if result:
                pic = result.get("picUrl") or result.get("img1v1Url")
                if pic:
                    try:
                        url = pic.replace("http://", "https://") + "?param=500y500"
                        r = requests.get(url, headers=HEADERS, timeout=20)
                        r.raise_for_status()
                        if r.headers.get("content-type", "").startswith("image/") and len(r.content) >= 5000:
                            img_data = r.content
                            source = "netease"
                            netease_name = result.get("name")
                    except Exception:
                        pass
            if rl:
                global NETEASE_DISABLED
                NETEASE_DISABLED = True
                print("  >>> NetEase rate limited — switching to Bing for the rest", flush=True)
        if img_data is None:
            img_data = download_from_bing(cname)
            source = "bing"
        if img_data is None:
            return {"id": artist_id, "name": name, "status": "no_image"}
        obj_name = f"{PREFIX}/{artist_id}.jpg"
        minio_client.put_object(BUCKET, obj_name, io.BytesIO(img_data),
                                length=len(img_data), content_type="image/jpeg")
        return {"id": artist_id, "name": name, "status": "ok", "source": source,
                "netease_name": netease_name, "bytes": len(img_data)}
    except Exception as e:
        return {"id": artist_id, "name": name, "status": "error", "error": str(e)[:200]}


def main():
    artists = []
    with open(LIST_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            aid, name = line.split("\t", 1)
            if int(aid) in SKIP_IDS:
                continue
            artists.append((int(aid), name))

    print(f"processing {len(artists)} artists (sequential, throttled)...", flush=True)
    results = []
    done = 0
    for aid, name in artists:
        res = process_artist(aid, name, netease_ok=not NETEASE_DISABLED)
        results.append(res)
        done += 1
        if done % 10 == 0 or res["status"] != "ok":
            print(f"[{done}/{len(artists)}] {res}", flush=True)
        time.sleep(1.0)

    ok = [r for r in results if r["status"] == "ok"]
    failed = [r for r in results if r["status"] != "ok"]

    with open(SQL_OUT, "w", encoding="utf-8") as f:
        f.write("USE vibe_music;\n")
        for r in sorted(ok, key=lambda x: x["id"]):
            f.write(f"UPDATE tb_artist SET avatar='http://localhost:9095/vibe-music-data/artists/{r['id']}.jpg' WHERE id={r['id']};\n")

    with open(REPORT_OUT, "w", encoding="utf-8") as f:
        json.dump({"ok": sorted(ok, key=lambda x: x["id"]),
                   "failed": sorted(failed, key=lambda x: x["id"])},
                  f, ensure_ascii=False, indent=2)

    print(f"DONE ok={len(ok)} failed={len(failed)}", flush=True)
    for r in failed:
        print(f"  FAILED id={r['id']} name={r['name']} status={r['status']} {r.get('error','')}", flush=True)


if __name__ == "__main__":
    main()
