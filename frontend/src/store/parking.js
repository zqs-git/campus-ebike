import { defineStore } from 'pinia';
import { 
  getParkingLots, 
  addParkingLot, 
  parkIn, 
  parkOut, 
  getCurrentRecord,
  updateParkingLot,
  deleteParkingLot,
  getParkingRecords
} from '@/api/parking';

export const useParkingStore = defineStore('parking', {
  state: () => ({
    parkingLots: [],         // 停车场列表
    currentRecord: null,     // 当前停车记录
    message: '',             // 系统消息
    isAdmin: false,          // 管理员状态

    // 📌 添加分页相关状态
    parkingRecords: [],      // 停车记录列表
    totalRecords: 0,         // 总停车记录数
    currentPage: 1,          // 当前页码
    pageSize: 10,            // 每页显示的数量
    loadingRecords: false    // 加载状态
  }),

  actions: {
    // 获取停车场列表
    async fetchParkingLots() {
      try {
        this.parkingLots = await getParkingLots();
      } catch (error) {
        this.message = error.message;
        throw error;
      }
    },

    // 获取当前停车记录
    async fetchCurrentRecord() {
      try {
        this.currentRecord = await getCurrentRecord();
      } catch (error) {
        this.currentRecord = null;
        if (error.message !== '未找到停车记录') {
          this.message = error.message;
        }
      }
    },

    // 创建停车场（管理员）
    async createParkingLot(lotData) {
      try {
        await addParkingLot(lotData);
        this.message = '停车场创建成功';
        await this.fetchParkingLots();
      } catch (error) {
        this.message = error.message;
        throw error;
      }
    },

    async updateParkingLot(lotId, data) {
      try {
        await updateParkingLot(lotId, data);
        this.message = "停车场信息更新成功";
        await this.fetchParkingLots();
      } catch (error) {
        this.message = error.message;
        throw error;
      }
    },
    
    async deleteParkingLot(lotId) {
      try {
        await deleteParkingLot(lotId);
        this.message = "停车场删除成功";
        await this.fetchParkingLots();
      } catch (error) {
        this.message = error.message;
        throw error;
      }
    },

    // 📌 修改 `fetchParkingRecords` 方法，增加分页
    async fetchParkingRecords(keyword = "", page = 1, pageSize = 10) {
      this.loadingRecords = true;
      try {
        const response = await getParkingRecords({ keyword, page, pageSize });
        
        this.parkingRecords = response.records; // 停车记录
        this.totalRecords = response.total;    // 记录总数
        this.currentPage = page;
        this.pageSize = pageSize;
      } catch (error) {
        this.message = error.message;
        throw error;
      } finally {
        this.loadingRecords = false;
      }
    },

    // 停车入库
    async parkInVehicle(parkingdata) {
      try {
        console.log('UserID:', parkingdata.user_id);
        this.currentRecord = await parkIn(parkingdata);
        this.message = '停车成功';
      } catch (error) {
        this.message = error.message;
        throw error;
      }
    },

    // 停车出库
    async parkOutVehicle(recordId) {
      try {
        await parkOut(recordId);
        this.currentRecord = null;
        this.message = '取车成功';
      } catch (error) {
        this.message = error.message;
        throw error;
      }
    }
  },

  getters: {
    // 获取可用停车场 (可选)
    availableLots: (state) => {
      return state.parkingLots.filter(lot => lot.occupied < lot.capacity);
    }
  }
});
