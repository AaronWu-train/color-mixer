<template>
  <el-container style="height: 100vh">
    <!-- 頂部導覽列 -->
    <el-header>
      <el-menu
        :default-active="activeMenu"
        mode="horizontal"
        @select="handleMenuSelect"
        background-color="transparent"
        text-color="#303133"
        active-text-color="#409EFF"
      >
        <el-menu-item index="home">Color Mixer</el-menu-item>
      </el-menu>
    </el-header>

    <!-- 主內容區 -->
    <el-main class="main-content">
      <!-- 伺服器狀態卡片 -->
      <el-card class="status-card">
        <el-row class="status-header" type="flex" justify="center" align="middle">
          <el-col :span="6">
            <span class="status-title">Server Status:</span>
          </el-col>
          <el-col :span="16">
            <el-tag :type="tagType">{{ statusState }}</el-tag>
          </el-col>
          <el-col :span="2">
            <el-button size="default" circle @click="fetchStatus">
              <el-icon><Refresh /></el-icon>
            </el-button>
          </el-col>
        </el-row>
        <el-row type="flex" justify="center" align="middle">
          <el-input v-model="statusMessage" readonly placeholder="狀態訊息" style="width: 100%" />
        </el-row>
      </el-card>

      <el-row type="flex" justify="center" align="middle" :gutter="30">
        <!-- Sensor Color 卡片 -->
        <el-col :span="6">
          <el-card class="card">
            <template #header>
              <div class="card-header">
                <span>Sensor Color</span>
                <el-button size="default" @click="toggleSensor">
                  {{ sensorActive ? '停止' : '啟動' }}
                </el-button>
              </div>
            </template>
            <div class="color-block" :style="{ backgroundColor: sensorColor }"></div>
          </el-card>
        </el-col>

        <!-- 套用按鈕與標籤 -->
        <el-col :span="1" class="arrow-col">
          <el-button circle @click="applyColor">
            <el-icon><ArrowRight /></el-icon>
          </el-button>
        </el-col>

        <!-- Target Color 卡片 -->
        <el-col :span="6">
          <el-card class="card">
            <template #header>
              <div class="card-header">
                <span>Target Color</span>
                <el-button size="default" @click="resetTarget">重設</el-button>
              </div>
            </template>
            <div class="color-block" :style="{ backgroundColor: targetColor }"></div>
            <div class="picker-wrapper">
              <el-color-picker v-model="targetColor" size="default" />
            </div>
          </el-card>
        </el-col>
      </el-row>
      <el-row type="flex" justify="center" align="middle" class="mix-row">
        <el-button type="primary" size="large" @click="startMix" :disabled="mixingActive">
          開始混色
        </el-button>
      </el-row>
    </el-main>
  </el-container>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { Refresh } from '@element-plus/icons-vue'

// 導覽列目前選中項目
const activeMenu = ref('home')
const handleMenuSelect = (index) => {
  activeMenu.value = index
}

// 感測器狀態與顏色
const sensorActive = ref(false)
const sensorColor = ref('#ffffff')

// 目標顏色
const targetColor = ref('#ffffff')

const statusState = ref('idle')
const statusMessage = ref('No additional message.')
const mixingActive = ref(false)

// WebSocket 實例
let wsColor = null
let wsStatus = null

// 啟動或停止感測器
const toggleSensor = () => {
  if (sensorActive.value) {
    wsColor?.close()
    sensorActive.value = false
  } else {
    sensorActive.value = true
    startSensorWebsocket()
  }
}

// 建立 WebSocket 連線以接收感測器顏色
const startSensorWebsocket = () => {
  wsColor?.close()
  wsColor = new WebSocket(`ws://${window.location.host}/ws/color`)
  wsColor.onmessage = (event) => {
    sensorColor.value = event.data
  }
  wsColor.onclose = () => {
    sensorActive.value = false
  }
}

const hexToRgbArray = (hex) => {
  const pairs = hex.replace('#', '').match(/.{2}/g) || []
  return pairs.map((p) => parseInt(p, 16))
}

const startStatusWebsocket = () => {
  wsStatus?.close()
  wsStatus = new WebSocket(`ws://${window.location.host}/ws/status`)
  wsStatus.onmessage = (event) => {
    const data = JSON.parse(event.data)
    statusState.value = data.state
    statusMessage.value = data.message || 'No additional message.'
    if (data.state === 'idle') {
      wsStatus.close()
    }
  }
  wsStatus.onclose = () => {
    mixingActive.value = false
  }
}

// 套用感測器顏色到目標
const applyColor = () => {
  targetColor.value = sensorColor.value
}

// 重設目標顏色
const resetTarget = () => {
  targetColor.value = '#ffffff'
}

const startMix = async () => {
  mixingActive.value = true
  const payload = { target: hexToRgbArray(targetColor.value), message: null }
  await axios.post('/mix', payload)
  startStatusWebsocket()
}

// 請求並更新伺服器狀態
const fetchStatus = async () => {
  try {
    const res = await axios.get('/status')
    statusState.value = res.data.state
    statusMessage.value = res.data.message || 'No additional message.'
  } catch {
    statusState.value = 'error'
    statusMessage.value = '錯誤'
  }
}

const tagType = computed(() => {
  switch (statusState.value) {
    case 'idle':
      return 'success'
    case 'running':
      return 'info'
    case 'accepted':
      return 'warning'
    case 'error':
      return 'danger'
    default:
      return 'info'
  }
})

// 初次載入時獲取伺服器狀態
onMounted(() => {
  // fetchStatus()
})
</script>

<style scoped>
.card {
  max-width: 300px;
  height: 325px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.color-block {
  width: 100%;
  height: 160px;
  border-radius: 4px;
  border: 1px solid #ebeef5;
  margin: 10px 0;
}

.arrow-col {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.picker-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 10px;
}

.main-content {
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  flex: 1;
  min-height: 0;
}
.status-card {
  width: 600px;
  height: max-content;
  margin: 20px auto;
  padding: 20px;
  margin-top: 20px; /* ensure spacing below header */
}
.status-header {
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.status-title {
  margin-right: 10px;
  font-weight: 600;
}

.mix-row {
  margin-top: 60px;
  margin-bottom: 20px;
}
</style>
