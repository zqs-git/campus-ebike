// src/api/score.js
import axios from 'axios';

// 创建 axios 实例
const api = axios.create({
  baseURL: 'http://localhost:5000/api',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
});

// 积分规则
export const getRules = () => api.get('/score/rules');
export const createRule = data => api.post('/score/rules', data);
export const updateRule = (id, data) => api.put(`/score/rules/${id}`, data);
export const deleteRule = id => api.delete(`/score/rules/${id}`);

// 自动加减分日志
export const getAutoLogs = () => api.get('/score/auto-logs');

// —— 新增：学生端上报 —— 
export function createReport(form) {
  return api.post('/score/reports', form);
}

// 上报事件审核
export const getPendingReports = () => api.get('/score/reports/pending');
export const approveReport = (id, points) =>
  api.post(`/score/reports/${id}/approve`, { points });
export const rejectReport = id => api.post(`/score/reports/${id}/reject`);

// —— 新增：学生端申诉 —— 
export function createAppeal(form) {
  return api.post('/score/appeals', form);
}

// 扣分申诉管理
export const getAppeals = () => api.get('/score/appeals');
export function handleAppeal(id, payload) {
  return api.post(`/score/appeals/${id}`, payload);
}

// 手动加减分
export const searchUsers = q => api.get('/score/users/search', { params: { q } });
export const manualAdjust = payload => api.post('/score/adjust', payload);

// 违规记录审核
export const getViolations = () => api.get('/score/violations/pending');
export const approveViolation = id => api.post(`/score/violations/${id}/approve`);
export const rejectViolation = id => api.post(`/score/violations/${id}/reject`);

// 获取用户积分列表
export const getUserScores = () => api.get('/score/users/scores')
// 获取某用户的明细日志
export const getUserLogs   = (userId) => api.get(`/score/users/${userId}/logs`)

// —— 以下是“模拟违规”专用 —— 
// 单条模拟
export const simulateViolation = payload =>api.post('/violations/simulate', payload);
// 批量模拟
export const simulateBatchViolations = ({ count, useOnlyRealUsers }) =>api.post('/violations/simulate/batch', { count, useOnlyRealUsers });