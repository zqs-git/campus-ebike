<template>
  <div class="management-page">
    <!-- 顶部标题 -->
    <!-- <h3>校园电瓶车停车场管理后台</h3> -->
    <!-- <el-page-header content="校园电瓶车停车场管理后台" :icon="null" class="page-header" /> -->

    <!-- 模块切换 -->
    <el-tabs v-model="activeTab" type="border-card" class="module-tabs">
      <!-- 停车场管理模块 -->
      <el-tab-pane label="停车场管理" name="lots">
        <div class="module-section">
          <div class="section-header">
            <el-button type="primary" @click="openAddLotDialog">添加停车场</el-button>
          </div>
          <el-table
            :key="tableKey"
            :data="parkingStore.parkingLots"
            style="width: 100%;"
            height="300px"
            v-loading="parkingStore.loadingLots"
            element-loading-text="加载中..."
          >
            <el-table-column prop="id" label="ID" width="60" />
            <el-table-column prop="name" label="名称" />
            <el-table-column prop="location" label="地点" />
            <!-- <el-table-column prop="capacity" label="总车位" width="100" /> -->
            <!-- <el-table-column prop="occupied" label="已占用" width="100" /> -->
            <el-table-column label="操作" width="200">
              <template #default="{ row }">
                <el-button size="small" @click="openEditLotDialog(row)">编辑</el-button>
                <el-button size="small" type="danger" @click="handleDeleteLot(row.id)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>
      
      <el-tab-pane label="充电桩管理" name="charging">
        <ChargingAdmin/>
      </el-tab-pane>

      <el-tab-pane label="违停管理" name="violations">
        <h2>功能待开发</h2>
      </el-tab-pane>

      <!-- 充电记录模块 - 增强版 -->
      <el-tab-pane label="充电记录" name="records">
        <div class="module-section">
          <!-- 筛选区 -->
          <div class="filter-section">
            <el-form :inline="true" :model="chargingFilter" class="filter-form">
              <el-form-item label="用户ID">
                <el-input v-model="chargingFilter.user_id" placeholder="输入用户ID" clearable />
              </el-form-item>
              <el-form-item label="充电区">
                <el-select v-model="chargingFilter.location_id" placeholder="选择充电区" clearable @change="onZoneChange">
                  <el-option 
                    v-for="loc in chargingZones"
                    :key="loc.id"
                    :label="loc.name"
                    :value="loc.name" />
                </el-select>
                <el-tag v-if="chargingFilter.location_id" class="selected-tag">
                  已选：{{ chargingFilter.location_id }}
                </el-tag>
              </el-form-item>
              <el-form-item label="日期范围">
                <el-date-picker
                  v-model="chargingFilter.dateRange"
                  type="daterange"
                  range-separator="至"
                  start-placeholder="开始日期"
                  end-placeholder="结束日期"
                  value-format="YYYY-MM-DD"
                />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="fetchChargingRecords">查询</el-button>
                <el-button @click="resetChargingFilter">重置</el-button>
              </el-form-item>
            </el-form>
          </div>

          <!-- 数据表格 -->
          <el-table
            :key="tableKey"
            :data="filteredChargingLogs"
            class="log-table"
            v-loading="adminChargingStore.loadingLogs"
            element-loading-text="加载中..."
          >
            <el-table-column prop="id" label="ID" width="60" />
            <el-table-column prop="user_id" label="用户ID" width="80" />
            <el-table-column label="用户名" width="100">
              <template #default="{ row }">
                {{ row.user?.name || row.user_name || '未知' }}
              </template>
            </el-table-column>
            <el-table-column prop="vehicle_id" label="车辆ID" width="80" />
            <el-table-column label="充电区" width="120">
              <template #default="{ row }">
                {{ row.charging_zone || getLocationName(row.location_id) || '未知' }}
              </template>
            </el-table-column>
            <el-table-column label="充电桩" width="120">
              <template #default="{ row }">
                {{ row.pile_name || '未知' }}
              </template>
            </el-table-column>
            <el-table-column prop="start_time" label="开始时间" width="160" />
            <el-table-column prop="end_time" label="结束时间" width="160" />
            <el-table-column prop="energy_kwh" label="充电量(kWh)" width="100" />
            <el-table-column prop="fee_amount" label="费用(元)" width="100" />
          </el-table>

          <!-- 分页 -->
          <el-pagination
            v-model:current-page="chargingPage.current"
            :page-size="chargingPage.size"
            :total="allFilteredChargingLogs.length"
            layout="total, sizes, prev, pager, next"
            @current-change="handleChargingPageChange"
            @size-change="handleChargingSizeChange"
            class="pagination-container"
          />
        </div>
      </el-tab-pane>

      <!-- 地点管理模块 -->
      <el-tab-pane label="地点管理" name="locations">
        <div class="module-section">
          <div class="section-header">
            <el-button type="primary" @click="openAddLocationDialog">添加地点</el-button>
          </div>
          <el-table
            :key="tableKey"
            :data="locationStore.locations"
            style="width: 100%;"
            height="200px"
            v-loading="locationStore.loadingLocations"
            element-loading-text="加载中..."
          >
            <el-table-column prop="id" label="ID" width="60" />
            <el-table-column prop="name" label="名称" />
            <el-table-column prop="latitude" label="纬度" width="120" />
            <el-table-column prop="longitude" label="经度" width="120" />
            <el-table-column prop="location_type" label="类型" width="100" />
            <el-table-column label="操作" width="200">
              <template #default="{ row }">
                <el-button size="small" @click="openEditLocationDialog(row)">编辑</el-button>
                <el-button size="small" type="danger" @click="handleDeleteLocation(row.id)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 停车场添加/编辑弹窗 -->
    <el-dialog
      title="停车场信息"
      v-model="lotDialogVisible"
      width="500px"
      :before-close="handleLotDialogClose"
    >
    <el-form :model="lotForm" label-width="100px">
      <el-form-item label="地点">
        <el-select v-model="lotForm.location_id" placeholder="请选择地点" @change="autoFillLotName">
          <el-option
            v-for="loc in locationStore.locations"
            :key="loc.id"
            :label="loc.name"
            :value="loc.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="名称">
        <el-input v-model="lotForm.name" placeholder="请输入停车场名称" />
      </el-form-item>
      <el-form-item label="容量">
        <el-input-number v-model="lotForm.capacity" :min="1" />
      </el-form-item>
    </el-form>
      <template #footer>
        <el-button @click="handleLotDialogClose">取消</el-button>
        <el-button type="primary" @click="submitLotForm">确定</el-button>
      </template>
    </el-dialog>

    <!-- 地点添加/编辑弹窗 -->
    <el-dialog
      title="地点信息"
      v-model="locationDialogVisible"
      width="500px"
      :before-close="handleLocationDialogClose"
    >
      <el-form :model="locationForm" label-width="100px">
        <el-form-item label="名称">
          <el-input v-model="locationForm.name" placeholder="请输入地点名称" />
        </el-form-item>
        <el-form-item label="纬度">
          <el-input v-model="locationForm.latitude" placeholder="请输入纬度" />
        </el-form-item>
        <el-form-item label="经度">
          <el-input v-model="locationForm.longitude" placeholder="请输入经度" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="locationForm.location_type" placeholder="请选择类型">
            <el-option label="教学楼" value="building" />
            <el-option label="停车场" value="parking" />
            <el-option label="充电桩区域" value="charging" />
            <el-option label="宿舍" value="dormitory" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input type="textarea" v-model="locationForm.description" placeholder="请输入描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="handleLocationDialogClose">取消</el-button>
        <el-button type="primary" @click="submitLocationForm">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, watch,  computed,onBeforeUnmount } from "vue";
import {
  ElMessage,
  ElTabs,
  ElTabPane,
  ElButton,
  ElTable,
  ElTableColumn,
  ElDialog,
  ElForm,
  ElFormItem,
  ElInput,
  ElInputNumber,
  ElSelect,
  ElOption,
  ElPagination,
  ElDatePicker
} from 'element-plus'
import { useParkingStore } from "@/store/parking";
import { useLocationStore } from "@/store/location";
import { useAdminChargingStore } from "@/store/chargingAdmin";
import ChargingAdmin from "@/components/ChargingAdmin.vue";
console.log('ChargingAdmin =', ChargingAdmin)

const activeTab = ref("lots");
const tableKey = ref(0);

// 使用停车场相关 Store（直接使用对象，模板中访问其属性）
const parkingStore = useParkingStore();
const {
  fetchParkingLots,
  createParkingLot,
  updateParkingLot,
  deleteParkingLot,
} = parkingStore;

// 使用地点相关 Store
const locationStore = useLocationStore();
const { fetchLocations, addLocation, editLocation, removeLocation } = locationStore;

// 使用充电管理相关 Store
const adminChargingStore = useAdminChargingStore();

function handleResizeObserverError(event) {
  const msg = event.message || '';
  if (msg.includes('ResizeObserver loop completed with undelivered notifications')) {
    event.stopImmediatePropagation();
  }
}

// 页面加载时初始化数据
onMounted(() => {
  fetchParkingLots();
  fetchLocations();
  
  console.log("地点数据:", locationStore.locations);
});

onMounted(() => {
  window.addEventListener('error', handleResizeObserverError);
});
onBeforeUnmount(() => {
  window.removeEventListener('error', handleResizeObserverError);
});

// 当切换到充电记录标签页时自动加载数据
watch(() => activeTab.value, (newTab) => {
  if (newTab === 'records') {
    fetchChargingRecords();
  }
});

// 获取充电区名称的辅助函数
const getLocationName = (locationId) => {
  if (!locationId) return '未知';
  const location = locationStore.locations.find(loc => loc.id === locationId);
  return location ? location.name : '未知';
};

// ---------- 停车场管理 ---------- //
const lotDialogVisible = ref(false);
const lotForm = ref({
  id: null,
  name: "",
  capacity: 1,
  location_id: ""
});
const isEditingLot = ref(false);

const openAddLotDialog = () => {
  isEditingLot.value = false;
  lotForm.value = { id: null, name: "", capacity: 1, location_id: "" };
  lotDialogVisible.value = true;
};

const openEditLotDialog = (lot) => {
  isEditingLot.value = true;
  // 若后端返回数据中未包含 location_id 则设为空字符串
  lotForm.value = { ...lot, location_id: lot.location_id || "" };
  lotDialogVisible.value = true;
};

const handleLotDialogClose = () => {
  lotDialogVisible.value = false;
};

const submitLotForm = async () => {
  if (!lotForm.value.name || !lotForm.value.capacity || !lotForm.value.location_id) {
    return ElMessage.error("请填写完整信息");
  }
  console.log("提交地点表单", lotForm.value); // 打印提交的数据

  try {
    if (isEditingLot.value) {
      await updateParkingLot(lotForm.value.id, lotForm.value);
      ElMessage.success("停车场更新成功");
    } else {
      await createParkingLot(lotForm.value);
      ElMessage.success("停车场创建成功");
    }
    fetchParkingLots();
    lotDialogVisible.value = false;
  } catch (error) {
    ElMessage.error(error.message || "操作失败");
  }
};

const handleDeleteLot = async (id) => {
  try {
    await deleteParkingLot(id);
    ElMessage.success("停车场删除成功");
    fetchParkingLots();
  } catch (error) {
    ElMessage.error(error.message || "删除失败");
  }
};

// 自动填充停车场名称
const autoFillLotName = () => {
  const selectedLocation = locationStore.locations.find(loc => loc.id === lotForm.value.location_id);
  if (selectedLocation) {
    lotForm.value.name = selectedLocation.name; // 根据选中的地点填充停车场名称
  }
};

// ---------- 充电记录 - 增强版 ---------- //
// 充电记录筛选条件
const chargingFilter = ref({
  user_id: '',
  location_id: '',
  dateRange: [],
  status: ''
});

// 充电记录分页
const chargingPage = ref({
  current: 1,
  size: 10,
  total: 0
});

// 可选充电区列表
const chargingZones = computed(() =>
  locationStore.locations.filter(l => l.location_type === "charging")
);

// 全量过滤后的记录（分页前）
const allFilteredChargingLogs = computed(() => {
  let logs = adminChargingStore.logs || [];

  // 用户ID 过滤
  if (chargingFilter.value.user_id) {
    logs = logs.filter(l =>
      l.user_id?.toString().includes(chargingFilter.value.user_id)
    );
  }
  // 充电区 过滤
  if (chargingFilter.value.location_id) {
    logs = logs.filter(
      l => (l.charging_zone || "") === chargingFilter.value.location_id
    );
  }
  // 日期范围 过滤
  const [start, end] = chargingFilter.value.dateRange;
  if (start && end) {
    const s = new Date(start);
    const e = new Date(end);
    e.setHours(23,59,59);
    logs = logs.filter(l => {
      const t = new Date(l.start_time);
      return t >= s && t <= e;
    });
  }
  return logs;
});



// 分页后展示
const filteredChargingLogs = computed(() => {
  const start = (chargingPage.value.current - 1) * chargingPage.value.size;
  return allFilteredChargingLogs.value.slice(
    start,
    start + chargingPage.value.size
  );
});



// 重置筛选条件
const resetChargingFilter = () => {
  chargingFilter.value = { user_id: "", location_id: "", dateRange: [] };
  chargingPage.value.current = 1;
  fetchChargingRecords();
};

// 查询、重置、分页回调
const fetchChargingRecords = async () => {
  adminChargingStore.loadingLogs = true;
  try {
    await adminChargingStore.loadLogs();
    chargingPage.value.current = 1;
    tableKey.value++;
  } finally {
    adminChargingStore.loadingLogs = false;
  }
};

// 处理分页变化
const handleChargingPageChange = (page) => {
  chargingPage.value.current = page;
  // 无需重新加载数据，因为使用的是计算属性进行客户端分页
};

// 处理每页显示数量变化
const handleChargingSizeChange = (size) => {
  chargingPage.value.size = size;
  chargingPage.value.current = 1; // 重置到第一页
  // 无需重新加载数据，因为使用的是计算属性进行客户端分页
};

// ---------- 地点管理 ---------- //
const locationDialogVisible = ref(false);
const locationForm = ref({
  id: null,
  name: "",
  latitude: "",
  longitude: "",
  location_type: "building",
  description: ""
});
const isEditingLocation = ref(false);

const openAddLocationDialog = () => {
  isEditingLocation.value = false;
  locationForm.value = { id: null, name: "", latitude: "", longitude: "", location_type: "building", description: "" };
  locationDialogVisible.value = true;
};

const openEditLocationDialog = (loc) => {
  isEditingLocation.value = true;
  locationForm.value = { ...loc };
  locationDialogVisible.value = true;
};

const handleLocationDialogClose = () => {
  locationDialogVisible.value = false;
};

const submitLocationForm = async () => {
  if (!locationForm.value.name || !locationForm.value.latitude || !locationForm.value.longitude) {
    return ElMessage.error("请填写完整信息");
  }
  try {
    if (isEditingLocation.value) {
      await editLocation(locationForm.value.id, locationForm.value);
      ElMessage.success("地点更新成功");
    } else {
      await addLocation(locationForm.value);
      ElMessage.success("地点创建成功");
    }
    fetchLocations();
    locationDialogVisible.value = false;
  } catch (error) {
    ElMessage.error(error.message || "操作失败");
  }
};

const handleDeleteLocation = async (id) => {
  try {
    await removeLocation(id);
    ElMessage.success("地点删除成功");
    fetchLocations();
  } catch (error) {
    ElMessage.error(error.message || "删除失败");
  }
};
</script>

<style scoped>
.management-page { padding: 24px; background-color: #f5f7fa; }
.module-tabs { margin-bottom: 20px; }
.module-section { padding: 24px; background: #fff; border-radius: 8px; box-shadow: 0 2px 12px rgba(0,0,0,0.05); }
.filter-section { margin-bottom: 20px; padding: 16px; background: #fafafa; border-left: 4px solid #409eff; border-radius: 4px; }
.filter-form .el-form-item { margin-right: 20px; margin-bottom: 12px; }
.selected-tag { margin-left: 8px; line-height: 32px; }
.log-table { width: 100%; max-height: 400px; overflow: auto; }
.pagination-container { margin-top: 20px; text-align: right; }
</style>
