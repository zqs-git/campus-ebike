<template>
  <div class="violation-management-panel">
    <h3>模拟违规事件</h3>
    <el-form :model="simulationForm" label-width="120px">
      <!-- 车辆选择 -->
      <el-form-item label="车辆选择">
        <el-select
          v-model="simulationForm.license_plate"
          filterable
          placeholder="选择系统中的真实车牌"
          @change="onVehicleSelect"
        >
          <el-option
            v-for="v in realVehicles"
            :key="v.license_plate"
            :label="`${v.license_plate} (${v.owner_name || '未知用户'})`"
            :value="v.license_plate"
          />
        </el-select>
      </el-form-item>

      <!-- 用户ID -->
      <el-form-item label="用户ID">
        <el-input v-model="simulationForm.user_id" disabled />
      </el-form-item>

      <!-- 事件类型，可输入也可选 -->
      <el-form-item label="事件类型">
        <el-select
          v-model="simulationForm.event_type"
          filterable
          allow-create
          placeholder="请选择或输入事件类型"
          @change="onEventTypeChange"
        >
          <el-option
            v-for="rule in scoreStore.scoreRules"
            :key="rule.event_type"
            :label="rule.description"
            :value="rule.event_type"
          />
        </el-select>
      </el-form-item>

      <!-- 禁停区选择 -->
      <el-form-item
        v-if="simulationForm.event_type === 'forbidden_parking'"
        label="位置"
      >
        <el-select
          v-model="simulationForm.location"
          filterable
          placeholder="请选择禁停区"
        >
          <el-option
            v-for="zone in forbiddenZones"
            :key="zone.id"
            :label="zone.name"
            :value="zone.name"
          />
        </el-select>
      </el-form-item>

      <!-- 停车区选择 -->
      <el-form-item
        v-else-if="simulationForm.event_type === 'normal_parking'"
        label="位置"
      >
        <el-select
          v-model="simulationForm.location"
          filterable
          placeholder="请选择停车区"
        >
          <el-option
            v-for="zone in parkingZones"
            :key="zone.id"
            :label="zone.name"
            :value="zone.name"
          />
        </el-select>
      </el-form-item>

      <!-- 其他或自定义事件，自由输入位置 -->
      <el-form-item v-else label="位置">
        <el-input
          v-model="simulationForm.location"
          placeholder="请输入位置信息"
        />
      </el-form-item>

      <!-- 提交按钮 -->
      <el-button type="primary" @click="generateViolation">
        模拟生成事件
      </el-button>
    </el-form>

    <el-divider />

    <h3>批量模拟数据</h3>
    <el-form inline>
      <el-form-item label="生成数量">
        <el-input-number v-model="batchCount" :min="1" :max="50" />
      </el-form-item>
      <el-form-item label="只使用真实用户">
        <el-switch v-model="useOnlyRealUsers" />
      </el-form-item>
      <el-button type="success" @click="generateBatchData">
        批量生成测试数据
      </el-button>
    </el-form>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useScoreStore } from '@/store/score'
import { useVehicleStore } from '@/store/vehicleService'
import { useLocationStore } from '@/store/location'
import { ElMessage } from 'element-plus'

export default {
  name: 'ViolationManagementPanel',
  setup(_, { emit }) {
    const scoreStore    = useScoreStore()
    const vehicleStore  = useVehicleStore()
    const locationStore = useLocationStore()

    // --- 数据 & 表单 ---
    const realVehicles     = ref([])
    const useOnlyRealUsers = ref(true)
    const batchCount       = ref(5)

    const simulationForm = ref({
      user_id:       '',
      license_plate: '',
      event_type:    '',
      location:      ''
    })

    // --- 区域列表（从 locationStore 过滤） ---
    const forbiddenZones = computed(() =>
      locationStore.locations.filter(z => z.location_type === 'no-parking')
    )
    const parkingZones = computed(() =>
      locationStore.locations.filter(z => z.location_type === 'parking')
    )

    // --- 事件处理 ---
    const onVehicleSelect = plate => {
      const v = realVehicles.value.find(x => x.license_plate === plate)
      if (v) simulationForm.value.user_id = v.user_id
    }

    const onEventTypeChange = type => {
      if (type === 'forbidden_parking' && forbiddenZones.value.length) {
        simulationForm.value.location = forbiddenZones.value[0].name
      }
      else if (type === 'normal_parking' && parkingZones.value.length) {
        simulationForm.value.location = parkingZones.value[0].name
      }
      else {
        simulationForm.value.location = ''
      }
    }

    const generateViolation = async () => {
      try {
        await scoreStore.simulateViolation(simulationForm.value)
        ElMessage.success('模拟违规事件生成成功')
        emit('refresh-data')
      } catch {
        ElMessage.error('模拟违规生成失败')
      }
    }

    const generateBatchData = async () => {
      try {
        await scoreStore.simulateBatchViolations({
          count: batchCount.value,
          useOnlyRealUsers: useOnlyRealUsers.value
        })
        ElMessage.success(`成功生成 ${batchCount.value} 条模拟违规数据`)
        emit('refresh-data')
      } catch {
        ElMessage.error('批量模拟数据生成失败')
      }
    }

    // --- 初始加载 ---
    const fetchRealVehicles = async () => {
      try {
        await vehicleStore.fetchAllVehicles()
        realVehicles.value = vehicleStore.allVehicles.map(v => ({
          license_plate: v.plate_number || v.license_plate,
          user_id:       v.owner_id,
          owner_name:    v.owner_name
        }))
        if (realVehicles.value.length) {
          const first = realVehicles.value[0]
          simulationForm.value.license_plate = first.license_plate
          simulationForm.value.user_id       = first.user_id
        }
      } catch {
        ElMessage.error('获取车辆数据失败')
      }
    }

    onMounted(() => {
      // 加载车辆、积分规则、以及所有地点
      fetchRealVehicles()
      if (!scoreStore.scoreRules.length) {
        scoreStore.fetchRules()
      }
      locationStore.fetchLocations()
    })

    return {
      simulationForm,
      realVehicles,
      forbiddenZones,
      parkingZones,
      useOnlyRealUsers,
      batchCount,
      scoreStore,
      onVehicleSelect,
      onEventTypeChange,
      generateViolation,
      generateBatchData
    }
  }
}
</script>

<style scoped>
.violation-management-panel {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}
h3 {
  margin: 0 0 20px;
  color: #333;
  font-weight: 600;
}
.el-divider {
  margin: 30px 0;
}
.el-form-item {
  margin-bottom: 15px;
}
.el-button {
  margin-top: 10px;
}
</style>
