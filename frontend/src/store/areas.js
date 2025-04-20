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
        this.list = data.map(area => ({
          id: area.id,
          name: area.name,
          type: area.type,
          path: area.path || [],
          // 重点：把后台给的经纬度字段映射出来
          latitude: area.latitude ?? area.center?.lat ?? (area.path?.[0]?.[1] || 0),
          longitude: area.longitude ?? area.center?.lng ?? (area.path?.[0]?.[0] || 0),
          // 如果你也需要中心点，保留它
          center: area.center || { lng: 0, lat: 0 },
          description: area.description || ''
        }))
      } catch (err) {
        console.error('加载区域失败', err)
      }
    },
    

    /**
     * @param {{ name: string, type: string, path: Array<[number, number]>, center: { lng: number, lat: number }, description?: string }} area
     */

    async saveAreaToServer(area) {
      try {
        const response = await createArea(area)
        const id = response.data.id
        const newArea = { ...area, id }
        this.list.push(newArea)
        return newArea // ✅ 添加这一行，返回完整对象
      } catch (err) {
        console.error('保存区域失败', err)
        throw err // ✅ 建议抛出错误，让调用者可以 catch
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
