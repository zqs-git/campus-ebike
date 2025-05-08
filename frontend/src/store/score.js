// src/stores/score.js
import { defineStore } from 'pinia';
import * as scoreApi from '@/api/score';

export const useScoreStore = defineStore('score', {
  state: () => ({
    scoreRules: [],
    autoLogs: [],
    userScores: [],
    userLogs: [],
    userAppeals: [],       // 存储当前用户的申诉记录
    reportedEvents: [],
    appeals: [],
    manualUser: null,
    violations: [],
    loading: {
      rules: false,
      auto: false,
      reports: false,
      appeals: false,
      manual: false,
      violations: false,
      users: false,
      logs: false,
      userAppeals: false,
    },
  }),
  actions: {
    // 拉取用户积分列表
    async fetchUserScores() {
      this.loading.users = true;
      try {
        const { data } = await scoreApi.getUserScores();
        this.userScores = data;
      } finally {
        this.loading.users = false;
      }
    },

    // 拉取某用户的日志明细，并合并该用户的申诉状态
    async fetchUserLogs(userId) {
      this.loading.logs = true;
      try {
        // 1. 获取原始积分日志
        const { data: logs } = await scoreApi.getUserLogs(userId);
        // 2. 获取该用户所有申诉
        this.loading.userAppeals = true;
        const { data: appeals } = await scoreApi.getAppeals(userId);
        this.userAppeals = appeals;
        // 3. 合并状态到日志
        const merged = logs.map(log => {
          const app = appeals.find(a => a.score_log_id === log.id);
          return {
            ...log,
            appeal_status: app ? app.status : null,
            rejection_reason: app ? app.rejection_reason : '',
          };
        });
        this.userLogs = merged;
        return merged;
      } finally {
        this.loading.logs = false;
        this.loading.userAppeals = false;
      }
    },

    // —— 模拟生成违规 ——
    async simulateViolation(form) {
      await scoreApi.simulateViolation(form);
    },
    async simulateBatchViolations({ count, useOnlyRealUsers }) {
      await scoreApi.simulateBatchViolations({ count, useOnlyRealUsers });
    },

    // 规则设置
    async fetchRules() {
      this.loading.rules = true;
      try {
        const { data } = await scoreApi.getRules();
        this.scoreRules = data;
      } finally {
        this.loading.rules = false;
      }
    },
    async createRule(rule) {
      const { data } = await scoreApi.createRule(rule);
      this.scoreRules.push(data);
    },
    async updateRule(id, rule) {
      const { data } = await scoreApi.updateRule(id, rule);
      const idx = this.scoreRules.findIndex(r => r.id === id);
      if (idx > -1) this.scoreRules.splice(idx, 1, data);
    },
    async deleteRule(id) {
      await scoreApi.deleteRule(id);
      this.scoreRules = this.scoreRules.filter(r => r.id !== id);
    },

    // 自动日志
    async fetchAutoLogs() {
      this.loading.auto = true;
      try {
        const { data } = await scoreApi.getAutoLogs();
        this.autoLogs = data;
      } finally {
        this.loading.auto = false;
      }
    },

    // 上报违规事件
    async reportEvent(form) {
      const { data } = await scoreApi.createReport(form);
      return data;
    },

    // 上报事件审核（管理员端）
    async fetchReported() {
      this.loading.reports = true;
      try {
        const { data } = await scoreApi.getPendingReports();
        this.reportedEvents = data.map(r => ({ ...r, adjust_points: 0 }));
      } finally {
        this.loading.reports = false;
      }
    },
    async approveReport(id, points) {
      await scoreApi.approveReport(id, points);
      this.fetchReported();
    },
    async rejectReport(id) {
      await scoreApi.rejectReport(id);
      this.fetchReported();
    },

    // 申诉管理（管理员端）
    async fetchAppeals() {
      this.loading.appeals = true;
      try {
        const { data } = await scoreApi.getAppeals();
        this.appeals = data;
      } finally {
        this.loading.appeals = false;
      }
    },

    async handleAppeal(id, approve, rejectionReason = '') {
      // 1. 构造 payload
      const payload = { approve };
      if (!approve) payload.rejection_reason = rejectionReason;
      
      // 2. 调接口
      await scoreApi.handleAppeal(id, payload);
      
      // 3. 刷新列表，等它完成再返回
      await this.fetchAppeals();
    },

    // 提交申诉（学生端）
    async submitAppeal({ user_id, score_log_id, reason }) {
      const { data } = await scoreApi.createAppeal({ user_id, score_log_id, reason });
      return data;
    },

    // 手动加减分
    async searchUsers(q) {
      this.loading.manual = true;
      try {
        const { data } = await scoreApi.searchUsers(q);
        this.manualUser = data.length ? data[0] : null;
      } finally {
        this.loading.manual = false;
      }
    },
    async manualAdjust({ user_id, points, reason }) {
      await scoreApi.manualAdjust({ user_id, points, reason });
      await this.fetchUserScores();
    },

    // 违规记录审核（管理员端）
    async fetchViolations() {
      this.loading.violations = true;
      try {
        const { data } = await scoreApi.getViolations();
        this.violations = data;
      } finally {
        this.loading.violations = false;
      }
    },
    async approveViolation(id) {
      await scoreApi.approveViolation(id);
      this.fetchViolations();
    },
    async rejectViolation(id) {
      await scoreApi.rejectViolation(id);
      this.fetchViolations();
    },
  },
});
