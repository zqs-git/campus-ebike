// src/stores/charging.js
import { defineStore } from 'pinia'
import {
  getLocations,
  getChargingPiles,
  getPileSlots,
  reserveSession,
  cancelSession,
  startSession,
  stopSession
} from '../api/charging'

export const useChargingStore = defineStore('charging', {
  state: () => ({
    locations: [],              // 充电区列表
    piles: [],                  // 当前选中充电区的桩列表
    slots: {},                  // 各桩的时段预约状态
    loading: {
      locations: false,
      piles: false,
      slots: false,
      reserve: false,
      cancel: false,
    },
    sessionId: null,
    selectedLocation: null,
  }),
  getters: {
    currentLocation: state => state.selectedLocation,
    getSessionId: state => state.sessionId,
    // 获取某桩的时段列表
    getSlotsByPile: state => pileId => state.slots[pileId] || []
  },
  actions: {
    setSessionId(id) {
      this.sessionId = id
    },
    // 拉取充电区
    async fetchLocations() {
      this.loading.locations = true
      try {
        const { data } = await getLocations()
        this.locations = data
      } finally {
        this.loading.locations = false
      }
    },
    // 拉取桩列表
    async fetchPiles(locationId) {
      this.loading.piles = true
      try {
        const { data } = await getChargingPiles(locationId)
        this.piles = data
      } finally {
        this.loading.piles = false
      }
    },
    // 拉取某桩的时段预约状态
    async fetchPileSlots(pileId, date, userId = null) {
      this.loading.slots = true
      try {
        const { data } = await getPileSlots(pileId, date, userId)
        this.slots = { ...this.slots, [pileId]: data }
      } finally {
        this.loading.slots = false
      }
    },
    // 预约指定时段
    async reservePile(userId, pileId, vehicleId, date, slot) {
      this.loading.reserve = true
      try {
        const res = await reserveSession(userId, pileId, vehicleId, date, slot)
        if (res.data && res.data.session_id) {
          this.sessionId = res.data.session_id
        }
        // 刷新时段与桩状态
        if (this.selectedLocation) {
          await this.fetchPileSlots(pileId, date, userId)
          await this.fetchPiles(this.selectedLocation)
        }
        return res
      } finally {
        this.loading.reserve = false
      }
    },
    // 取消预约
    async cancelReservation(sessionId, pileId, date,userId) {
      this.loading.cancel = true
      try {
        await cancelSession(sessionId)
        // 刷新时段
        if (pileId && date) {
          await this.fetchPileSlots(pileId, date, userId)
        }
      } finally {
        this.loading.cancel = false
      }
    },
    // 开始充电
    async startCharging(sessionId) {
      await startSession(sessionId)
      if (this.selectedLocation) {
        await this.fetchPiles(this.selectedLocation)
      }
    },
    // 停止充电
    async stopCharging(sessionId) {
      await stopSession(sessionId)
      // 停止后清除 sessionId
      this.sessionId = null
      if (this.selectedLocation) {
        await this.fetchPiles(this.selectedLocation)
      }
    }
  }
})
