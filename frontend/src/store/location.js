import { defineStore } from 'pinia';
import { getLocations, addLocation, updateLocation, deleteLocation } from '@/api/location';

export const useLocationStore = defineStore('location', {
  state: () => ({
    locations: [],
    message: '',
  }),

  actions: {
    async fetchLocations() {
      try {
        const response = await getLocations();
        this.locations = response; // 直接赋值
      } catch (error) {
        console.error('获取地点失败:', error);
      }
    },

    async addLocation(locationData) {
      try {
        await addLocation(locationData); // 修正方法名
        this.fetchLocations();
        this.message = '地点创建成功';
      } catch (error) {
        console.error('创建地点失败:', error);
      }
    },

    async editLocation(id, locationData) {
      try {
        await updateLocation(id, locationData);
        this.fetchLocations();
        this.message = '地点更新成功';
      } catch (error) {
        console.error('更新地点失败:', error);
        this.message = "更新失败";
      }
    },

    async removeLocation(id) {
      try {
        await deleteLocation(id);
        this.fetchLocations();
        this.message = '地点删除成功';
      } catch (error) {
        console.error('删除地点失败:', error);
      }
    },
  },
});
