import { defineStore } from 'pinia'
import piniaPersistConfig from '@/stores/helper/persist'
import { ThemeState } from '@/stores/interface'
/**
 * 主题设置
 */
export const themeStore = defineStore({
  id: 'themeStore',
  state: (): ThemeState => ({
    isDark: false,
    primary: '#10b981',
  }),
  actions: {
    setDark(isDark: string | number | boolean) {
      this.isDark = isDark
    },
    setPrimary(primary: string) {
      this.primary = primary
    },
  },
  persist: piniaPersistConfig('ThemeStore'),
})
