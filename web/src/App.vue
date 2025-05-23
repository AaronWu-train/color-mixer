<template>
  <el-container style="height: 100vh">
    <!-- 頂部導覽 -->
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

    <!-- 主要內容 -->
    <el-main class="main-content">
      <!-- Server Status 卡片 -->
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
                <el-button size="default" @click="toggleSensor" :disabled="mixingActive">
                  {{ sensorActive ? '停止' : '啟動' }}
                </el-button>
              </div>
            </template>
            <div class="color-block" :style="{ backgroundColor: sensorColor }"></div>
          </el-card>
        </el-col>

        <!-- 套用按鈕 -->
        <el-col :span="1" class="arrow-col">
          <el-button circle @click="applyColor" :disabled="mixingActive">
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
              <el-color-picker v-model="targetColor" size="default" color-format="rgb" />
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 開始混色按鈕 -->
      <el-row type="flex" justify="center" align="middle" class="mix-row">
        <el-button type="primary" size="large" @click="toggleMix">
          {{ mixingActive ? '停止' : '開始混色' }}
        </el-button>
      </el-row>
    </el-main>
  </el-container>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { Refresh, ArrowRight } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// --- 狀態宣告 ---
const WS_BASE = ref(import.meta.env.VITE_WS_BASE_URL)
const activeMenu = ref('home')
const sensorActive = ref(false)
const sensorColor = ref('rgb(255, 255, 255)')
const targetColor = ref('rgb(255, 255, 255)')
const statusState = ref('idle')
const statusMessage = ref('No additional message.')
const mixingActive = ref(false)

// WebSocket 實例
let wsColor = null
let wsStatus = null

// --- Computed ---
const tagType = computed(() => {
  switch (statusState.value) {
    case 'idle':
      return 'success'
    case 'finished':
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

// --- 工具函式 ---
const rgbStrToArray = (rgbString) => {
  const nums = rgbString.match(/\d+/g).map(Number)
  return nums.length === 3 ? nums : [0, 0, 0]
}

const rgbArrayToStr = (rgbArrayStr) => {
  const rgbArray = JSON.parse(rgbArrayStr)
  return `rgb(${rgbArray[0]}, ${rgbArray[1]}, ${rgbArray[2]})`
}

// --- WebSocket & HTTP 方法 ---
// 取得並更新伺服器狀態
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

// 建立狀態進度 WebSocket
const startStatusWebsocket = () => {
  wsStatus?.close()
  wsStatus = new WebSocket(`${WS_BASE.value}/ws/status`)
  console.log('Starting status WebSocket...')
  console.log('WebSocket URL:', `${WS_BASE.value}/ws/status`)

  wsStatus.onmessage = (e) => {
    console.log('Received status:', e.data)
    const data = JSON.parse(e.data)
    statusState.value = data.state
    statusMessage.value = data.message || 'No additional message.'
    if (data.state === 'finished') {
      mixingActive.value = false
      ElMessage({
        message: 'Mixing finished successfully!',
        type: 'success',
      })
    } else if (data.state === 'error') {
      mixingActive.value = false
      ElMessage({
        message: 'Mixing error occurred!',
        type: 'error',
      })
    } else if (data.state === 'idle') {
      mixingActive.value = false
    }
  }
  wsStatus.onclose = () => {
    mixingActive.value = false
  }
}

// 建立感測器顏色 WebSocket
const startSensorWebsocket = () => {
  wsColor?.close()
  wsColor = new WebSocket(`${WS_BASE.value}/ws/color`)
  console.log('Starting sensor WebSocket...')
  console.log('WebSocket URL:', `${WS_BASE.value}/ws/color`)
  wsColor.onmessage = (e) => {
    console.log('Received color:', e.data)
    sensorColor.value = rgbArrayToStr(e.data)
  }
  wsColor.onclose = () => {
    sensorActive.value = false
    ElMessage({
      message: 'Sensor WebSocket closed.',
      type: 'info',
    })
  }
}

// --- 動作函式 ---
// 切換感測器
const toggleSensor = () => {
  sensorActive.value
    ? wsColor?.close() && (sensorActive.value = false)
    : ((sensorActive.value = true), startSensorWebsocket())
}

// 將感測器顏色套用到目標
const applyColor = () => {
  targetColor.value = sensorColor.value
}

// 重設目標顏色
const resetTarget = () => {
  targetColor.value = '#ffffff'
}

// 切換混色狀態
const toggleMix = () => {
  mixingActive.value ? stopMix() : startMix()
}

// 開始混色流程
const startMix = async () => {
  await axios
    .post('/mix', {
      target: rgbStrToArray(targetColor.value),
      message: null,
    })
    .then((response) => {
      statusState.value = response.data.state
      statusMessage.value = response.data.message
      ElMessage({
        message: 'Mixing started successfully!',
        type: 'success',
      })
      mixingActive.value = true
    })
    .catch((err) => {
      console.error('Error starting mix:', err)
      ElMessage({
        message: 'Error starting mix: ' + err,
        type: 'error',
      })
    })
}

// 停止混色流程
const stopMix = async () => {
  await axios
    .post('/reset')
    .then(() => {
      ElMessage({
        message: 'Mixing stopped.',
        type: 'info',
      })
      mixingActive.value = false
    })
    .err((err) => {
      console.error('Error:', err)
      ElMessage({
        message: 'Error: ' + err,
        type: 'error',
      })
    })
}

// 切換導覽列選項
const handleMenuSelect = (index) => {
  activeMenu.value = index
}

// --- 生命周期 ---
onMounted(() => {
  // 初次載入時可啟動狀態檢查
  fetchStatus()
  startStatusWebsocket()
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
  border: 1px solid #a4a4a4;
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
  margin: 20px auto;
  padding: 20px;
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
  margin: 60px 0 20px;
}
</style>
