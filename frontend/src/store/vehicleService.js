import { defineStore } from 'pinia';
import { ref } from 'vue';
import { getMyVehicle, bindVehicle, unbindVehicle, updateVehicle } from '../api/vehicleApi';

export const useVehicleStore = defineStore('vehicle', {
  state: () => ({
    vehicle: ref(null),  // 当前用户绑定的电动车
  }),

  actions: {
    async fetchMyVehicle() {
      try {
        const data = await getMyVehicle();
        if (data.code === 200) {
          this.vehicle = data.vehicle;
        } else {
          this.vehicle = null;
        }
      } catch (error) {
        console.error('获取电动车信息失败', error);
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
          this.vehicle = null;  // 清除绑定的电动车
        }
      } catch (error) {
        console.error('解绑电动车失败', error);
      }
    },

    async updateVehicleHandler(vehicleId, updates) {
      try {
        const response = await updateVehicle(vehicleId, updates);
        if (response.code === 200) {
          this.vehicle = response.vehicle;  // 更新电动车信息
        }
      } catch (error) {
        console.error('更新电动车信息失败', error);
      }
    },
  },
});
