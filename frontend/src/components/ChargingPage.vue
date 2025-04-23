  <template>
    <div class="charging-page">
      <el-row gutter="20">
        <el-col :span="16">
          <el-card :body-style="{ padding: '20px' }">
            <h3>充电桩状态</h3>

            <!-- 1. 选择充电区 -->
            <el-select
              v-model="charging.selectedLocation"
              placeholder="选择充电区"
              :loading="charging.loading.locations"
              @change="onLocationChange"
              style="width: 300px; margin-bottom: 20px;"
            >
              <el-option
                v-for="loc in charging.locations"
                :key="loc.id"
                :label="loc.name"
                :value="loc.id"
              />
            </el-select>

            <!-- 2. 列表中每条桩都可打开“时段对话框” -->
            <el-table
              :data="charging.piles"
              style="width: 100%"
              v-loading="charging.loading.piles"
              @row-click="openSlotDialog"
            >
              <el-table-column prop="name" label="名称" />
              <el-table-column prop="connector" label="接口" />
              <el-table-column prop="status" label="状态" />
              <el-table-column label="操作">
                <template #default="{ row }">
                  <el-button
                    size="small"
                    type="primary"
                    @click.stop="openSlotDialog(row)"
                  >去预约</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>

        <!-- 3. 我的预约 -->
        <el-col :span="8">
          <el-card header="我的预约" :body-style="{ padding: '20px' }">
            <div v-if="myReservations.length===0">
              暂无预约
            </div>
            <el-list v-else>
              <el-list-item v-for="item in myReservations" :key="item.sessionId">
                <div>
                  <strong>{{ item.pileName }}</strong><br>
                  {{ item.date }} {{ item.slot }}
                </div>
                <div style="margin-top: 5px;">
                  <el-button
                    size="mini"
                    type="danger"
                    @click="cancel(item)"
                  >取消</el-button>
                  <el-button
                    size="mini"
                    type="success"
                    @click="start(item)"
                    :disabled="item.status!=='reserved'"
                  >开始</el-button>
                  <el-button
                    size="mini"
                    type="warning"
                    @click="stop(item)"
                    :disabled="item.status!=='ongoing'"
                  >停止</el-button>
                </div>
              </el-list-item>
            </el-list>
          </el-card>
        </el-col>
      </el-row>

      <!-- 4. 时段对话框：支持多选时段 -->
      <el-dialog
        v-model="slotDialogVisible"
        width="600px"
      >
        <template #title>
          <span>预约时段</span>
          <el-date-picker
            v-model="selectedDate"
            type="date"
            placeholder="选择日期"
            value-format="YYYY-MM-DD"
            :picker-options="{ disabledDate: date => date < new Date() }"
            @change="onDateChange"
            style="margin-left: 20px;"
          />
        </template>

        <div v-if="loadingSlots">
          <el-skeleton rows="3" animated />
        </div>
        <div v-else>
          <el-time-picker
            v-model="selectedSlots"
            is-range
            range-separator="至"
            start-placeholder="开始时段"
            end-placeholder="结束时段"
            format="HH:mm"
            value-format="HH:mm"
          />
          <div style="margin-top: 20px;">
            <el-button
              type="primary"
              :disabled="selectedSlots.length !== 2"
              @click="batchReserve"
            >预约选中时段</el-button>
          </div>
        </div>
        <template #footer>
          <el-button @click="slotDialogVisible=false">关闭</el-button>
        </template>
      </el-dialog>
    </div>
  </template>

  <script setup>
  import { ref, onMounted,onUnmounted} from 'vue'
  import { ElMessage } from 'element-plus'
  import { useChargingStore } from '@/store/charging'
  import { useAuthStore } from '@/store/auth'
  import { useVehicleStore } from '@/store/vehicleService'
  import { startSession, stopSession,getMyReservations } from '@/api/charging'
  const charging = useChargingStore()
  const auth = useAuthStore()
  const vehicleStore = useVehicleStore()

  // 状态
  const slotDialogVisible = ref(false)
  const currentPile = ref(null)
  const today = new Date()
  const defaultDate = `${today.getFullYear()}-${(today.getMonth()+1).toString().padStart(2,'0')}-${today.getDate().toString().padStart(2,'0')}`
  const selectedDate = ref(defaultDate)
  // 多选时段
  const selectedSlots = ref([])  // now array of two HH:mm strings

  // 我的预约
  const myReservations = ref([])

  // 初始化
  onMounted(() => {
    // 首次加载
   (async () => {
     await charging.fetchLocations()
     await loadMyReservations()
   })()
  // 每分钟刷新一次
  const timer = setInterval(async () => {
    await loadMyReservations()
    if (currentPile.value) {
      await charging.fetchPileSlots(
        currentPile.value.id,
        selectedDate.value,
        auth.user.user_id
      )
    }
  }, 60 * 1000)
  onUnmounted(() => clearInterval(timer))
})
  // 充电区切换
  async function onLocationChange(locId) {
    try {
      await charging.fetchPiles(locId)
      // 清空当前预约视图
      // myReservations.value = []
    } catch {
      ElMessage.error('加载充电桩失败')
    }
  }

  // 打开对话框时，拉完时段后刷新我的预约
  async function openSlotDialog(pile) {
    currentPile.value = pile
    slotDialogVisible.value = true
    selectedSlots.value = []
    try {
      await charging.fetchPileSlots(pile.id, selectedDate.value, auth.user.user_id)
      loadMyReservations()         // ← 新增：时段拉完就同步“我的预约”
    } catch {
      ElMessage.error('加载时段失败')
    }
  }

  // 切换日期时，也要拉完时段后刷新“我的预约”
  async function onDateChange(date) {
    if (!currentPile.value) return
    try {
      await charging.fetchPileSlots(currentPile.value.id, date, auth.user.user_id)
      loadMyReservations()         // ← 新增：日期切换后同步“我的预约”
    } catch {
      ElMessage.error('加载时段失败')
    }
  }


  // 批量预约
  async function batchReserve() {
    if (!currentPile.value || selectedSlots.value.length !== 2) return
    const [start, end] = selectedSlots.value
    // 生成每小时/半小时的时段数组
    const slots = generateSlots(start, end)
    try {
      for (const slot of slots) {
        await charging.reservePile(
          auth.user.user_id,
          currentPile.value.id,
          vehicleStore.vehicle.vehicle_id,
          selectedDate.value,
          slot
        )
      }
      ElMessage.success('批量预约成功')
      slotDialogVisible.value = false
      loadMyReservations()
    } catch {
      ElMessage.error('批量预约失败')
    }
  }

  // 生成选中区间内所有时段（每小时）
  function generateSlots(start, end) {
    const slots = []
    // const [h1, m1] = start.split(':').map(Number)
    // const [h2, m2] = end.split(':').map(Number)
    let dt = new Date(`${selectedDate.value} ${start}`)
    const endDt = new Date(`${selectedDate.value} ${end}`)
    while (dt < endDt) {
      const hh = dt.getHours().toString().padStart(2,'0')
      const mm = dt.getMinutes().toString().padStart(2,'0')
      slots.push(`${hh}:${mm}`)
      dt.setHours(dt.getHours()+1)
    }
    return slots
  }

  // 加载“我的预约”

  async function loadMyReservations() {
    try {
      const { data } = await getMyReservations(auth.user.user_id)
      myReservations.value = data.map(item => ({
        sessionId: item.session_id,
        pileName:  item.pile_name,
        date:      item.date,
        slot:      item.slot,
        status:    item.status
      }))
    } catch (e) {
      ElMessage.error('加载我的预约失败')
    }
  }


  // 操作
  async function cancel(item) {
    try {
      await charging.cancelReservation(item.sessionId, currentPile.value.id, item.date,auth.user.user_id)
      ElMessage.success('取消成功')
      loadMyReservations()
    } catch {
      ElMessage.error('取消失败')
    }
  }
  async function start(item) {
    try {
      await startSession(item.sessionId)
      ElMessage.success('开始充电')
      await loadMyReservations()
    } catch {
      ElMessage.error('开始失败')
    }
  }
  async function stop(item) {
    try {
      await stopSession(item.sessionId)
      ElMessage.success('停止充电')
      await loadMyReservations()
    } catch {
      ElMessage.error('停止失败')
    }
  }
  </script>

  <style scoped>
  .charging-page { padding: 20px; }
  .el-card { margin-top: 20px; }
  .el-select { width: 300px; }
  </style>
