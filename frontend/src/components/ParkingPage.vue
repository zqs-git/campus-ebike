<!-- src/components/StudentParkingPage.vue -->
<template>
  <div class="student-parking">
    <h2>校内停车场</h2>
    
    <!-- 搜索和排序功能（新增） -->
    <div class="search-sort-container">
      <input
        type="text"
        v-model="searchQuery"
        placeholder="搜索停车场..."
        class="search-input"
      />
      <button class="sort-button" @click="toggleSortByDistance">
        {{ sortByDistance ? '取消按距离排序' : '按离我距离排序' }}
      </button>
    </div>
    
    <!-- 消息提示 -->
    <div v-if="message" class="message-box" :class="{ success: isSuccess, error: !isSuccess }">
      {{ message }}
    </div>

    <!-- 停车场实时状态 -->
    <div class="parking-status">
      <!-- <h3>停车场实时状态</h3> -->
      <div class="status-grid">
        <!-- 修改：循环使用 filteredParkingLots（排序和搜索后得到的数据） -->
        <div v-for="lot in filteredParkingLots" :key="lot.id" class="parking-lot" @click="toggleLotDetails(lot.id)">
          <div class="lot-header">
            <span class="lot-name">{{ lot.name }}</span>
            <span class="lot-occupancy">
              {{ lot.occupied }}/{{ lot.capacity }}
            </span>
          </div>
          <div class="progress-bar">
            <div 
              class="progress" 
              :style="{ width: (lot.occupied / lot.capacity * 100) + '%' }"
              :class="{ 
                'low': (lot.occupied / lot.capacity) < 0.5,
                'medium': (lot.occupied / lot.capacity) >= 0.5 && (lot.occupied / lot.capacity) < 0.8,
                'high': (lot.occupied / lot.capacity) >= 0.8 
              }"
            ></div>
          </div>

          <!-- 添加"查看详情"按钮 -->
          <button class="view-details-btn" @click.stop="toggleLotDetails(lot.id)">
            {{ expandedLotId === lot.id ? "收起详情" : "查看详情" }}
          </button>
          
          <!-- 新增：导航按钮（暂不实现导航功能） -->
          <button class="navigate-btn" @click.stop="handleNavigate(lot)">
            导航
          </button>

          <!-- 展开显示停车场详情 -->
          <div v-if="expandedLotId === lot.id" class="lot-details">
            <h4>停车场详情</h4>
            <p>名称：{{ lot.name }}</p>
            <p>位置：{{ lot.location }}</p>
            <!-- <p>总车位：{{ lot.capacity }}</p> -->
            <!-- <p>已占用：{{ lot.occupied }}</p> -->
            <!-- <p>剩余车位：{{ lot.capacity - lot.occupied }}</p> -->
          </div>

        </div>
      </div>
    </div>

    <!-- 操作面板
    <div class="action-panel">
      <div class="park-action">
        <h3>停车操作</h3>
        <button class="park-button" @click="handleParkIn" :disabled="!!currentParkingRecord">
          <i class="el-icon-circle-plus-outline"></i>
          我要停车
        </button>
      </div>

      <div class="retrieve-action">
        <h3>取车操作</h3>
        <button 
          class="retrieve-button" 
          :disabled="!currentParkingRecord"
          @click="handleParkOut"
        >
          <i class="el-icon-circle-close"></i>
          我要取车
        </button>
      </div>
    </div> -->

    <!-- 停车记录 -->
    <div v-if="currentParkingRecord" class="parking-record">
      <h3>当前停车记录</h3>
      <div class="record-details">
        <p>停车场：{{ findLotName(currentParkingRecord.lot_id) }}</p>
        <p>入场时间：{{ formattedEntryTime }}</p>
        <p>已停时长：{{ calculateDuration }} 分钟</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useParkingStore } from '@/store/parking';
// import { useVehicleStore } from '@/store/vehicleService';

const parkingStore = useParkingStore();
// const vehicleStore = useVehicleStore();

const expandedLotId = ref(null);

const findLotName = (lotId) => {
  const lot = parkingLots.value.find(lot => lot.id === lotId);
  return lot ? lot.name : '未知停车场';
};

// 点击展开/折叠停车场详情
const toggleLotDetails = (lotId) => {
  expandedLotId.value = expandedLotId.value === lotId ? null : lotId;
};

// 实时数据获取
onMounted(async () => {
  await parkingStore.fetchParkingLots();
  console.log("获取到的 parkingLots 数据:", parkingLots.value); 
  await parkingStore.fetchCurrentRecord();
  console.log("当前停车记录:", currentParkingRecord.value);  
});

// 计算属性
const parkingLots = computed(() => parkingStore.parkingLots);
const currentParkingRecord = computed(() => parkingStore.currentRecord);
// const userVehicle = computed(() => vehicleStore.vehicle);

const message = ref('');
const isSuccess = ref(false);

// 新增：搜索和排序功能相关变量
const searchQuery = ref('');
const sortByDistance = ref(false);

// 计算过滤和排序后的停车场列表（假设每个停车场对象中有 distance 字段，若没有可自行补充）
const filteredParkingLots = computed(() => {
  let list = parkingLots.value;
  // 过滤：根据搜索框内容匹配停车场名称（不区分大小写）
  if (searchQuery.value.trim()) {
    const keyword = searchQuery.value.trim().toLowerCase();
    list = list.filter(lot => lot.name.toLowerCase().includes(keyword));
  }
  // 排序：如果开启了按距离排序，则对列表按 distance 属性排序（升序）
  if (sortByDistance.value) {
    list = list.slice().sort((a, b) => {
      // 如果没有 distance 字段，则保持原顺序
      return (a.distance || 0) - (b.distance || 0);
    });
  }
  return list;
});

const toggleSortByDistance = () => {
  sortByDistance.value = !sortByDistance.value;
};

// 新增：导航按钮点击事件（目前仅提示）
const handleNavigate = (lot) => {
  alert(`导航功能暂未实现，停车场：${lot.name}`);
};

const formatTime = (timestamp) => {
  if (!timestamp) return '无数据';
  
  const date = new Date(timestamp + 'Z'); // 强制按 UTC 解析
  if (isNaN(date.getTime())) return '无效时间';
  return date.toLocaleString();
};

const formattedEntryTime = computed(() => {
  return formatTime(currentParkingRecord.value?.entry_time);
});

const calculateDuration = computed(() => {
  if (!currentParkingRecord.value?.entry_time) return 0;
  const entryTime = new Date(currentParkingRecord.value.entry_time + 'Z');
  if (isNaN(entryTime.getTime())) return '无效时间';
  const now = new Date();
  return Math.floor((now.getTime() - entryTime.getTime()) / 60000); // 计算分钟数
});

// 输出调试信息
console.log("当前停车记录:", currentParkingRecord.value);
console.log("entry_time:", currentParkingRecord.value?.entry_time);
console.log("解析后的时间:", new Date(currentParkingRecord.value?.entry_time));

</script>

<style scoped>
.student-parking {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

/* 新增：搜索和排序部分样式 */
.search-sort-container {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  align-items: center;
}

.search-input {
  flex: 1;
  padding: 8px 10px;
  font-size: 16px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.sort-button {
  padding: 8px 12px;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.3s;
}

.sort-button:hover {
  background: #66b1ff;
}

.message-box {
  padding: 15px;
  margin: 20px 0;
  border-radius: 5px;
  text-align: center;
}

.success {
  background-color: #e1f3d8;
  color: #67c23a;
}

.error {
  background-color: #fde2e2;
  color: #f56c6c;
}

.parking-status {
  margin-bottom: 30px;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
}

.parking-lot {
  background: #fff;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
  cursor: pointer;
  transition: all 0.3s;
}

.parking-lot:hover {
  transform: scale(1.02);
  background: #f5f5f5;
}

.lot-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.lot-name {
  font-weight: bold;
}

.lot-details {
  margin-top: 10px;
  padding: 10px;
  background: #f9f9f9;
  border-radius: 5px;
  box-shadow: inset 0 0 5px rgba(0,0,0,0.1);
}

/* 过渡动画 */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter, .fade-leave-to {
  opacity: 0;
}

.view-details-btn, .navigate-btn {
  margin-top: 10px;
  padding: 5px 10px;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background 0.3s;
}

.view-details-btn:hover, .navigate-btn:hover {
  background: #66b1ff;
}

.progress-bar {
  height: 10px;
  background: #eee;
  border-radius: 5px;
  overflow: hidden;
}

.progress {
  height: 100%;
  transition: width 0.3s ease;
}

.low { background: #67c23a; }
.medium { background: #e6a23c; }
.high { background: #f56c6c; }

.action-panel {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
  margin: 30px 0;
}

.park-button, .retrieve-button {
  width: 100%;
  padding: 15px;
  border: none;
  border-radius: 5px;
  font-size: 16px;
  cursor: pointer;
  transition: transform 0.2s;
}

.park-button {
  background: #67c23a;
  color: white;
}

.park-button:disabled {
  background: #c0c4cc !important;
  cursor: not-allowed;
  opacity: 0.7;
}

.retrieve-button {
  background: #409eff;
  color: white;
}

.retrieve-button:disabled {
  background: #c0c4cc;
  cursor: not-allowed;
}

button:hover:not(:disabled) {
  transform: translateY(-2px);
}

.parking-record {
  background: #f8f8f8;
  padding: 20px;
  border-radius: 8px;
}
</style>
