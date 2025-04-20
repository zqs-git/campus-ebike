import { defineStore } from 'pinia'
import { getAreas, createArea, updateArea, deleteArea } from '../api/areas'

export const useAreaStore = defineStore('areaStore', {
  state: () => ({
    list: []  // 存储从后端加载的区域对象数组
  }),
  
  actions: {
    /**
     * 从后端加载所有区域，赋值到 state.list
     */
    async loadAreasFromServer() {
      try {
        const { data } = await getAreas()
        // 在这里处理数据，以确保包含 path 和 center 字段
        this.list = data.map(area => ({
          id: area.id,
          name: area.name,
          type: area.type,
          path: area.path || [],  // 如果没有路径数据，默认空数组
          center: area.center || { lng: 0, lat: 0 },  // 如果没有中心点数据，默认值
        }))
      } catch (err) {
        console.error('加载区域失败', err)
      }
    },

    /**
     * 提交新区域到后端，并将返回的 id 添加到本地列表
     * @param {{ name: string, type: string, path: Array<[number, number]>, center: { lng: number, lat: number } }} area
     */
    async saveAreaToServer(area) {
      try {
        const response = await createArea(area)
        const id = response.data.id
        // 将新的区域添加到列表中
        this.list.push({ ...area, id })
      } catch (err) {
        console.error('保存区域失败', err)
      }
    },

    /**
     * 更新区域信息
     * @param {number} areaId
     * @param {object} updatedData
     */
    async updateAreaInServer(areaId, updatedData) {
      try {
        await updateArea(areaId, updatedData)
        const index = this.list.findIndex(area => area.id === areaId)
        if (index !== -1) {
          this.list[index] = { ...this.list[index], ...updatedData }  // 更新本地数据
        }
      } catch (err) {
        console.error('更新区域失败', err)
      }
    },

    /**
     * 删除区域
     * @param {number} areaId
     */
    async deleteAreaFromServer(areaId) {
      try {
        await deleteArea(areaId)
        this.list = this.list.filter(area => area.id !== areaId)  // 从本地数据中移除
      } catch (err) {
        console.error('删除区域失败', err)
      }
    }
  }
})
