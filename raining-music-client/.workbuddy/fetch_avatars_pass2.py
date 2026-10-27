# -*- coding: utf-8 -*-
"""Second pass: retry failed artists via Bing, force HTTPS on image URLs."""
import io
import json
import re
import time

import requests
from minio import Minio
from PIL import Image

REPORT = r"D:/Files/WorkSpace/vibe-coding/vibe-music-master/vibe-music-master/vibe-music-client/.workbuddy/avatar_report.json"
SQL_OUT = r"D:/Files/WorkSpace/vibe-coding/vibe-music-master/vibe-music-master/vibe-music-client/.workbuddy/avatar_updates2.sql"
REPORT2 = r"D:/Files/WorkSpace/vibe-coding/vibe-music-master/vibe-music-master/vibe-music-client/.workbuddy/avatar_report2.json"

MINIO_ENDPOINT = "localhost:9095"
BUCKET = "vibe-music-data"

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
      "Referer": "https://cn.bing.com/"}
minio_client = Minio(MINIO_ENDPOINT, access_key="minioadmin", secret_key="minioadmin", secure=False)


def bing_image_urls(query: str, n: int = 15) -> list:
    try:
        r = requests.get("https://cn.bing.com/images/search",
                         params={"q": query, "form": "HDRSC2", "first": "1"},
                         headers=UA, timeout=15)
        r.raise_for_status()
        urls = re.findall(r'murl&quot;:&quot;(.*?)&quot;', r.text)
        seen, out = set(), []
        for u in urls:
            u = u.replace("\\u002f", "/").replace("http://", "https://")
            if u.startswith("https") and u not in seen:
                seen.add(u)
                out.append(u)
            if len(out) >= n:
                break
        return out
    except Exception as e:
        print(f"  bing search failed ({query}): {e}", flush=True)
        return []


def validate_image(data: bytes, min_side: int = 120) -> bool:
    try:
        img = Image.open(io.BytesIO(data))
        img.verify()
        img = Image.open(io.BytesIO(data))
        w, h = img.size
        return w >= min_side and h >= min_side and len(data) >= 4000
    except Exception:
        return False


def queries_for(name: str) -> list:
    base = re.sub(r"[（(].*", "", name).strip() or name
    return [f"{base} 歌手", base, f"{base} singer"]


def process(aid: int, name: str):
    for q in queries_for(name):
        for u in bing_image_urls(q, 12):
            try:
                r = requests.get(u, headers=UA, timeout=15)
                if r.status_code != 200:
                    continue
                data = r.content
                if validate_image(data):
                    minio_client.put_object(BUCKET, f"artists/{aid}.jpg",
                                            io.BytesIO(data), length=len(data),
                                            content_type="image/jpeg")
                    return {"id": aid, "name": name, "status": "ok",
                            "query": q, "bytes": len(data)}
            except Exception:
                continue
        time.sleep(0.8)
    return {"id": aid, "name": name, "status": "no_image"}


def main():
    with open(REPORT, encoding="utf-8") as f:
        report = json.load(f)
    failed = report["failed"]
    print(f"retrying {len(failed)} failed artists...", flush=True)
    results = []
    for i, item in enumerate(failed, 1):
        res = process(item["id"], item["name"])
        results.append(res)
        print(f"[{i}/{len(failed)}] {res}", flush=True)
        time.sleep(0.6)

    ok = [r for r in results if r["status"] == "ok"]
    with open(SQL_OUT, "w", encoding="utf-8") as f:
        f.write("USE vibe_music;\n")
        for r in sorted(ok, key=lambda x: x["id"]):
            f.write(f"UPDATE tb_artist SET avatar='http://localhost:9095/vibe-music-data/artists/{r['id']}.jpg' WHERE id={r['id']};\n")
    with open(REPORT2, "w", encoding="utf-8") as f:
        json.dump({"ok": sorted(ok, key=lambda x: x["id"]),
                   "failed": sorted([r for r in results if r["status"] != "ok"],
                                    key=lambda x: x["id"])},
                  f, ensure_ascii=False, indent=2)
    print(f"DONE ok={len(ok)} failed={len(results)-len(ok)}", flush=True)
    for r in results:
        if r["status"] != "ok":
            print(f"  STILL FAILED: id={r['id']} {r['name']}", flush=True)


if __name__ == "__main__":
    main()
