import { defineStore } from 'pinia'
import {
  fetchAreas,
  createArea,
  updateArea,
  deleteArea,
  fetchPilesByArea,
  createPile,
  updatePile,
  deletePile,
  fetchChargingLogs
} from '@/api/chargingAdmin'

export const useAdminChargingStore = defineStore('adminCharging', {
  state: () => ({
    locations: [],     // 原 areas 改名为 locations
    piles: [],
    logs: [],
    loadingAreas: false,
    loadingPiles: false,
    loadingLogs: false,
    error: null // 记录错误信息
  }),
  actions: {
    // 加载充电区
    async fetchLocations() {
      this.loadingAreas = true
      this.error = null
      try {
        const { data } = await fetchAreas()
        this.locations = data
      } catch (err) {
        console.error('加载充电区失败:', err)
        this.error = '加载充电区失败，请重试。'
      } finally {
        this.loadingAreas = false
      }
    },

    // 新增或编辑充电区（组件中调用 saveLocation）
    async saveLocation(location) {
      try {
        if (location.id) {
          await updateArea(location.id, location)
        } else {
          await createArea(location)
        }
        await this.loadAreas()
      } catch (err) {
        console.error('保存充电区失败:', err)
        this.error = '保存充电区失败，请重试。'
      }
    },

    // 删除充电区（组件中调用 deleteLocation）
    async deleteLocation(id) {
      try {
        await deleteArea(id)
        await this.loadAreas()
      } catch (err) {
        console.error('删除充电区失败:', err)
        this.error = '删除充电区失败，请重试。'
      }
    },

    // 获取指定充电区下的充电桩（组件中调用 fetchPiles）
    async fetchPiles(areaId) {
      this.loadingPiles = true
      this.error = null
      try {
        const { data } = await fetchPilesByArea(areaId)
        this.piles = data
      } catch (err) {
        console.error('加载充电桩失败:', err)
        this.error = '加载充电桩失败，请重试。'
      } finally {
        this.loadingPiles = false
      }
    },

    // 新增或编辑充电桩（组件中调用 savePile）
    async savePile(pile) {
      try {
        if (pile.id) {
          await updatePile(pile.id, pile)
        } else {
          await createPile(pile.location_id, pile)
        }
        // 保存后重新加载当前区域的桩列表
        await this.fetchPiles(pile.location_id)
      } catch (err) {
        console.error('保存充电桩失败:', err)
        this.error = '保存充电桩失败，请重试。'
      }
    },

    // 删除充电桩（组件中调用 deletePile）
    async deletePile(id) {
      try {
        await deletePile(id)
      } catch (err) {
        console.error('删除充电桩失败:', err)
        this.error = '删除充电桩失败，请重试。'
      }
    },

    // 加载充电日志
    async loadLogs() {
      this.loadingLogs = true
      this.error = null
      try {
        const { data } = await fetchChargingLogs()
        this.logs = data
      } catch (err) {
        console.error('加载充电日志失败:', err)
        this.error = '加载充电日志失败，请重试。'
      } finally {
        this.loadingLogs = false
      }
    }
  }
})
