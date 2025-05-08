<template>
  <div class="charging-page el-container">
    <el-row gutter="20">
      <!-- 充电桩状态区 -->
      <el-col :span="16">
        <el-card shadow="hover" class="card--charging-status">
          <div class="card-header">
            <h3>充电桩状态</h3>
            <el-select
              v-model="selectedLocation"
              placeholder="选择充电区"
              :loading="loadingLocations"
              @change="onLocationChange"
              class="select-location"
            >
              <el-option
                v-for="loc in locations"
                :key="loc.id"
                :label="loc.name"
                :value="loc.id"
              />
            </el-select>
          </div>

          <el-skeleton :loading="loadingPiles" animated>
            <template #template>
              <el-skeleton-item variant="table" />
            </template>
            <el-table
              :data="piles"
              style="width: 100%"
              @row-click="openSlotDialog"
              highlight-current-row
            >
              <el-table-column prop="name" label="名称" width="180" />
              <el-table-column prop="connector" label="接口" width="120" />
              <!-- 状态列：根据是否有可预约时段显示 -->
              <el-table-column label="状态" width="120">
                <template #default="{ row }">
                  <el-tag
                    :type="hasAvailableSlots(row) ? 'success' : 'danger'"
                    size="small"
                    effect="light"
                  >
                    {{ hasAvailableSlots(row) ? '可预约' : '已约满' }}
                  </el-tag>
                </template>
              </el-table-column>
              <!-- 操作列：预约按钮在已约满时禁用 -->
              <el-table-column label="操作" width="100">
                <template #default="{ row }">
                  <el-button
                    size="small"
                    type="primary"
                    @click.stop="openSlotDialog(row)"
                    :disabled="!hasAvailableSlots(row)"
                  >
                    预约
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-skeleton>
        </el-card>
      </el-col>

      <!-- 我的预约区 -->
      <el-col :span="8">
        <el-card shadow="hover" class="card--my-reservations">
          <template #header>
            <div class="card-header">
              <span>我的充电预约</span>
            </div>
          </template>
          <div v-if="!reservations.length" class="no-reservations">
            <el-empty description="暂无充电预约" />
          </div>
          <el-list v-else>
            <el-list-item v-for="item in reservations" :key="item.sessionId">
              <div class="reservation-info">
                <div class="title">{{ item.pileName }}</div>
                <div>{{ item.date }} {{ item.startSlot }} - {{ item.endSlot }}</div>
              </div>
              <div class="status-info">
                <template v-if="item.status === 'completed'">
                  <i class="el-icon-check" /> 充电已完成：{{ formatElapsed(item) }}
                </template>
                <template v-else-if="item.status === 'reserved'">
                  <template v-if="isBeforeReserve(item)">
                    <i class="el-icon-time" /> 预约已确认
                  </template>
                  <template v-else>
                    <i class="el-icon-warning" /> 请尽快开始充电，预约将于 {{ autoReleaseCountdown(item) }} 分钟后自动取消
                  </template>
                </template>
                <template v-else-if="item.status === 'ongoing'">
                  <i class="el-icon-loading" /> 正在充电：{{ formatElapsed(item) }}
                </template>
                <template v-else-if="item.status === 'paused'">
                  <i class="el-icon-pause" /> 已暂停：{{ formatPauseElapsed(item) }}
                </template>
              </div>
              <div class="action-buttons">
                <template v-if="item.status === 'reserved'">
                  <el-button size="mini" type="success" :disabled="isBeforeReserve(item)" @click="start(item)">开始充电</el-button>
                  <el-button size="mini" type="danger" @click="confirmCancel(item)">取消预约</el-button>
                </template>
                <template v-else-if="['ongoing','paused'].includes(item.status)">
                  <el-button size="mini" type="info" @click="togglePause(item)">{{ item.status === 'ongoing' ? '暂停充电' : '继续充电' }}</el-button>
                  <el-button size="mini" type="warning" @click="confirmStop(item)">停止充电</el-button>
                </template>
              </div>
            </el-list-item>
          </el-list>
        </el-card>
      </el-col>
    </el-row>

    <!-- 预约对话框 -->
    <el-dialog v-model="slotDialogVisible" width="720px" destroy-on-close>
      <template #title>
        <span>选择预约时段</span>
        <el-date-picker
          v-model="selectedDate"
          type="date"
          placeholder="选择日期"
          value-format="YYYY-MM-DD"
          :picker-options="{ disabledDate: d => d < new Date() }"
          class="date-picker"
        />
      </template>

      <div v-if="loadingSlots" class="dialog-loading">
        <el-skeleton rows="3" animated />
      </div>

      <template v-else>
        <transition-group name="slot-fade" tag="div" class="slots-row">
          <div
            v-for="cell in futureSlotCells"
            :key="cell.time"
            class="slot-cell"
            :class="{ reserved: !cell.available, selected: cell.selected }"
            @click="selectCell(cell)"
            :aria-disabled="!cell.available"
          >
            <el-tooltip v-if="!cell.available" content="已被预约" placement="top">
              {{ cell.time }}
            </el-tooltip>
            <span v-else>{{ cell.time }}</span>
          </div>
        </transition-group>

        <div class="dialog-footer">
          <el-button type="primary" :disabled="!rangeStart" @click="confirmRange">
            预约 {{ rangeStart }} - {{ displayEnd }}
          </el-button>
        </div>
      </template>

      <template #footer>
        <el-button @click="slotDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import dayjs from 'dayjs'
import isSameOrBefore from 'dayjs/plugin/isSameOrBefore'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useChargingStore } from '@/store/charging'
import { useAuthStore } from '@/store/auth'
import { useVehicleStore } from '@/store/vehicleService'
import { startSession, stopSession, pauseSession, resumeSession, getMyReservations } from '@/api/charging'

dayjs.extend(isSameOrBefore)

// stores
const charging = useChargingStore()
const auth = useAuthStore()
const vehicleStore = useVehicleStore()

// 地点与桩
const locations = computed(() => charging.locations)
const selectedLocation = ref(null)
const loadingLocations = computed(() => charging.loading.locations)
const piles = computed(() => charging.piles)
const loadingPiles = computed(() => charging.loading.piles)

// 预约对话框
const slotDialogVisible = ref(false)
const currentPile = ref(null)
const selectedDate = ref(dayjs().format('YYYY-MM-DD'))
const loadingSlots = computed(() => charging.loading.slots)

// 当前时间
const now = ref(dayjs())
let reservationTimer, nowTimer

// 我的预约
const reservations = ref([])
async function loadMyReservations() {
  try {
    const { data } = await getMyReservations(auth.user.user_id)
    reservations.value = data.map(i => ({
      sessionId: i.session_id,
      pileId: i.pile_id,
      pileName: i.pile_name,
      date: i.date,
      startSlot: i.start_slot,
      endSlot: i.end_slot,
      status: i.status,
      startTime: i.start_time ? dayjs(i.start_time) : null,
      pausedTime: null,
      pausedDuration: 0
    }))
  } catch {
    ElMessage.error('加载预约失败')
  }
}

// 当天该桩是否还有可预约时段
function hasAvailableSlots(pile) {
  const slots = charging.slots[pile.id] || []
  const todayStr = dayjs().format('YYYY-MM-DD')
  return slots.some(s => {
    if (s.status !== 'free') return false
    const slotTime = dayjs(`${selectedDate.value} ${s.slot}`, 'YYYY-MM-DD HH:mm')
    if (selectedDate.value === todayStr) {
      return slotTime.isAfter(dayjs())
    }
    return dayjs(selectedDate.value).isAfter(dayjs(), 'day')
  })
}

// 预约弹窗打开
function openSlotDialog(pile) {
  currentPile.value = pile
  slotDialogVisible.value = true
  rangeStart.value = ''
  rangeEnd.value = ''
  charging.fetchPileSlots(pile.id, selectedDate.value, auth.user.user_id)
}

// 监听日期或桩变化，刷新时段
watch(selectedDate, async (newDate) => {
  if (!piles.value.length) return
  for (const pile of piles.value) {
    await charging.fetchPileSlots(pile.id, newDate, auth.user.user_id)
  }
})

// 生成槽位格子
const slotCells = computed(() => {
  const raw = charging.slots[currentPile.value?.id] || []
  const reservedSet = new Set(raw.filter(s => s.status !== 'free').map(s => s.slot))
  let dt = dayjs(selectedDate.value)
  const startMs = rangeStart.value ? dayjs(`${selectedDate.value} ${rangeStart.value}`).valueOf() : null
  const endMs = rangeEnd.value ? dayjs(`${selectedDate.value} ${rangeEnd.value}`).valueOf() : null
  const cells = []
  for (let i = 0; i < 72; i++) {
    const time = dt.format('HH:mm')
    const tm = dt.valueOf()
    const isPast = tm <= now.value.valueOf()
    const available = !isPast && !reservedSet.has(time)
    const selected = startMs !== null && endMs !== null && tm >= startMs && tm < endMs
    cells.push({ time, available, isPast, selected })
    dt = dt.add(20, 'minute')
  }
  return cells
})
const futureSlotCells = computed(() => slotCells.value.filter(c => !c.isPast))

// 区间选择
const rangeStart = ref('')
const rangeEnd = ref('')
function selectCell(cell) {
  if (!cell.available) return
  if (!rangeStart.value || rangeEnd.value) {
    rangeStart.value = cell.time
    rangeEnd.value = ''
  } else if (dayjs(cell.time, 'HH:mm').isAfter(dayjs(rangeStart.value, 'HH:mm'))) {
    const conflict = futureSlotCells.value
      .filter(c => dayjs(c.time, 'HH:mm').isAfter(dayjs(rangeStart.value, 'HH:mm')) && dayjs(c.time, 'HH:mm').isSameOrBefore(dayjs(cell.time, 'HH:mm')))
      .some(c => !c.available)
    if (conflict) {
      ElMessage.error('所选区间包含不可预约段，请重新选择')
      rangeStart.value = ''
    } else {
      rangeEnd.value = cell.time
    }
  } else {
    rangeStart.value = cell.time
  }
}

// 计算真正要展示和提交的结束时间
const displayEnd = computed(() => {
  if (!rangeStart.value) return ''
  if (!rangeEnd.value) {
    return dayjs(rangeStart.value, 'HH:mm').add(20, 'minute').format('HH:mm')
  }
  return rangeEnd.value === '23:40' ? '24:00' : rangeEnd.value
})

// 确认预约
async function confirmRange() {
  if (!rangeStart.value) return
  const endSlot = displayEnd.value
  try {
    await charging.reservePile(
      auth.user.user_id,
      currentPile.value.id,
      vehicleStore.vehicle.vehicle_id,
      selectedDate.value,
      rangeStart.value,
      endSlot
    )
    ElMessage.success('预约成功')
    slotDialogVisible.value = false
    await loadMyReservations()
  } catch {
    ElMessage.error('预约失败')
  }
}

// 取消/停止确认
async function confirmCancel(item) {
  try {
    await ElMessageBox.confirm('确定取消该预约？')
    await charging.cancelReservation(
      item.sessionId,
      item.pileId,
      item.date,
      auth.user.user_id
    )
    ElMessage.success('取消成功')
    await loadMyReservations()
  } catch {
    ElMessage.error('取消失败')
  }
}
async function confirmStop(item) {
  try {
    await ElMessageBox.confirm('确定停止充电？')
    await stopSession(item.sessionId)
    item.status = 'completed'
    ElMessage.success('已停止')
  } catch {
    ElMessage.error('停止失败')
  }
}

// 开始/暂停/继续
async function start(item) {
  try {
    await startSession(item.sessionId)
    item.status = 'ongoing'
    item.startTime = dayjs()
    ElMessage.success('开始充电')
  } catch {
    ElMessage.error('开始失败')
  }
}
async function togglePause(item) {
  if (item.status === 'ongoing') {
    await pauseSession(item.sessionId)
    item.status = 'paused'
    item.pausedTime = dayjs()
    ElMessage.success('已暂停')
  } else {
    await resumeSession(item.sessionId)
    item.status = 'ongoing'
    item.pausedDuration += dayjs().diff(item.pausedTime)
    item.pausedTime = null
    ElMessage.success('继续充电')
  }
}

// 我的预约辅助
function isBeforeReserve(item) {
  return now.value.isBefore(dayjs(`${item.date} ${item.startSlot}`))
}
function autoReleaseCountdown(item) {
  const startMs = dayjs(`${item.date} ${item.startSlot}`).valueOf()
  return Math.max(0, Math.ceil((startMs + 5*60*1000 - now.value.valueOf())/60000))
}
function formatElapsed(item) {
  if (!item.startTime) return '00h 00m'
  const paused = item.pausedDuration + (item.pausedTime ? dayjs().diff(item.pausedTime) : 0)
  const diff = dayjs().diff(item.startTime) - paused
  const h = Math.floor(diff/3600000), m = Math.floor((diff%3600000)/60000)
  return `${String(h).padStart(2,'0')}h ${String(m).padStart(2,'0')}m`
}
function formatPauseElapsed(item) {
  if (!item.pausedTime) return '0m'
  return `${Math.floor(dayjs().diff(item.pausedTime)/60000)}m`
}

// 切换充电区
async function onLocationChange(locId) {
  try {
    await charging.fetchPiles(locId)
    for (const pile of piles.value) {
      charging.fetchPileSlots(pile.id, selectedDate.value, auth.user.user_id)
    }
  } catch {
    ElMessage.error('加载桩位失败')
  }
}

// 生命周期
onMounted(async () => {
  await charging.fetchLocations()
  if (locations.value.length) {
    selectedLocation.value = locations.value[0].id
    await onLocationChange(selectedLocation.value)
  }
  await loadMyReservations()
  reservationTimer = setInterval(loadMyReservations, 60000)
  nowTimer = setInterval(() => { now.value = dayjs() }, 1000)
})
onUnmounted(() => {
  clearInterval(reservationTimer)
  clearInterval(nowTimer)
})
</script>

<style scoped>
.charging-page { padding: 20px; max-width: 1200px; margin: auto; }
.card--charging-status, .card--my-reservations { margin-top: 20px; }
.card-header { display: flex; align-items: center; justify-content: space-between; }
.select-location { width: 240px; }
.slots-row { display: flex; overflow-x: auto; padding: 8px; border: 1px solid #eaeaea; background: #fdfdfd; border-radius: 6px; }
.slot-cell { flex: 0 0 60px; text-align: center; line-height: 28px; margin-right: 4px; border-radius: 4px; user-select: none; transition: transform .2s, background .2s; cursor: pointer; }
.slot-cell:hover { transform: translateY(-2px); box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
.slot-cell.reserved { background: #fde2e2; color: #d9534f; cursor: not-allowed; }
.slot-cell.selected { background: #cce5ff; color: #004085; }
.dialog-footer { margin-top: 16px; text-align: right; }
.slot-fade-enter-active, .slot-fade-leave-active { transition: all .3s; }
.slot-fade-enter-from, .slot-fade-leave-to { opacity: 0; transform: translateY(10px); }
.date-picker { margin-left: 16px; }
.no-reservations { padding: 40px; text-align: center; }
</style>
