<template>
  <div class="admin-score-management">
    <el-tabs v-model="activeTab" class="score-tabs" type="card" stretch>
      <!-- 1. 积分规则设置 -->
      <el-tab-pane label="积分规则设置" name="rules">
        <el-card class="box-card">
          <template #header>
            <div class="card-header">
              <span>规则列表</span>
              <el-button type="primary" size="small" icon="Plus" @click="openRuleDialog()">新建规则</el-button>
            </div>
          </template>
          <el-table
            :data="scoreStore.scoreRules"
            v-loading="scoreStore.loading.rules"
            stripe
            highlight-current-row
            @row-click="openRuleDialog"
            :header-cell-style="{ background: '#f5f7fa', color: '#303133', fontWeight: '600' }"
            style="width:100%; margin-top:10px;"
          >
            <el-table-column prop="event_type"      label="事件类型" width="180"/>
            <el-table-column prop="points"          label="分值" width="120"/>
            <el-table-column prop="description"     label="描述"/>
            <el-table-column prop="frequency_limit" label="频率与上限"/>
            <el-table-column prop="remark"          label="备注"/>
            <el-table-column label="操作" width="200">
              <template #default="{ row }">
                <el-tooltip content="编辑此规则" placement="top">
                  <el-button size="small" icon="Edit" @click.stop="openRuleDialog(row)">编辑</el-button>
                </el-tooltip>
                <el-tooltip content="删除此规则" placement="top">
                  <el-button size="small" type="danger" icon="Delete" @click.stop="deleteRule(row.id)">删除</el-button>
                </el-tooltip>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
        <el-dialog title="积分规则" v-model="isRuleDialogVisible" width="500px" :destroy-on-close="true">
          <el-form :model="ruleForm" label-width="110px" :label-position="'left'">
            <el-form-item label="事件类型">
              <el-select v-model="ruleForm.event_type" placeholder="请选择事件类型" @change="onEventTypeChange">
                <el-option label="禁停区停车" value="forbidden_parking"/>
                <el-option label="规范停车" value="normal_parking"/>
                <el-option label="其他严重交通违规" value="other_violation"/>
              </el-select>
            </el-form-item>
            <el-form-item label="分值">
              <el-input-number v-model="ruleForm.points" :min="-100" :max="100"/>
            </el-form-item>
            <el-form-item label="描述">
              <el-input v-model="ruleForm.description"/>
            </el-form-item>
            <el-form-item label="频率与上限">
              <el-input v-model="ruleForm.frequency_limit" placeholder="填写频率与上限说明"/>
            </el-form-item>
            <el-form-item label="备注">
              <el-input v-model="ruleForm.remark" placeholder="填写备注"/>
            </el-form-item>
          </el-form>
          <template #footer>
            <el-button @click="isRuleDialogVisible = false">取消</el-button>
            <el-button type="primary" @click="saveRule">保存</el-button>
          </template>
        </el-dialog>
      </el-tab-pane>

      <!-- 2. 系统自动加减分 -->
      <el-tab-pane label="积分日志" name="auto">
        <el-card class="box-card small-card">
          <el-table
            :data="scoreStore.autoLogs"
            v-loading="scoreStore.loading.auto"

            style="width:100%"
          >
            <el-table-column prop="id" label="记录ID" width="100"/>
            <el-table-column prop="user_id" label="用户ID" width="100"/>
            <el-table-column prop="license_plate" label="车牌号" width="120"/>
            <el-table-column prop="event_type" label="事件类型" width="150"/>
            <el-table-column prop="points" label="分值变动" width="100"/>
            <el-table-column prop="timestamp" label="时间" width="170"/>
            <el-table-column prop="source" label="来源" width="100"/>
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- 3. 人工上报事件审核 -->
      <el-tab-pane label="上报事件审核" name="report">
        <el-card class="box-card small-card">
          <el-table
            :data="scoreStore.reportedEvents"
            v-loading="scoreStore.loading.reports"
            stripe
            border
            style="width:100%"
          >
            <el-table-column prop="id" label="ID" width="50"/>
            <el-table-column prop="reporter" label="上报人" width="90"/>
            <el-table-column prop="license_plate" label="车牌号" width="100"/>
            <el-table-column prop="event_type" label="事件类型" width="100"/>
            <el-table-column prop="details" label="详情"/>
            <el-table-column prop="created_at" label="上报时间" width="170"/>
            <el-table-column label="操作" width="260">
              <template #default="{ row }">
                <el-input-number v-model="row.adjust_points" :min="-100" :max="100" size="small"/>
                <el-button size="small" type="success" @click="approveReport(row)">通过</el-button>
                <el-button size="small" type="danger" @click="rejectReport(row.id)">驳回</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- 4. 扣分申诉管理 -->
      <el-tab-pane label="申诉管理" name="appeal">
        <el-card class="box-card small-card">
          <el-table
            :data="scoreStore.appeals"
            v-loading="scoreStore.loading.appeals"
            stripe
            border
            style="width:100%"
          >
            <el-table-column prop="id" label="申诉ID" width="50"/>
            <el-table-column prop="user_id" label="用户ID" width="50"/>
            <el-table-column prop="license_plate" label="车牌号" width="90"/>
            <el-table-column prop="event_type" label="事件类型" width="110"/>
            <el-table-column prop="reason" label="申诉原因"/>
            <el-table-column prop="status" label="状态" width="90">
              <template #default="{ row }">
                <el-tag 
                  :type="row.status === 'approved' ? 'success' : 
                        row.status === 'rejected' ? 'danger' : 'info'"
                >
                  {{ row.status === 'approved' ? '已批准' : 
                    row.status === 'rejected' ? '已驳回' : '待处理' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="rejection_reason" label="驳回原因" width="120"/>
            <el-table-column prop="created_at" label="申请时间" width="130"/>
            <el-table-column label="操作" width="150">
              <template #default="{ row }">
                <el-button size="small" type="primary" :disabled="row.status!=='pending'" @click="handleAppealApprove(row.id)">同意</el-button>
                <el-button size="small" type="danger" :disabled="row.status!=='pending'" @click="openRejectDialog(row.id)">驳回</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
        
        <!-- 新增：申诉驳回原因对话框 -->
        <el-dialog v-model="rejectDialogVisible" title="驳回申诉" width="400px" :destroy-on-close="true">
          <el-form :model="rejectForm" label-width="100px">
            <el-form-item label="驳回原因">
              <el-input 
                type="textarea" 
                v-model="rejectForm.rejection_reason" 
                placeholder="请输入驳回原因（将显示给申诉用户）"
                :rows="4"
              />
            </el-form-item>
          </el-form>
          <template #footer>
            <el-button @click="rejectDialogVisible = false">取消</el-button>
            <el-button type="danger" @click="handleAppealReject">确认驳回</el-button>
          </template>
        </el-dialog>
      </el-tab-pane>


      <!-- 5. 用户积分表 -->
      <el-tab-pane label="用户积分表" name="manual">
        <el-card class="box-card">
          <div class="search-bar">
            <el-input
              v-model="manualSearch"
              placeholder="搜索：用户名 / 手机号 / 车牌号"
              clearable
              prefix-icon="Search"
              style="width: 360px;"
            />
          </div>
          <el-table
            :data="filteredUserScores"
            v-loading="scoreStore.loading.users"
            border
            stripe
            highlight-current-row
            style="width:100%; margin-top:10px;"
            :header-cell-style="{ textAlign:'center', background: '#f5f7fa' }"
            :cell-style="{ textAlign:'center' }"
          >
            <el-table-column prop="user_id" label="用户ID" width="100"/>
            <el-table-column prop="name" label="用户名" width="150"/>
            <el-table-column prop="phone" label="手机号" width="150"/>
            <el-table-column prop="license_plate" label="车牌号" width="150"/>
            <el-table-column prop="current_score" label="当前积分" width="120"/>
            <el-table-column label="操作" width="200">
              <template #default="{ row }">
                <el-button size="small" type="primary" @click="openManualDialog(row)">调整积分</el-button>
                <el-button size="small" type="text" @click="viewLogs(row.user_id)">详情</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
        <!-- 弹窗：手动调整积分 -->
        <el-dialog v-model="manualDialogVisible" title="手动加减分" width="400px" :destroy-on-close="true">
          <el-form :model="manualForm" label-width="100px">
            <el-form-item label="用户ID"><span>{{ manualForm.user_id }}</span></el-form-item>
            <el-form-item label="用户名"><span>{{ manualForm.name }}</span></el-form-item>
            <el-form-item label="调整分值"><el-input-number v-model="manualForm.points" :min="-999" :max="999"/></el-form-item>
            <el-form-item label="原因">
              <el-input type="textarea" v-model="manualForm.reason" placeholder="请输入加/扣分原因"/>
            </el-form-item>
          </el-form>
          <template #footer>
            <el-button @click="manualDialogVisible = false">取消</el-button>
            <el-button type="primary" @click="submitManualAdjust">确定</el-button>
          </template>
        </el-dialog>

        <!-- 弹窗：查看积分明细 -->
        <el-dialog v-model="detailDialogVisible" title="积分明细" width="60%" :destroy-on-close="true">
          <el-table
            :data="scoreStore.userLogs"
            v-loading="scoreStore.loading.logs"
            border
            stripe
            :header-cell-style="{ textAlign:'center', background: '#f5f7fa' }"
            :cell-style="{ textAlign:'center' }"
            style="width: 100%;"
          >
            <el-table-column prop="id" label="记录ID" width="80"/>
            <el-table-column prop="license_plate" label="车牌号" width="140"/>
            <el-table-column prop="event_type" label="事件类型"/>
            <el-table-column prop="points" label="分值变动" width="100"/>
            <el-table-column prop="source" label="来源" width="100"/>
            <el-table-column prop="timestamp" label="时间" width="180"/>
          </el-table>
          <template #footer>
            <el-button @click="detailDialogVisible = false">关闭</el-button>
          </template>
        </el-dialog>
      </el-tab-pane>

      <!-- 6. 违规记录审核 -->
      <el-tab-pane label="违规记录审核" name="review">
        <el-card class="box-card small-card">
          <el-table
            :data="scoreStore.violations"
            v-loading="scoreStore.loading.violations"
            stripe
            border
            style="width:100%"
          >
            <el-table-column prop="id" label="ID" width="80"/>
            <el-table-column prop="user_id" label="用户ID" width="120"/>
            <el-table-column prop="license_plate" label="车牌号" width="120"/>
            <el-table-column prop="event_type" label="事件类型" width="150"/>
            <el-table-column prop="location" label="位置"/>
            <el-table-column prop="timestamp" label="时间" width="180"/>
            <el-table-column label="操作" width="160">
              <template #default="{ row }">
                <el-button size="small" type="primary" @click="approveViolation(row.id)">通过</el-button>
                <el-button size="small" type="danger" @click="rejectViolation(row.id)">驳回</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="模拟违规" name="violation">
        <ViolationManagement />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useScoreStore } from '@/store/score'
import { ElMessage } from 'element-plus'
import ViolationManagement from '@/components/ViolationManagement.vue'

const scoreStore = useScoreStore()
const activeTab = ref('rules')

const ruleForm = ref({ id: null, event_type: '', points: 0, description: '', frequency_limit: '', remark: '' })
const isRuleDialogVisible = ref(false)

const manualSearch = ref('')
const manualDialogVisible = ref(false)
const manualForm = ref({ user_id: null, name: '', points: 0, reason: '' })
const detailDialogVisible = ref(false)

const rejectDialogVisible = ref(false)
const rejectForm = ref({ appeal_id: null, rejection_reason: '' })

const predefinedRules = {
  forbidden_parking: { description: '用户将车停在禁止区域', frequency_limit: '每次扣 10 分；同日可多次扣，日累计上限 –30 分', remark: '一周内累计 3 次以上，在通知功能模块通报展示' },
  normal_parking: { description: '用户停入合法停车位', frequency_limit: '每次加 2 分；日累计上限 +6 分', remark: '每周累计上限 +20 分' },
  other_violation: { description: '其他经传感或摄像头判定的严重违规', frequency_limit: '每次扣 10 分；日累计上限 –30 分', remark: '严重者一周内累计超过3 次，在通知功能模块通报展示' }
}

// 打开驳回对话框
function openRejectDialog(id) {
  rejectForm.value = { appeal_id: id, rejection_reason: '' }
  rejectDialogVisible.value = true
}

// 处理申诉批准
async function handleAppealApprove(id) {
 try {
  await scoreStore.handleAppeal(id, true);
   ElMessage.success('申诉已批准');
  } catch (e) {
   console.error(e);
   ElMessage.error('操作失败');
 }
}

// 处理申诉驳回
async function handleAppealReject() {
  if (!rejectForm.value.rejection_reason.trim()) {
    ElMessage.warning('请输入驳回原因')
    return
  }
  
  try {
    await scoreStore.handleAppeal(
      rejectForm.value.appeal_id, 
      false, 
      rejectForm.value.rejection_reason
    )
    rejectDialogVisible.value = false
    ElMessage.success('申诉已驳回')
  } catch (e) {
    console.error(e)
    ElMessage.error('操作失败')
  }
}

function onEventTypeChange() {
  const cfg = predefinedRules[ruleForm.value.event_type]
  if (cfg) Object.assign(ruleForm.value, cfg)
}
function openRuleDialog(r = null) { if (r) ruleForm.value = { ...r }; else ruleForm.value = { id: null, event_type: '', points: 0, description: '', frequency_limit: '', remark: '' }; isRuleDialogVisible.value = true }
async function saveRule() { try { ruleForm.value.id ? await scoreStore.updateRule(ruleForm.value.id, ruleForm.value) : await scoreStore.createRule(ruleForm.value); isRuleDialogVisible.value = false } catch (e) { console.error(e) } }
async function deleteRule(id) { try { await scoreStore.deleteRule(id) } catch (e) { console.error(e) } }
async function approveReport(row) { try { await scoreStore.approveReport(row.id, row.adjust_points) } catch (e) { console.error(e) } }
async function rejectReport(id) { try { await scoreStore.rejectReport(id) } catch (e) { console.error(e) } }
// async function handleAppeal(id, agree) { try { await scoreStore.handleAppeal(id, agree) } catch (e) { console.error(e) } }
function openManualDialog(row) { manualForm.value = { user_id: row.user_id, name: row.name, points: 0, reason: '' }; manualDialogVisible.value = true }
async function submitManualAdjust() { if (!manualForm.value.reason.trim()) return ElMessage.warning('请输入原因'); try { await scoreStore.manualAdjust(manualForm.value); ElMessage.success('操作成功'); manualDialogVisible.value = false; manualForm.value.points = 0; manualForm.value.reason = '' } catch (e) { ElMessage.error('操作失败') } }
function viewLogs(userId) { scoreStore.fetchUserLogs(userId).then(() => { detailDialogVisible.value = true }) }
async function approveViolation(id) { try { await scoreStore.approveViolation(id) } catch (e) { console.error(e) } }
async function rejectViolation(id) { try { await scoreStore.rejectViolation(id) } catch (e) { console.error(e) } }
const filteredUserScores = computed(() => {
  const q = manualSearch.value.trim().toLowerCase()
  return q ? scoreStore.userScores.filter(u => [u.name, u.phone, u.license_plate].some(v => v && v.toLowerCase().includes(q))) : scoreStore.userScores
})

onMounted(() => {
  scoreStore.fetchRules()
  scoreStore.fetchAutoLogs()
  scoreStore.fetchReported()
  scoreStore.fetchAppeals()
  scoreStore.fetchViolations()
  scoreStore.fetchUserScores()
})
</script>

<style scoped>
.admin-score-management { padding: 24px; background: #f0f2f5; }
.score-tabs { margin-top: 20px; }
.box-card { margin-bottom: 20px; }
.small-card { padding: 12px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.search-bar { text-align: right; margin-bottom: 16px; }
</style>
