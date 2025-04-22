<template>
  <div class="admin-charging-manage">
    <el-card>
      <h2>充电区管理</h2>
      <div class="controls">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索充电区"
          :style="{ width: '300px' }"
          @input="onSearch"
        />
        <el-button type="primary" @click="openLocationDialog(null)">
          新增充电区
        </el-button>
      </div>

      <!-- 直接用 loadingAreas 布尔 -->
      <el-table :data="filteredLocations" v-loading="loadingAreas">
        <el-table-column prop="name" label="充电区名称" />
        <el-table-column label="操作">
          <template #default="{ row }">
            <el-button size="small" @click="openLocationDialog(row)">
              编辑
            </el-button>
            <el-button
              size="small"
              type="danger"
              @click="deleteLocation(row.id)"
            >
              删除
            </el-button>
            <el-button size="small" @click="selectLocation(row.id)">
              查看充电桩
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogs.location" title="充电区信息">
      <el-form :model="locationForm">
        <el-form-item label="名称">
          <el-input v-model="locationForm.name" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogs.location = false">取消</el-button>
        <el-button type="primary" @click="saveLocation">保存</el-button>
      </template>
    </el-dialog>

    <!-- 只有选了 location 才展示下半部分 -->
    <el-card v-if="selectedLocation">
      <h3>充电桩管理</h3>
      <div class="controls">
        <el-button type="primary" @click="openPileDialog(null)">
          新增充电桩
        </el-button>
      </div>

      <!-- 直接用 loadingPiles 布尔 -->
      <el-table :data="piles" v-loading="loadingPiles">
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="connector" label="接口类型" />
        <el-table-column prop="power_kw" label="功率 (kW)" />
        <el-table-column prop="fee_rate" label="费率 (元/度)" />
        <el-table-column prop="status" label="状态" />
        <el-table-column label="操作">
          <template #default="{ row }">
            <el-button size="small" @click="openPileDialog(row)">
              编辑
            </el-button>
            <el-button
              size="small"
              type="danger"
              @click="deletePile(row.id)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogs.pile" title="充电桩信息">
      <el-form :model="pileForm">
        <el-form-item label="名称">
          <el-input v-model="pileForm.name" />
        </el-form-item>
        <el-form-item label="接口类型">
          <el-input v-model="pileForm.connector" />
        </el-form-item>
        <el-form-item label="功率">
          <el-input-number v-model="pileForm.power_kw" :min="0" />
        </el-form-item>
        <el-form-item label="费率">
          <el-input-number v-model="pileForm.fee_rate" :min="0" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="pileForm.status">
            <el-option
              v-for="s in statuses"
              :key="s"
              :label="s"
              :value="s"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogs.pile = false">取消</el-button>
        <el-button type="primary" @click="savePile">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
// —— ① imports 放最前 ——  
import { ref, computed, onMounted, watch } from 'vue'
import {
  ElMessage,
  ElCard,
  ElInput,
  ElButton,
  ElTable,
  ElTableColumn,
  ElDialog,
  ElForm,
  ElFormItem,
  ElInputNumber,
  ElSelect,
  ElOption
} from 'element-plus'
import { useAdminChargingStore } from '@/store/chargingAdmin'

// —— ② 初始化 store —— 
const store = useAdminChargingStore()

// —— ③ 响应式数据 —— 
const searchKeyword     = ref('')
const selectedLocation  = ref(null)
const dialogs           = ref({ location: false, pile: false })
const locationForm      = ref({ name: '' })
const pileForm          = ref({
  name: '',
  connector: '',
  power_kw: 0,
  fee_rate: 0,
  status: 'available'
})
const statuses          = ['available','reserved','charging','finished','offline']

// —— ④ 计算属性 —— 
const loadingAreas      = computed(() => store.loadingAreas)
const loadingPiles      = computed(() => store.loadingPiles)
const locations         = computed(() => store.locations)
const piles             = computed(() => store.piles)
const filteredLocations = computed(() =>
  locations.value.filter(loc => loc.name.includes(searchKeyword.value))
)

// —— ⑤ 生命周期 —— 
onMounted(() => {
  store.fetchLocations()
})

// —— ⑥ watch —— 
watch(selectedLocation, newVal => {
  console.log('选中充电区 ID:', newVal)
})

// —— ⑦ 方法 —— 
const onSearch = () => {}
const openLocationDialog = row => {
  locationForm.value = row ? { ...row } : { name: '' }
  dialogs.value.location = true
}
const saveLocation = async () => {
  await store.saveLocation(locationForm.value)
  ElMessage.success('充电区保存成功')
  dialogs.value.location = false
  store.fetchLocations()
}
const deleteLocation = async id => {
  await store.deleteLocation(id)
  if (selectedLocation.value === id) selectedLocation.value = null
}
const selectLocation = async id => {
  selectedLocation.value = id
  await store.fetchPiles(id)
}
const openPileDialog = row => {
  pileForm.value = row
    ? { ...row }
    : { name:'',connector:'',power_kw:0,fee_rate:0,status:'available' }
  dialogs.value.pile = true
}
const savePile = async () => {
  await store.savePile({ ...pileForm.value, location_id: selectedLocation.value })
  ElMessage.success('充电桩保存成功')
  dialogs.value.pile = false
  selectLocation(selectedLocation.value)
}
const deletePile = async id => {
  await store.deletePile(id)
  selectLocation(selectedLocation.value)
}
</script>

<style scoped>
.admin-charging-manage { padding: 20px; }
.controls { display: flex; justify-content: space-between; margin-bottom: 20px; }
</style>
