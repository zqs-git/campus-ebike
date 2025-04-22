<template>
  <div class="charging-page">
    <el-row>
      <el-col :span="24">
        <el-card :body-style="{ padding: '20px' }">
          <h3>充电桩状态</h3>

          <el-select
            v-model="selectedLocation"
            placeholder="选择充电区"
            :loading="charging.loadingLocations"
            @change="onLocationChange"
          >
            <el-option
              v-for="loc in charging.locations"
              :key="loc.id"
              :label="loc.name"
              :value="loc.id"
            />
          </el-select>

          <el-table
            :data="charging.piles"
            style="width: 100%"
            v-loading="charging.loadingPiles"
          >
            <el-table-column prop="name" label="充电桩名称" />
            <el-table-column prop="connector" label="接口类型" />
            <el-table-column prop="status" label="状态" />

            <el-table-column label="操作" width="260px">
              <template #default="{ row }">
                <el-button
                  size="small"
                  type="primary"
                  @click="reservePile(row.id)"
                  :disabled="row.status !== 'available'"
                >预约</el-button>
                <el-button
                  size="small"
                  type="success"
                  @click="startCharging(row.id)"
                  :disabled="row.status !== 'reserved'"
                >开始充电</el-button>
                <el-button
                  size="small"
                  type="danger"
                  @click="stopCharging(row.id)"
                  :disabled="row.status !== 'charging'"
                >停止充电</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted,computed} from 'vue'
import { ElMessage } from 'element-plus'
import { useChargingStore } from '@/store/charging'
import { useAuthStore } from "../store/auth";

// 引入 Store
const charging = useChargingStore()

// 本地选中充电区
const selectedLocation = ref(null)
const authStore = useAuthStore();


const user = computed(() => authStore.user);

// 页面初始化
onMounted(async () => {
  try {
    await charging.fetchLocations()
  } catch {
    ElMessage.error('加载充电区失败')
  }
})

// 充电区切换
const onLocationChange = async (locId) => {
  selectedLocation.value = locId
  try {
    await charging.fetchPiles(locId)
  } catch {
    ElMessage.error('加载充电桩失败')
  }
}

// 发起预约
const reservePile = async (pileId) => {
  try {
    // 假设从用户信息模块里拿到真实 userId
    const userId = user.value.user_id
    console.log('userId', userId)
    await charging.reservePile(userId, pileId)
    ElMessage.success('预约成功')
  } catch {
    ElMessage.error('预约失败')
  }
}

// 开始充电
const startCharging = async (sessionId) => {
  try {
    console.log('sessionId', sessionId)
    await charging.startCharging(sessionId)
    ElMessage.success('充电开始')
  } catch {
    ElMessage.error('开始充电失败')
  }
}

// 停止充电
const stopCharging = async (sessionId) => {
  try {
    await charging.stopCharging(sessionId)
    ElMessage.success('充电结束')
  } catch {
    ElMessage.error('停止充电失败')
  }
}
</script>

<style scoped>
.charging-page { padding: 20px; }
.el-card { margin-top: 20px; }
.el-select { margin-bottom: 20px; width: 300px; }
</style>
