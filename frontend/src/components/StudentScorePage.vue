<template>
  <div class="student-score">
    <!-- 顶部统计区 -->
    <el-row gutter="20" class="summary-row">
      <!-- 当前积分卡片 -->
      <el-col :span="12">
        <el-card shadow="hover" class="score-summary-card">
          <template #header>
            <el-space align="center">
              <el-icon><Document /></el-icon>
              <span class="header-text">当前积分</span>
            </el-space>
          </template>
          <div class="score-value">{{ userScore }}</div>
        </el-card>
      </el-col>
      <!-- 违规上报卡片 -->
      <el-col :span="12">
        <el-card shadow="hover" class="report-card">
          <template #header>
            <el-space align="center">
              <el-icon><Warning /></el-icon>
              <span class="header-text">校园违规上报</span>
            </el-space>
          </template>
          <div class="card-body">
            <el-button type="danger" icon="Upload" @click="reportDialog = true">
              我要上报
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 积分明细 -->
    <el-card shadow="never" class="logs-card">
      <div class="logs-header">
        <el-space align="center">
          <el-icon><List /></el-icon>
          <span>积分明细</span>
        </el-space>
        <el-button type="primary" icon="Refresh" @click="refreshLogs">
          刷新
        </el-button>
      </div>
      <el-table
        :data="scoreLogs"
        v-loading="loading.logs"
        stripe
        border
        size="small"
        class="logs-table"
      >
        <el-table-column prop="id" label="记录ID" width="80"/>
        <el-table-column prop="license_plate" label="车牌号" width="140"/>
        <el-table-column prop="event_type" label="事件类型"/>
        <el-table-column label="分值变动" width="120">
          <template #default="{ row }">
            <el-tag :type="row.points >= 0 ? 'success' : 'danger'" effect="light">
              {{ row.points >= 0 ? '+' + row.points : row.points }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="source" label="来源" width="100"/>
        <el-table-column prop="timestamp" label="时间" width="180"/>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button
              v-if="row.points < 0 && row.source === 'auto' && row.appeal_status == null"
              size="small"
              type="warning"
              @click="openAppeal(row)"
            >
              申诉
            </el-button>
            <el-tag
              v-else-if="row.appeal_status === 'pending'"
              type="info"
              size="small"
            >
              待审核
            </el-tag>
            <el-tag
              v-else-if="row.appeal_status === 'approved'"
              type="success"
              size="small"
            >
              申诉通过
            </el-tag>
            <el-tooltip
              v-else-if="row.appeal_status === 'rejected'"
              :content="row.rejection_reason || '无理由说明'"
              placement="top"
            >
              <el-tag type="danger" size="small" effect="plain">
                申诉驳回
              </el-tag>
            </el-tooltip>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 弹窗：违规上报 -->
    <el-dialog title="违规上报" v-model="reportDialog" width="500px" :destroy-on-close="true">
      <el-form :model="reportForm" label-width="100px">
        <el-form-item label="车牌号">
          <el-select v-model="reportForm.license_plate" placeholder="请选择车牌号">
            <el-option
              v-for="plate in userPlates"
              :key="plate"
              :label="plate"
              :value="plate"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="事件类型">
          <el-select v-model="reportForm.event_type" placeholder="请选择事件类型">
            <el-option label="禁停区停车" value="forbidden_parking"/>
            <el-option label="其他违规" value="other_violation"/>
          </el-select>
        </el-form-item>
        <el-form-item label="详情描述">
          <el-input type="textarea" v-model="reportForm.details" placeholder="请输入违规详情"/>
        </el-form-item>
        <el-form-item label="图片证据">
          <el-upload
            action=""
            list-type="picture-card"
            :on-success="handleUploadSuccess"
            :file-list="reportForm.files"
          >
            <i class="el-icon-plus"></i>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="reportDialog = false">取消</el-button>
        <el-button type="primary" @click="submitReport">提交</el-button>
      </template>
    </el-dialog>

    <!-- 弹窗：积分申诉 -->
    <el-dialog title="积分申诉" v-model="appealDialog" width="400px" :destroy-on-close="true">
      <el-form :model="appealForm" label-width="100px">
        <el-form-item label="记录ID"><span>{{ appealForm.record_id }}</span></el-form-item>
        <el-form-item label="申诉原因">
          <el-input type="textarea" v-model="appealForm.reason" placeholder="请输入申诉原因"/>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="appealDialog = false">取消</el-button>
        <el-button type="primary" @click="submitAppeal">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { useScoreStore } from '@/store/score';
import { useAuthStore } from '@/store/auth';
import { useVehicleStore } from '@/store/vehicleService';
import { Document, Warning, List, } from '@element-plus/icons-vue';

const scoreStore = useScoreStore();
const authStore = useAuthStore();
const vehicleStore = useVehicleStore();

const userId = authStore.user.user_id;
const userScore = authStore.user.score;
const scoreLogs = ref([]);
const loading = ref({ logs: false });
const userPlates = ref([]);

const reportDialog = ref(false);
const reportForm = ref({ reporter_id: userId, license_plate: '', event_type: '', details: '', files: [] });

const appealDialog = ref(false);
const appealForm = ref({ record_id: null, reason: '' });

async function fetchScoreData() {
  loading.value.logs = true;
  try {
    const data = await scoreStore.fetchUserLogs(userId);
    scoreLogs.value = data;
  } finally {
    loading.value.logs = false;
  }
}

async function fetchAllPlates() {
  await vehicleStore.fetchAllVehicles();
  userPlates.value = vehicleStore.allVehicles.map(v => v.plate_number);
}

function refreshLogs() {
  fetchScoreData();
}

function openAppeal(row) {
  appealForm.value = { record_id: row.id, reason: '' };
  appealDialog.value = true;
}

async function submitReport() {
  if (!reportForm.value.details.trim()) return ElMessage.warning('请输入违规详情');
  try {
    await scoreStore.reportEvent(reportForm.value);
    ElMessage.success('上报成功，等待管理员审核');
    reportDialog.value = false;
    reportForm.value = { reporter_id: userId, license_plate: '', event_type: '', details: '', files: [] };
  } catch {
    ElMessage.error('上报失败');
  }
}

function handleUploadSuccess(res, file, fileList) {
  reportForm.value.files = fileList;
}

async function submitAppeal() {
  if (!appealForm.value.reason.trim()) return ElMessage.warning('请输入申诉原因');
  try {
    await scoreStore.submitAppeal({ user_id: userId, score_log_id: appealForm.value.record_id, reason: appealForm.value.reason });
    ElMessage.success('申诉提交成功');
    appealDialog.value = false;
    fetchScoreData();
  } catch {
    ElMessage.error('申诉提交失败');
  }
}

onMounted(() => {
  fetchScoreData();
  fetchAllPlates();
});
</script>

<style scoped>
.student-score { padding: 24px; background: #f5f7fa; }
.summary-row { margin-bottom: 20px; }
.score-summary-card,
.report-card { height: 120px; display: flex; flex-direction: column; justify-content: center; align-items: center; }
.score-summary-card .score-value {
  font-size: 36px;
  font-weight: bold;
  color: #409EFF;
}
.header-text { font-size: 18px; font-weight: 600; }
.report-col { text-align: right; }
.report-card .card-body { display: flex; justify-content: center; align-items: center; width: 100%; }
.logs-card { padding: 16px; }
.logs-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.logs-table ::v-deep .el-table__header { background: #eef1f6; }
</style>
