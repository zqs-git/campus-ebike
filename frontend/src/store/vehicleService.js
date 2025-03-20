import { defineStore } from 'pinia';
import { ref } from 'vue';
import { getMyVehicle, bindVehicle, unbindVehicle, updateVehicle, getAllVehicles } from '../api/vehicleApi';

export const useVehicleStore = defineStore('vehicle', {
  state: () => ({
    vehicle: ref(null),      // 当前用户绑定的车辆
    allVehicles: ref([]),    // 所有车辆列表（管理员专用）
  }),

  actions: {

    
    async fetchMyVehicle() {
      try {
        const data = await getMyVehicle();
        console.log("获取车辆信息的原始响应:", data); // 添加此行
        if (data.code === 200) {
          this.vehicle = data.vehicle;
          console.log("存储的车辆信息:", this.vehicle);
        } else {
          this.vehicle = {};
        }
      } catch (error) {
        console.error('获取电动车信息失败', error);
        console.log("请求错误详情:", error.response?.data || error.message);
        this.vehicle = null; // 出错时清空车辆信息
      }
    },

    // 新增获取所有车辆的方法
    async fetchAllVehicles() {
      try {
        const data = await getAllVehicles();
        if (data.code === 200) {
          this.allVehicles = data.data; // 存储所有车辆数据
        } else {
          this.allVehicles = [];
          throw new Error(data.msg || '获取所有车辆失败');
        }
      } catch (error) {
        console.error('获取所有车辆失败:', error);
        // 处理 401/403 等错误（如权限不足）
        if (error.response?.status === 401) {
          alert('登录已过期，请重新登录');
          // 触发跳转登录逻辑
        } else if (error.response?.status === 403) {
          alert('无权限访问该接口');
        }
        this.allVehicles = []; // 清空数据
      }
    },

    async bindVehicleHandler(vehicleData) {
      console.log("🚀 发送的数据:", vehicleData); // 添加日志，检查数据是否完整
      try {
        const response = await bindVehicle(vehicleData);
        console.log("绑定返回数据:", response);
        if (response.code === 201) {
          this.vehicle = response.vehicle;  // 更新当前绑定的电动车
        }
      } catch (error) {
        console.error('绑定电动车失败', error);
      }
    },

    async unbindVehicleHandler(vehicleId) {
      try {
        const response = await unbindVehicle(vehicleId);
        if (response.code === 200) {
          this.vehicle = null;
        }
      } catch (error) {
        console.error('解绑电动车失败', error);
      }
    },

    async updateVehicleHandler(vehicleId, updates) {
      try {
        const response = await updateVehicle(vehicleId, updates);
        if (response.code === 200 && response.vehicle) {
          this.vehicle = response.vehicle;  // 更新电动车信息
        }
      } catch (error) {
        console.error('更新电动车信息失败', error);
      }
    },
  },
});
