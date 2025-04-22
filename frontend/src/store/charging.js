// src/stores/charging.js
import { defineStore } from 'pinia'
import {
  getLocations,
  getChargingPiles,
  reserveSession,
  startSession,
  stopSession
} from '../api/charging'

export const useChargingStore = defineStore('charging', {
  state: () => ({
    locations: [],         // 充电区列表
    piles: [],             // 当前选中充电区的桩列表
    loadingLocations: false,
    loadingPiles: false,
  }),
  actions: {
    async fetchLocations() {
      this.loadingLocations = true
      try {
        const { data } = await getLocations()
        this.locations = data
      } finally {
        this.loadingLocations = false
      }
    },
    async fetchPiles(locationId) {
      this.loadingPiles = true
      try {
        const { data } = await getChargingPiles(locationId)
        this.piles = data
      } finally {
        this.loadingPiles = false
      }
    },
    async reservePile(userId, pileId) {
      await reserveSession(userId, pileId)
      // 刷新列表
      const loc = this.currentLocation
      if (loc) await this.fetchPiles(loc)
    },
    async startCharging(sessionId) {
      await startSession(sessionId)
      const loc = this.currentLocation
      if (loc) await this.fetchPiles(loc)
    },
    async stopCharging(sessionId) {
      await stopSession(sessionId)
      const loc = this.currentLocation
      if (loc) await this.fetchPiles(loc)
    }
  },
  getters: {
    currentLocation: (state) => state.selectedLocation,
  },
  // 临时存放一下当前选中充电区 id
  // 也可以把 selectedLocation 放到组件里
  selectedLocation: null
})
