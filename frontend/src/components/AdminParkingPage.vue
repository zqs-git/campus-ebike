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
      
      <el-tab-pane label="充电桩管理">
        <h2>功能待开发</h2>
      </el-tab-pane>
      <el-tab-pane label="违停管理">
        <h2>功能待开发</h2>
      </el-tab-pane>

      

      <!-- 停车操作模块
      <el-tab-pane label="停车操作" name="operations">
        <div class="module-section">
          <el-form :model="parkForm" label-width="100px" class="operation-form">
            <el-form-item label="停车场">
              <el-select v-model="parkForm.lot_id" placeholder="请选择">
                <el-option
                  v-for="lot in parkingStore.parkingLots"
                  :key="lot.id"
                  :label="lot.name"
                  :value="lot.id"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="车辆ID">
              <el-input v-model="parkForm.vehicle_id" placeholder="请输入车辆ID" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleParkIn">停车</el-button>
              <el-button type="warning" @click="handleParkOut">取车</el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-tab-pane> -->

      <!-- 停车记录模块 -->
      <!-- 停车记录模块 -->
      <el-tab-pane label="充电记录" name="records">
        <div class="module-section">
          <div class="section-header">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索车牌号"
              clearable
              class="search-input"
              @clear="resetAndFetchRecords"
              @input="resetAndFetchRecords"
            />
          </div>
          
          <el-table
            :key="tableKey"
            :data="parkingStore.parkingRecords"
            style="width: 100%;"
            height="400px"
            v-loading="parkingStore.loadingRecords"
            element-loading-text="加载中..."
          >
            <el-table-column prop="id" label="ID" width="60" />
            <el-table-column prop="plate_number" label="车牌号" />
            <el-table-column prop="1号充电桩" label="充电区" />
            <el-table-column prop="entry_time" label="充电时间" />
            <el-table-column prop="exit_time" label="离开时间" />
          </el-table>

          <!-- 分页组件 -->
          <el-pagination
            v-model:current-page="parkingStore.currentPage"
            :page-size="parkingStore.pageSize"
            layout="total, sizes, prev, pager, next"
            :total="parkingStore.totalRecords"
            @current-change="fetchRecords"
            @size-change="updatePageSize"
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
        <el-form-item label="名称">
          <el-input v-model="lotForm.name" placeholder="请输入停车场名称" />
        </el-form-item>
        <el-form-item label="容量">
          <el-input-number v-model="lotForm.capacity" :min="1" />
        </el-form-item>
        <el-form-item label="地点">
          <el-select v-model="lotForm.location_id" placeholder="请选择地点">
            <el-option
              v-for="loc in locationStore.locations"
              :key="loc.id"
              :label="loc.name"
              :value="loc.id"
            />
          </el-select>
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
            <el-option label="充电桩区域" value="parking" />
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
import { ref, onMounted,} from "vue";
import { ElMessage } from "element-plus";
import { useParkingStore } from "@/store/parking";
import { useLocationStore } from "@/store/location";

// 模块切换
const activeTab = ref("lots");
const tableKey = ref(0);


// 使用停车场相关 Store（直接使用对象，模板中访问其属性）
const parkingStore = useParkingStore();
const {
  fetchParkingLots,
  createParkingLot,
  updateParkingLot,
  deleteParkingLot,
  // parkInVehicle,
  // parkOutVehicle,
  fetchParkingRecords
} = parkingStore;

// 使用地点相关 Store
const locationStore = useLocationStore();
const { fetchLocations, addLocation, editLocation, removeLocation } = locationStore;

// 页面加载时初始化数据
onMounted(() => {
  fetchParkingLots();
  fetchLocations();
  fetchParkingRecords();

  console.log("地点数据:", locationStore.locations);
});

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

// ---------- 停车操作 ---------- //
// const parkForm = ref({
//   lot_id: "",
//   vehicle_id: ""
// });
const searchKeyword = ref("");

// const handleParkIn = async () => {
//   if (!parkForm.value.lot_id || !parkForm.value.vehicle_id) {
//     return ElMessage.error("请填写完整信息");
//   }
//   try {
//     await parkInVehicle(parkForm.value);
//     ElMessage.success("停车成功");
//     fetchParkingLots();
//   } catch (error) {
//     ElMessage.error(error.message || "停车失败");
//   }
// };

// const handleParkOut = async () => {
//   if (!parkForm.value.vehicle_id) {
//     return ElMessage.error("请输入车辆 ID");
//   }
//   try {
//     await parkOutVehicle(parkForm.value.vehicle_id);
//     ElMessage.success("取车成功");
//     fetchParkingLots();
//   } catch (error) {
//     ElMessage.error(error.message || "取车失败");
//   }
// };


// ---------- 停车记录 ---------- //


import { nextTick } from "vue";

const fetchRecords = async () => {
  try {
    parkingStore.loadingRecords = true;
    await parkingStore.fetchParkingRecords(searchKeyword.value, parkingStore.currentPage, parkingStore.pageSize);
    await nextTick();
    tableKey.value += 1; // 触发表格重新渲染
  } catch (error) {
    ElMessage.error("获取记录失败");
  } finally {
    parkingStore.loadingRecords = false;
  }
};

// **搜索时，重置分页**
const resetAndFetchRecords = () => {
  parkingStore.currentPage = 1; // **搜索时重置页码**
  fetchRecords();
};

// **修改分页大小**
const updatePageSize = (size) => {
  parkingStore.pageSize = size;
  fetchRecords();
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
.management-page {
  padding: 20px;
  background: #fefefe;
}

.page-header {
  margin-bottom: 20px;
}

.module-tabs {
  margin-bottom: 20px;
}

.module-section {
  padding: 20px;
  background: #fff;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.section-header {
  margin-bottom: 15px;
  text-align: right;
}

.search-input {
  margin-bottom: 15px;
}
</style>
