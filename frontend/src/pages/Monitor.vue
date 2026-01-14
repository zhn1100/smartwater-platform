<template>
  <div class="monitor-container" :class="{ 'fullscreen': isFullscreen }">
    <!-- Cesium 3D视图 -->
    <div ref="viewerEl" class="cesium-viewer"></div>
    
    <!-- 顶部标题栏 -->
    <div class="top-bar">
      <div class="title-section">
        <h1>智慧水利大坝安全监测平台</h1>
        <p class="subtitle">实时监测 · 三维可视化 · 数据分析</p>
      </div>
      <div class="user-section">
        <div class="user-info">
          <el-avatar :size="36" :src="userAvatar" />
          <div class="user-details">
            <div class="username">{{ userInfo.name || userInfo.username }}</div>
            <div class="user-role">{{ userInfo.role === 'admin' ? '管理员' : '普通用户' }}</div>
          </div>
          <el-button type="primary" size="small" @click="goToAdmin" v-if="isAdmin">后台管理</el-button>
          <el-button size="small" @click="handleLogout">退出</el-button>
        </div>
        <div class="time-display">
          <div class="current-time">{{ currentTime }}</div>
          <div class="current-date">{{ currentDate }}</div>
        </div>
      </div>
    </div>
    
    <!-- 左侧浮动窗口：监测概览（使用dataV边框） -->
    <dv-border-box-8 class="floating-window left-window overview-window" :class="{ 'collapsed': isOverviewCollapsed }">
      <div class="window-header">
        <h3><i class="el-icon-monitor"></i> 监测概览</h3>
        <div class="window-controls">
          <el-button size="small" @click="refreshData">
            <i class="el-icon-refresh"></i>
            刷新
          </el-button>
          <el-button size="small" @click="isOverviewCollapsed = !isOverviewCollapsed">
            <i :class="isOverviewCollapsed ? 'el-icon-full-screen' : 'el-icon-crop'">
            </i>
            {{ isOverviewCollapsed ? '展开' : '收起' }}
          </el-button>
        </div>
      </div>
      <div class="window-content" v-show="!isOverviewCollapsed">
        <!-- 使用dataV数字翻牌器 -->
        <div class="stats-grid">
          <div class="stat-item">
            <dv-digital-flop :config="totalMeasurementsConfig" />
            <div class="stat-label">总测量记录</div>
          </div>
          <div class="stat-item">
            <dv-digital-flop :config="instrumentCountConfig" />
            <div class="stat-label">监测仪器</div>
          </div>
          <div class="stat-item">
            <dv-digital-flop :config="typeCountConfig" />
            <div class="stat-label">监测类型</div>
          </div>
          <div class="stat-item">
            <dv-digital-flop :config="timeRangeConfig" />
            <div class="stat-label">最新数据年度</div>
          </div>
        </div>
        
        <div class="monitoring-types">
          <h4>监测类型分布</h4>
          <dv-active-ring-chart :config="typeChartConfig" class="chart-container" />
        </div>
        
        <div class="additional-charts">
          <div class="chart-section">
            <div class="chart-header">
              <h4>上游水位变化趋势</h4>
              <div class="chart-controls">
                <el-select v-model="upstreamYear" placeholder="年份" size="small" style="width: 100px;">
                  <el-option label="2018" value="2018" />
                  <el-option label="2019" value="2019" />
                  <el-option label="2020" value="2020" />
                  <el-option label="2021" value="2021" />
                  <el-option label="2022" value="2022" />
                  <el-option label="2023" value="2023" />
                  <el-option label="2024" value="2024" />
                </el-select>
              </div>
            </div>
            <div ref="upstreamChartEl" class="chart-container"></div>
          </div>
          
          <div class="chart-section">
            <div class="chart-header">
              <h4>下游水位变化趋势</h4>
              <div class="chart-controls">
                <el-select v-model="downstreamYear" placeholder="年份" size="small" style="width: 100px;">
                  <el-option label="2018" value="2018" />
                  <el-option label="2019" value="2019" />
                  <el-option label="2020" value="2020" />
                  <el-option label="2021" value="2021" />
                  <el-option label="2022" value="2022" />
                  <el-option label="2023" value="2023" />
                  <el-option label="2024" value="2024" />
                </el-select>
              </div>
            </div>
            <div ref="downstreamChartEl" class="chart-container"></div>
          </div>
        </div>
      </div>
    </dv-border-box-8>
    
    <!-- 右侧浮动窗口：测点数据（使用dataV边框） -->
    <dv-border-box-10 class="floating-window right-window points-window" :class="{ 'collapsed': isPointsCollapsed }">
      <div class="window-header">
        <h3><i class="el-icon-location-information"></i> 测点数据</h3>
        <div class="window-controls">
          <el-select v-model="selectedPointType" placeholder="类型筛选" size="small" style="width: 100px;">
            <el-option label="全部" value="all" />
            <el-option v-for="type in monitoringTypes" :key="type.id" :label="type.name" :value="type.id" />
          </el-select>
          <el-button size="small" @click="isPointsCollapsed = !isPointsCollapsed">
            <i :class="isPointsCollapsed ? 'el-icon-full-screen' : 'el-icon-crop'">
            </i>
            {{ isPointsCollapsed ? '展开' : '收起' }}
          </el-button>
        </div>
      </div>
      <div class="window-content" v-show="!isPointsCollapsed">
        <div class="points-list">
          <div 
            v-for="point in filteredPoints" 
            :key="point.id"
            class="point-item"
            :class="{ 'active': selectedPointId === point.id }"
            @click="selectPoint(point)"
          >
            <div class="point-info">
              <div class="point-name">{{ point.name }}</div>
              <div class="point-details">
                <span class="point-type">{{ point.type_name }}</span>
                <span class="point-instrument">仪器: {{ point.instrument_id }}</span>
              </div>
            </div>
            <div class="point-value">
              <div class="value">{{ point.latest_value?.toFixed(2) || '--' }}</div>
              <div class="unit">{{ point.unit || '' }}</div>
            </div>
          </div>
        </div>
        
        <div v-if="selectedPoint" class="point-detail">
          <!-- 第一张表：最新一个月/一年数据线（有选项卡） -->
          <div class="dynamic-chart">
            <div class="chart-header">
              <h4>最新数据趋势</h4>
              <div class="chart-controls">
                <el-radio-group v-model="trendTimeRange" size="small">
                  <el-radio-button label="month">一个月</el-radio-button>
                  <el-radio-button label="year">一年</el-radio-button>
                </el-radio-group>
              </div>
            </div>
            <div ref="trendChartEl" class="chart-container" style="height: 200px;"></div>
          </div>
          
          <!-- 第二张表：18-24年仪器使用记录 -->
          <div class="dynamic-chart">
            <div class="chart-header">
              <h4>仪器使用记录（2018-2024年）</h4>
            </div>
            <div ref="usageChartEl" class="chart-container" style="height: 200px;"></div>
          </div>
          
          <!-- 历史数据部分：包含表格和导出功能 -->
          <div class="historical-data-section">
            <div class="section-header">
              <h4>历史数据</h4>
              <div class="section-controls">
                <el-button size="small" @click="exportData" type="primary">
                  <i class="el-icon-download"></i>
                  导出CSV
                </el-button>
              </div>
            </div>
            
            <!-- 最近二十条数据表格 -->
            <div class="measurements-table">
              <el-table :data="pointMeasurements" size="small" height="200">
                <el-table-column prop="measure_time" label="测量时间" width="150" />
                <el-table-column prop="type_name" label="监测类型" width="100" />
                <el-table-column prop="instrument_id" label="仪器编号" width="100" />
                <el-table-column prop="value" label="测量值" width="100">
                  <template #default="{ row }">
                    {{ row.value.toFixed(2) }} {{ row.unit }}
                  </template>
                </el-table-column>
                <el-table-column prop="water_level" label="水位值" width="100">
                  <template #default="{ row }">
                    {{ row.water_level ? row.water_level.toFixed(2) : '--' }}
                  </template>
                </el-table-column>
              </el-table>
              <div class="table-footer">
                共 {{ pointMeasurements.length }} 条记录，显示最近20条
              </div>
            </div>
          </div>
        </div>
      </div>
    </dv-border-box-10>
    
    <!-- 底部浮动窗口：最新数据（使用dataV边框） -->
    <dv-border-box-12 class="floating-window bottom-window latest-data-window" :class="{ 'collapsed': isLatestDataCollapsed }">
      <div class="window-header">
        <h3><i class="el-icon-s-data"></i> 最新监测数据</h3>
        <div class="window-controls">
          <el-button size="small" @click="isLatestDataCollapsed = !isLatestDataCollapsed">
            <i :class="isLatestDataCollapsed ? 'el-icon-full-screen' : 'el-icon-crop'">
            </i>
            {{ isLatestDataCollapsed ? '展开' : '收起' }}
          </el-button>
        </div>
      </div>
      <div class="window-content" v-show="!isLatestDataCollapsed">
        <div class="scroll-board-container">
          <dv-scroll-board :config="scrollBoardConfig" />
        </div>
      </div>
    </dv-border-box-12>
    
    <!-- 模型控制窗口（使用dataV边框） -->
    <dv-border-box-13 class="floating-window model-control-window" :class="{ 'collapsed': isModelControlCollapsed }">
      <div class="window-header">
        <h3><i class="el-icon-map-location"></i> 模型控制</h3>
        <div class="window-controls">
          <el-button size="small" @click="isModelControlCollapsed = !isModelControlCollapsed">
            <i :class="isModelControlCollapsed ? 'el-icon-full-screen' : 'el-icon-crop'">
            </i>
            {{ isModelControlCollapsed ? '展开' : '收起' }}
          </el-button>
        </div>
      </div>
      <div class="window-content" v-show="!isModelControlCollapsed">
        <div class="model-controls">
          <el-select v-model="selectedModel" placeholder="选择模型" size="small" @change="switchModel">
            <el-option label="大坝模型1 (dam1.glb)" value="dam1" />
            <el-option label="大坝模型2 (dam2.glb)" value="dam2" />
            <el-option label="大坝模型3 (dam3.glb)" value="dam3" />
          </el-select>
          <el-button size="small" @click="resetView">重置视角</el-button>
          <el-button size="small" @click="toggleFullscreen">
            <i class="el-icon-full-screen"></i>
            全屏
          </el-button>
        </div>
        <div class="model-info">
          <div class="info-item">
            <span class="label">当前模型：</span>
            <span class="value">{{ modelNames[selectedModel] }}</span>
          </div>
          <div class="info-item">
            <span class="label">模型格式：</span>
            <span class="value">{{ modelFormats[selectedModel] }}</span>
          </div>
        </div>
        
        <!-- dam3模型分块交互信息 -->
        <div v-if="selectedModel === 'dam3'" class="block-interaction-info">
          <div class="info-section">
            <h4><i class="el-icon-mouse"></i> 分块交互</h4>
            <div class="info-item">
              <span class="label">悬停分块：</span>
              <span class="value" :class="{ 'highlight': hoveredBlock }">
                {{ hoveredBlock || '无' }}
              </span>
            </div>
            <div class="info-item">
              <span class="label">选中分块：</span>
              <span class="value" :class="{ 'highlight': selectedBlock }">
                {{ selectedBlock || '无' }}
              </span>
            </div>
            <div v-if="selectedInstrumentIdFromBlock" class="info-item">
              <span class="label">对应仪器：</span>
              <span class="value instrument-id">
                {{ selectedInstrumentIdFromBlock }}
              </span>
            </div>
            <div class="interaction-hint">
              <i class="el-icon-info"></i>
              提示：鼠标悬停可高亮分块，点击分块可查看对应测点数据
            </div>
          </div>
        </div>
      </div>
    </dv-border-box-13>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onBeforeUnmount, computed, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as Cesium from 'cesium'
import * as echarts from 'echarts'
import { logout, getCurrentUser, isAdmin } from '../api/auth.js'
import { 
  getStatistics, 
  getMeasurements, 
  getMonitoringTypes,
  getInstruments,
  getMeasurementsSummary
} from '../api/monitoring_new.js'

// 导入dataV组件
import {
  BorderBox8,
  BorderBox10,
  BorderBox12,
  BorderBox13,
  DigitalFlop,
  ActiveRingChart,
  ScrollRankingBoard,
  ScrollBoard
} from '@kjgl77/datav-vue3'

const router = useRouter()
const viewerEl = ref(null)

// 用户信息
const userInfo = ref({})
const userAvatar = computed(() => {
  return `https://api.dicebear.com/7.x/avataaars/svg?seed=${userInfo.value.username || 'user'}`
})

// 模型配置
const selectedModel = ref('dam1')
const modelNames = {
  dam1: '大坝模型1',
  dam2: '大坝模型2',
  dam3: '大坝模型3'
}
const modelFormats = {
  dam1: 'GLB格式',
  dam2: 'GLB格式',
  dam3: 'GLB格式'
}

// 数据状态
const statistics = ref({})
const monitoringTypes = ref([])
const instruments = ref([])
const latestMeasurements = ref([])
const selectedPointType = ref('all')
const selectedPointId = ref(null)
const selectedPoint = ref(null)
const pointMeasurements = ref([])
const isFullscreen = ref(false)

// 窗口状态控制
const isOverviewCollapsed = ref(false)
const isPointsCollapsed = ref(false)
const isLatestDataCollapsed = ref(false)
const isModelControlCollapsed = ref(false)

// 新增图表相关
const upstreamYear = ref('2024')
const downstreamYear = ref('2024')
const trendTimeRange = ref('month') // month 或 year
const upstreamChartEl = ref(null)
const downstreamChartEl = ref(null)
const trendChartEl = ref(null)
const usageChartEl = ref(null)
let upstreamChart = null
let downstreamChart = null
let trendChart = null
let usageChart = null

// 时间显示
const currentTime = ref('')
const currentDate = ref('')

// dataV配置
const totalMeasurementsConfig = reactive({
  number: [0],
  content: '{nt}',
  style: {
    fontSize: 24,
    fill: '#fff',
    fontWeight: 'bold'
  },
  formatter: (number) => {
    return number.toLocaleString()
  }
})

const instrumentCountConfig = reactive({
  number: [0],
  content: '{nt}',
  style: {
    fontSize: 24,
    fill: '#fff',
    fontWeight: 'bold'
  }
})

const typeCountConfig = reactive({
  number: [0],
  content: '{nt}',
  style: {
    fontSize: 24,
    fill: '#fff',
    fontWeight: 'bold'
  }
})

const timeRangeConfig = reactive({
  number: [0],
  content: '{nt}',
  style: {
    fontSize: 18,
    fill: '#fff',
    fontWeight: 'bold'
  },
  formatter: (number) => {
    return '2024-2025'
  }
})

const typeChartConfig = reactive({
  data: [],
  digitalFlopStyle: {
    fontSize: 14
  },
  color: ['#5B8FF9', '#5AD8A6', '#F6BD16', '#6F5EF9', '#E86452', '#945FB9', '#FF9845', '#1E9493'],
  showOriginValue: true
})

const rankingBoardConfig = reactive({
  data: [],
  rowNum: 5,
  waitTime: 3000,
  carousel: 'single',
  unit: 'mm'
})

const scrollBoardConfig = reactive({
  data: [],
  header: ['测量时间', '监测类型', '仪器编号', '测量值'],
  headerBGC: 'rgba(11, 25, 55, 0.9)',
  oddRowBGC: 'rgba(11, 25, 55, 0.7)',
  evenRowBGC: 'rgba(16, 36, 78, 0.7)',
  headerHeight: 40,
  rowNum: 5,
  columnWidth: [120, 80, 70, 70], // 进一步减少列宽以适应更窄的容器
  align: ['center', 'center', 'center', 'center']
})

// 导入模型映射配置
import { 
  getInstrumentIdFromBlockName, 
  getBlockNamesFromInstrumentId 
} from '../config/model-mapping.js'

// Cesium相关
let viewer = null
let currentModelEntity = null
let pointEntities = new Map()

// 模型分块交互相关
const hoveredBlock = ref('')
const selectedBlock = ref('')
const selectedInstrumentIdFromBlock = ref('')
const highlightedComponent = ref('')
let mouseMoveHandler = null
let clickHandler = null
let highlightedFeature = null

// 计算属性
const filteredPoints = computed(() => {
  if (selectedPointType.value === 'all') {
    return instruments.value
  }
  return instruments.value.filter(point => point.type_id == selectedPointType.value)
})

// 方法
const updateTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('zh-CN')
  currentDate.value = now.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long'
  })
}

const goToAdmin = () => {
  router.push('/admin')
}

const handleLogout = async () => {
  try {
    await logout()
    router.push('/login')
  } catch (error) {
    console.error('登出失败:', error)
  }
}

const refreshData = async () => {
  try {
    await Promise.all([
      loadStatistics(),
      loadMonitoringTypes(),
      loadInstruments(),
      loadLatestMeasurements()
    ])
    ElMessage.success('数据已刷新')
  } catch (error) {
    console.error('刷新数据失败:', error)
    ElMessage.error('刷新数据失败')
  }
}

const loadStatistics = async () => {
  try {
    statistics.value = await getStatistics()
    
    // 更新dataV配置
    totalMeasurementsConfig.number = [statistics.value.total_measurements || 0]
    instrumentCountConfig.number = [statistics.value.instrument_count || 0]
    
    // 从type_statistics数组长度获取监测类型数量
    const typeCount = statistics.value.type_statistics ? statistics.value.type_statistics.length : 0
    typeCountConfig.number = [typeCount]
    
    // 更新类型分布图表
    if (statistics.value.type_statistics) {
      typeChartConfig.data = statistics.value.type_statistics.map(item => ({
        name: item.name,
        value: item.count
      }))
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
    // 如果API失败，显示空数据
    totalMeasurementsConfig.number = [0]
    instrumentCountConfig.number = [0]
    typeCountConfig.number = [0]
    typeChartConfig.data = []
  }
}

const loadMonitoringTypes = async () => {
  try {
    monitoringTypes.value = await getMonitoringTypes()
  } catch (error) {
    console.error('加载监测类型失败:', error)
  }
}

const loadInstruments = async () => {
  try {
    // 1. 获取仪器列表
    const instrumentData = await getInstruments()
    
    // 2. 一次性获取250条最新数据（按时间逆序）
    const latestMeasurements = await getMeasurements({
      limit: 250,
      order_by: 'measure_time desc'
    })
    
    // 3. 创建仪器映射，用于快速查找
    const instrumentMap = new Map()
    instrumentData.forEach(item => {
      instrumentMap.set(item.instrument_id, {
        id: instrumentMap.size + 1,
        instrument_id: item.instrument_id,
        name: `仪器 ${item.instrument_id}`,
        type_id: item.type_id,
        type_name: item.type_name,
        latest_value: null, // 初始化为null
        unit: item.unit || 'mm'
      })
    })
    
    // 4. 从最新数据中提取每个仪器的最新值
    const seenInstruments = new Set()
    for (const measurement of latestMeasurements) {
      const instrumentId = measurement.instrument_id
      
      // 如果这个仪器还没有设置最新值，并且存在于仪器列表中
      if (!seenInstruments.has(instrumentId) && instrumentMap.has(instrumentId)) {
        const instrument = instrumentMap.get(instrumentId)
        instrument.latest_value = measurement.value
        seenInstruments.add(instrumentId)
        
        // 如果所有仪器都找到了最新值，可以提前退出
        if (seenInstruments.size === instrumentMap.size) {
          break
        }
      }
    }
    
    // 5. 转换为数组并设置到响应式变量
    instruments.value = Array.from(instrumentMap.values())
    
    console.log(`加载了 ${instruments.value.length} 个仪器，其中 ${seenInstruments.size} 个有最新数据`)
  } catch (error) {
    console.error('加载仪器列表失败:', error)
    // 如果批量获取失败，回退到原始方法（只获取仪器列表，不获取最新值）
    try {
      const instrumentData = await getInstruments()
      instruments.value = instrumentData.map((item, index) => ({
        id: index + 1,
        instrument_id: item.instrument_id,
        name: `仪器 ${item.instrument_id}`,
        type_id: item.type_id,
        type_name: item.type_name,
        latest_value: null,
        unit: item.unit || 'mm'
      }))
    } catch (fallbackError) {
      console.error('回退方法也失败:', fallbackError)
    }
  }
}

const loadLatestMeasurements = async () => {
  try {
    const data = await getMeasurements({ limit: 10 })
    latestMeasurements.value = data
    
    // 更新滚动表格数据
    scrollBoardConfig.data = data.map(item => [
      item.measure_time,
      item.type_name,
      item.instrument_id,
      `${item.value.toFixed(2)} ${item.unit}`
    ])
  } catch (error) {
    console.error('加载最新数据失败:', error)
  }
}

const loadPointMeasurements = async (instrumentId) => {
  try {
    // 获取选定仪器的测量数据
    const point = instruments.value.find(p => p.instrument_id === instrumentId)
    if (!point) return
    
    // 获取最近20条数据
    const measurements = await getMeasurements({
      instrument_id: point.instrument_id,
      limit: 20
    })
    
    pointMeasurements.value = measurements
    
    // 更新排名板数据（显示前5条）
    rankingBoardConfig.data = measurements.slice(0, 5).map((item, index) => ({
      name: `测量${index + 1}`,
      value: item.value.toFixed(2)
    }))
    
    // 使用nextTick确保DOM更新完成后再初始化图表
    await nextTick()
    
    // 初始化仪器使用记录图表和趋势图表
    initInstrumentCharts(point.instrument_id)
  } catch (error) {
    console.error('加载测点数据失败:', error)
    // 如果API失败，显示空数据
    pointMeasurements.value = []
    rankingBoardConfig.data = []
    
    // 尝试初始化图表，如果point存在的话
    const point = instruments.value.find(p => p.instrument_id === instrumentId)
    if (point) {
      await nextTick()
      initInstrumentCharts(point.instrument_id)
    }
  }
}

const initInstrumentCharts = (pointId) => {
  // 初始化趋势图表
  if (trendChartEl.value) {
    if (trendChart) {
      trendChart.dispose()
    }
    trendChart = echarts.init(trendChartEl.value)
    renderTrendChart(pointId)
  }
  
  // 初始化仪器使用记录图表
  if (usageChartEl.value) {
    if (usageChart) {
      usageChart.dispose()
    }
    usageChart = echarts.init(usageChartEl.value)
    renderUsageChart(pointId)
  }
}

const renderUsageChart = async (pointId) => {
  if (!usageChart) return
  
  try {
    // 获取当前选中的测点信息，判断是否是水位类型
    const point = instruments.value.find(p => p.instrument_id === pointId)
    const isWaterLevel = point && (point.type_name === '水位' || point.instrument_id === '上游' || point.instrument_id === '下游')
    
    // 根据仪器类型设置不同的请求参数
    const limit = isWaterLevel ? 2562 : 400 // 水位类型请求2562条，其他类型请求400条
    
    // 一次性获取2018-2024年的所有数据
    const allData = await getMeasurements({
      instrument_id: pointId,
      limit: limit,
      order_by: 'measure_time desc' // 按时间逆序，获取最新数据
    })
    
    // 按年份统计数据量
    const years = ['2018', '2019', '2020', '2021', '2022', '2023', '2024']
    const yearData = {}
    
    // 初始化年份数据
    years.forEach(year => {
      yearData[year] = 0
    })
    
    // 统计每个年份的数据量
    allData.forEach(item => {
      const measureTime = new Date(item.measure_time)
      const year = measureTime.getFullYear().toString()
      
      if (yearData.hasOwnProperty(year)) {
        yearData[year]++
      }
    })
    
    // 准备图表数据
    const values = years.map(year => yearData[year])
    
    // 计算最大值，用于设置y轴范围
    const maxValue = Math.max(...values)
    
    // 设置合理的y轴最大值
    let yMax = 100 // 默认最大值
    if (maxValue > 0) {
      // 如果最大值超过100，设置更大的范围
      if (maxValue > 100) {
        yMax = Math.ceil(maxValue * 1.2) // 增加20%的余量
      } else {
        yMax = Math.ceil(maxValue * 1.1) // 增加10%的余量
      }
    }
    
    usageChart.setOption({
      title: {
        text: '仪器使用记录（2018-2024年）',
        left: 'center',
        textStyle: {
          fontSize: 12,
          color: '#a0cfff'
        }
      },
      tooltip: {
        trigger: 'axis',
        formatter: (params) => {
          const year = params[0].name
          const value = params[0].value
          return `${year}: ${value} 条记录`
        }
      },
      xAxis: {
        type: 'category',
        data: years.map(year => `${year}年`),
        axisLabel: {
          color: '#a0cfff'
        },
        axisLine: {
          lineStyle: {
            color: 'rgba(64, 158, 255, 0.3)'
          }
        }
      },
      yAxis: {
        type: 'value',
        name: '记录数量',
        nameTextStyle: {
          color: '#a0cfff'
        },
        axisLabel: {
          color: '#a0cfff'
        },
        axisLine: {
          lineStyle: {
            color: 'rgba(64, 158, 255, 0.3)'
          }
        },
        splitLine: {
          lineStyle: {
            color: 'rgba(64, 158, 255, 0.1)'
          }
        },
        min: 0,
        max: yMax
      },
      series: [{
        name: '使用记录',
        type: 'bar',
        data: values,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#F6BD16' },
            { offset: 1, color: '#E86452' }
          ])
        },
        label: {
          show: true,
          position: 'top',
          formatter: '{c}',
          color: '#fff'
        }
      }],
      grid: {
        left: '10%',
        right: '10%',
        bottom: '15%',
        top: '20%',
        containLabel: true
      }
    })
  } catch (error) {
    console.error('加载仪器使用记录失败:', error)
    // 如果API失败，显示空图表
    usageChart.setOption({
      title: {
        text: '仪器使用记录（2018-2024年）',
        subtext: '数据加载失败',
        left: 'center',
        textStyle: {
          fontSize: 12,
          color: '#a0cfff'
        }
      },
      xAxis: {
        type: 'category',
        data: [],
        axisLabel: {
          color: '#a0cfff'
        }
      },
      yAxis: {
        type: 'value',
        name: '记录数量',
        nameTextStyle: {
          color: '#a0cfff'
        },
        min: 0,
        max: 100
      },
      series: [{
        name: '使用记录',
        type: 'bar',
        data: []
      }]
    })
  }
}

const renderTrendChart = async (pointId) => {
  if (!trendChart) return
  
  try {
    if (trendTimeRange.value === 'month') {
      // 最新一个月数据趋势：获取30条最新数据，然后筛选最近一个月内的数据
      const recentData = await getMeasurements({
        instrument_id: pointId,
        limit: 30,
        order_by: 'measure_time desc'
      })
      
      // 如果没有数据，显示空图表
      if (!recentData || recentData.length === 0) {
        trendChart.setOption({
          title: {
            text: '最新一个月数据趋势',
            subtext: '暂无数据',
            left: 'center',
            textStyle: {
              fontSize: 12,
              color: '#a0cfff'
            }
          },
          xAxis: {
            type: 'category',
            data: [],
            axisLabel: {
              color: '#a0cfff'
            }
          },
          yAxis: {
            type: 'value',
            name: '测量值',
            nameTextStyle: {
              color: '#a0cfff'
            },
            min: 0,
            max: 100
          },
          series: [{
            name: '数据趋势',
            type: 'line',
            data: []
          }]
        })
        return
      }
      
      // 获取最后一个数据的时间（最新的数据）
      const lastDataTime = new Date(recentData[0].measure_time)
      
      // 计算一个月前的时间（相对于最后一个数据）
      const oneMonthAgo = new Date(lastDataTime)
      oneMonthAgo.setDate(lastDataTime.getDate() - 30)
      
      // 筛选离最后一个数据30天以内的数据
      const filteredData = recentData.filter(item => {
        const measureTime = new Date(item.measure_time)
        return measureTime >= oneMonthAgo
      })
      
      // 如果没有最近一个月的数据，显示空图表
      if (filteredData.length === 0) {
        trendChart.setOption({
          title: {
            text: '最新一个月数据趋势',
            subtext: '最近一个月内无数据',
            left: 'center',
            textStyle: {
              fontSize: 12,
              color: '#a0cfff'
            }
          },
          xAxis: {
            type: 'category',
            data: [],
            axisLabel: {
              color: '#a0cfff'
            }
          },
          yAxis: {
            type: 'value',
            name: '测量值',
            nameTextStyle: {
              color: '#a0cfff'
            },
            min: 0,
            max: 100
          },
          series: [{
            name: '数据趋势',
            type: 'line',
            data: []
          }]
        })
        return
      }
      
      // 按时间排序（从早到晚）
      const sortedData = [...filteredData].sort((a, b) => 
        new Date(a.measure_time) - new Date(b.measure_time)
      )
      
      // 准备图表数据
      const times = sortedData.map(item => {
        const date = new Date(item.measure_time)
        return `${date.getMonth() + 1}/${date.getDate()}`
      })
      
      const values = sortedData.map(item => parseFloat(item.value.toFixed(2)))
      
      // 计算数据范围，设置合理的y轴范围
      const validValues = values.filter(v => !isNaN(v))
      const minValue = validValues.length > 0 ? Math.min(...validValues) : 0
      const maxValue = validValues.length > 0 ? Math.max(...validValues) : 100
      
      // 根据数据类型设置y轴范围，支持负数
      let yMin = 0
      let yMax = 100
      
      if (validValues.length > 0) {
        // 处理负数情况
        if (minValue < 0) {
          // 如果有负数，确保y轴包含负数
          const range = maxValue - minValue
          const padding = range * 0.1 // 10%的余量
          yMin = Math.floor(minValue - padding)
          yMax = Math.ceil(maxValue + padding)
        } else {
          // 没有负数的情况
          // 如果数据范围很小（如静力水准，小于10），设置较小的范围
          if (maxValue < 10) {
            yMin = 0
            yMax = Math.ceil(maxValue * 1.2) // 增加20%的余量
          } 
          // 如果数据范围中等（如引张线，10-100），设置中等范围
          else if (maxValue < 100) {
            yMin = Math.floor(minValue * 0.8) // 减少20%
            yMax = Math.ceil(maxValue * 1.2) // 增加20%
          }
          // 如果数据范围很大（如水位，100+），设置较大的范围
          else {
            yMin = Math.floor(minValue * 0.9) // 减少10%
            yMax = Math.ceil(maxValue * 1.1) // 增加10%
          }
        }
      }
      
      trendChart.setOption({
        title: {
          text: '最新一个月数据趋势',
          left: 'center',
          textStyle: {
            fontSize: 12,
            color: '#a0cfff'
          }
        },
        tooltip: {
          trigger: 'axis',
          formatter: (params) => {
            const time = params[0].name
            const value = params[0].value
            const dataIndex = params[0].dataIndex
            const originalTime = sortedData[dataIndex]?.measure_time || time
            return `${originalTime}: ${value}`
          }
        },
        xAxis: {
          type: 'category',
          data: times,
          axisLabel: {
            color: '#a0cfff',
            rotate: 45
          },
          axisLine: {
            lineStyle: {
              color: 'rgba(64, 158, 255, 0.3)'
            }
          }
        },
        yAxis: {
          type: 'value',
          name: '测量值',
          nameTextStyle: {
            color: '#a0cfff'
          },
          axisLabel: {
            color: '#a0cfff'
          },
          axisLine: {
            lineStyle: {
              color: 'rgba(64, 158, 255, 0.3)'
            }
          },
          splitLine: {
            lineStyle: {
              color: 'rgba(64, 158, 255, 0.1)'
            }
          },
          min: yMin,
          max: yMax
        },
        series: [{
          name: '数据趋势',
          type: 'line',
          data: values,
          smooth: true,
          itemStyle: {
            color: '#6F5EF9'
          },
          lineStyle: {
            width: 2
          },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(111, 94, 249, 0.6)' },
              { offset: 1, color: 'rgba(111, 94, 249, 0.1)' }
            ])
          }
        }],
        grid: {
          left: '10%',
          right: '10%',
          bottom: '20%',
          top: '20%',
          containLabel: true
        }
      })
    } else {
      // 最近一年数据趋势：使用summary API获取月度数据
      const summaryData = await getMeasurementsSummary({
        interval: 'month',
        instrument_id: pointId,
        end_time: '2024-12-31 23:59:59', // 数据截止到2024年底
        limit: 12
      })
      
      // 如果没有数据，显示空图表
      if (!summaryData || summaryData.length === 0) {
        trendChart.setOption({
          title: {
            text: '最近一年数据趋势',
            subtext: '暂无数据',
            left: 'center',
            textStyle: {
              fontSize: 12,
              color: '#a0cfff'
            }
          },
          xAxis: {
            type: 'category',
            data: [],
            axisLabel: {
              color: '#a0cfff'
            }
          },
          yAxis: {
            type: 'value',
            name: '测量值',
            nameTextStyle: {
              color: '#a0cfff'
            },
            min: 0,
            max: 100
          },
          series: [{
            name: '数据趋势',
            type: 'line',
            data: []
          }]
        })
        return
      }
      
      // 准备图表数据
      const times = summaryData.map(item => {
        const [year, month] = item.period.split('-')
        return `${parseInt(month)}月`
      }).reverse()
      
      const values = summaryData.map(item => item.avg_value).reverse()
      
      // 计算数据范围，设置合理的y轴范围
      const validValues = values.filter(v => v !== null && !isNaN(v))
      const minValue = validValues.length > 0 ? Math.min(...validValues) : 0
      const maxValue = validValues.length > 0 ? Math.max(...validValues) : 100
      
      // 根据数据类型设置y轴范围，支持负数
      let yMin = 0
      let yMax = 100
      
      if (validValues.length > 0) {
        // 处理负数情况
        if (minValue < 0) {
          // 如果有负数，确保y轴包含负数
          const range = maxValue - minValue
          const padding = range * 0.1 // 10%的余量
          yMin = Math.floor(minValue - padding)
          yMax = Math.ceil(maxValue + padding)
        } else {
          // 没有负数的情况
          // 如果数据范围很小（如静力水准，小于10），设置较小的范围
          if (maxValue < 10) {
            yMin = 0
            yMax = Math.ceil(maxValue * 1.2) // 增加20%的余量
          } 
          // 如果数据范围中等（如引张线，10-100），设置中等范围
          else if (maxValue < 100) {
            yMin = Math.floor(minValue * 0.8) // 减少20%
            yMax = Math.ceil(maxValue * 1.2) // 增加20%
          }
        // 如果数据范围很大（如水位，100+），设置较大的范围
        else {
          yMin = Math.floor(minValue * 0.9) // 减少10%
          yMax = Math.ceil(maxValue * 1.1) // 增加10%
        }
      }
    }
    
    trendChart.setOption({
      title: {
        text: '最近一年数据趋势',
        left: 'center',
        textStyle: {
          fontSize: 12,
          color: '#a0cfff'
        }
      },
      tooltip: {
        trigger: 'axis',
        formatter: (params) => {
          const time = params[0].name
          const value = params[0].value
          return `${time}: ${value !== null ? value.toFixed(2) : '无数据'}`
        }
      },
      xAxis: {
        type: 'category',
        data: times,
        axisLabel: {
          color: '#a0cfff'
        },
        axisLine: {
          lineStyle: {
            color: 'rgba(64, 158, 255, 0.3)'
          }
        }
      },
      yAxis: {
        type: 'value',
        name: '测量值',
        nameTextStyle: {
          color: '#a0cfff'
        },
        axisLabel: {
          color: '#a0cfff'
        },
        axisLine: {
          lineStyle: {
            color: 'rgba(64, 158, 255, 0.3)'
          }
        },
        splitLine: {
          lineStyle: {
            color: 'rgba(64, 158, 255, 0.1)'
          }
        },
        min: yMin,
        max: yMax
      },
      series: [{
        name: '数据趋势',
        type: 'line',
        data: values,
        smooth: true,
        itemStyle: {
          color: '#6F5EF9'
        },
        lineStyle: {
          width: 2
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(111, 94, 249, 0.6)' },
            { offset: 1, color: 'rgba(111, 94, 249, 0.1)' }
          ])
        },
        connectNulls: true // 连接空数据点
      }],
      grid: {
        left: '10%',
        right: '10%',
        bottom: '15%',
        top: '20%',
        containLabel: true
      }
    })
    }
  } catch (error) {
    console.error('加载趋势数据失败:', error)
    // 如果API失败，显示空图表
    trendChart.setOption({
      title: {
        text: trendTimeRange.value === 'month' ? '最新一个月数据趋势' : '最近一年数据趋势',
        subtext: '数据加载失败',
        left: 'center',
        textStyle: {
          fontSize: 12,
          color: '#a0cfff'
        }
      },
      xAxis: {
        type: 'category',
        data: [],
        axisLabel: {
          color: '#a0cfff'
        }
      },
      yAxis: {
        type: 'value',
        name: '测量值',
        nameTextStyle: {
          color: '#a0cfff'
        },
        min: 0,
        max: 100
      },
      series: [{
        name: '数据趋势',
        type: 'line',
        data: []
      }]
    })
  }
}

const selectPoint = (point) => {
  selectedPointId.value = point.id
  selectedPoint.value = point
  loadPointMeasurements(point.instrument_id)
  
  // 根据仪器ID获取对应的模型分块名字
  const blockNames = getBlockNamesFromInstrumentId(point.instrument_id)
  if (blockNames.length > 0 && selectedModel.value === 'dam3') {
    // 使用第一个匹配的分块进行高亮
    const blockName = blockNames[0]
    highlightComponent(blockName)
  } else {
    // 如果没有找到对应的分块，重置高亮
    resetHighlight()
    highlightedComponent.value = ''
  }
}

// Cesium相关方法
const initCesiumViewer = () => {
  if (!viewerEl.value) return

  viewer = new Cesium.Viewer(viewerEl.value, {
    animation: false,
    timeline: false,
    baseLayerPicker: false,
    geocoder: false,
    homeButton: false,
    sceneModePicker: false,
    navigationHelpButton: false,
    fullscreenButton: false,
    // 禁用selectionIndicator和infoBox
    selectionIndicator: false,
    infoBox: false,
    terrainProvider: new Cesium.EllipsoidTerrainProvider(),
    imageryProvider: new Cesium.UrlTemplateImageryProvider({
      url: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png'
    })
  })

  // 设置初始视角
  viewer.camera.setView({
    destination: Cesium.Cartesian3.fromDegrees(118.7460, 32.0600, 1000),
    orientation: {
      heading: Cesium.Math.toRadians(0),
      pitch: Cesium.Math.toRadians(-45),
      roll: 0
    }
  })

  // 加载初始模型
  switchModel()
  
  // 添加测点
  addPointsToCesium()
}

const switchModel = () => {
  if (!viewer) return

  // 移除当前模型
  if (currentModelEntity) {
    viewer.entities.remove(currentModelEntity)
    currentModelEntity = null
  }

  const position = Cesium.Cartesian3.fromDegrees(118.7460, 32.0600, 30.0)

  // 加载GLB模型
  let modelPath = '/models/dam1.glb'
  
  if (selectedModel.value === 'dam2') {
    modelPath = '/models/dam2.glb'
  } else if (selectedModel.value === 'dam3') {
    modelPath = '/models/dam3.glb'
  }
  
  currentModelEntity = viewer.entities.add({
    position: position,
    model: {
      uri: modelPath,
      scale: 5.0,
      minimumPixelSize: 128,
      maximumScale: 100
    }
  })
  
  viewer.zoomTo(currentModelEntity)
  
  // 如果是dam3模型，启用分块交互
  if (selectedModel.value === 'dam3') {
    // 等待模型加载完成后设置交互
    setTimeout(() => {
      setupModelBlockInteraction()
    }, 1000)
  } else {
    // 如果是其他模型，移除交互处理器
    removeModelBlockInteraction()
  }
}

// 设置dam3模型分块交互
const setupModelBlockInteraction = () => {
  if (!viewer || !currentModelEntity) return
  
  // 移除旧的处理器
  removeModelBlockInteraction()
  
  // 直接设置基础交互
  setupBasicInteraction()
}

// 设置基础交互
const setupBasicInteraction = () => {
  // 鼠标移动处理器：悬停显示
  mouseMoveHandler = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas)
  mouseMoveHandler.setInputAction((movement) => {
    const pick = viewer.scene.pick(movement.endPosition)
    
    if (Cesium.defined(pick) && pick.detail && pick.detail.node) {
      const rawName = pick.detail.node._name || pick.detail.node.name
      
      if (rawName) {
        const objectName = String(rawName)
        hoveredBlock.value = objectName
      } else {
        hoveredBlock.value = '模型表面'
      }
    } else {
      hoveredBlock.value = ''
    }
  }, Cesium.ScreenSpaceEventType.MOUSE_MOVE)
  
  // 鼠标点击处理器：选择分块
  clickHandler = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas)
  clickHandler.setInputAction((movement) => {
    const pick = viewer.scene.pick(movement.position)
    
    if (Cesium.defined(pick) && pick.detail && pick.detail.node) {
      const rawName = pick.detail.node._name || pick.detail.node.name
      
      if (rawName) {
        const objectName = String(rawName)
        selectedBlock.value = objectName
        
        // 根据分块名字获取仪器ID
        const instrumentId = getInstrumentIdFromBlockName(objectName)
        selectedInstrumentIdFromBlock.value = instrumentId
        
        if (instrumentId) {
          // 找到对应的测点
          const point = instruments.value.find(p => p.instrument_id === instrumentId)
          if (point) {
            // 选择该测点并加载数据
            selectPoint(point)
            ElMessage.success(`已选择分块: ${objectName} → 仪器: ${instrumentId}`)
          } else {
            ElMessage.warning(`找到分块: ${objectName}，但未找到对应的测点仪器: ${instrumentId}`)
          }
        } else {
          ElMessage.warning(`找到分块: ${objectName}，但未找到对应的仪器映射`)
        }
      } else {
        selectedBlock.value = '点击了模型表面'
        ElMessage.info('点击了模型表面，请尝试点击模型的不同部分')
      }
    } else {
      selectedBlock.value = '点击了模型表面'
      ElMessage.info('点击了模型表面，请尝试点击模型的不同部分')
    }
  }, Cesium.ScreenSpaceEventType.LEFT_CLICK)
}

// 移除模型分块交互
const removeModelBlockInteraction = () => {
  // 移除高亮
  if (highlightedFeature) {
    highlightedFeature.color = Cesium.Color.WHITE
    highlightedFeature = null
  }
  
  // 移除处理器
  if (mouseMoveHandler) {
    mouseMoveHandler.destroy()
    mouseMoveHandler = null
  }
  
  if (clickHandler) {
    clickHandler.destroy()
    clickHandler = null
  }
  
  // 清空显示
  hoveredBlock.value = ''
}

// 高亮组件函数
const highlightComponent = (componentName) => {
  if (!viewer || !currentModelEntity) return
  
  // 获取模型对象
  const model = currentModelEntity.model
  if (!model || !model._runtime || !model._runtime._model) return
  
  const cesiumModel = model._runtime._model
  
  // 如果传入空值或再次点击当前项，则重置
  if (!componentName || highlightedComponent.value === componentName) {
    resetHighlight()
    highlightedComponent.value = ''
    return
  }
  
  // 保存当前高亮的组件
  highlightedComponent.value = componentName
  
  try {
    // 1. 开启轮廓线
    cesiumModel.silhouetteSize = 5.0
    cesiumModel.silhouetteColor = Cesium.Color.YELLOW
    
    // 2. 设置透视效果
    viewer.scene.globe.depthTestAgainstTerrain = false
    
    // 3. 使用model.style进行局部高亮
    if (cesiumModel.style) {
      // 创建样式：目标节点亮色，其他节点暗色
      const style = new Cesium.Cesium3DTileStyle({
        color: {
          conditions: [
            [`\${name} === '${componentName}'`, "color('lime')"],
            ["true", "color('rgba(128, 128, 128, 0.3)')"]
          ]
        }
      })
      cesiumModel.style = style
    } else {
      // 如果style不可用，尝试直接修改节点颜色
      if (cesiumModel._sceneGraph && cesiumModel._sceneGraph._runtimeNodes) {
        const runtimeNodes = cesiumModel._sceneGraph._runtimeNodes
        let found = false
        
        // 遍历所有节点
        for (const node of runtimeNodes) {
          const nodeName = node._name || node.name
          if (!nodeName) continue
          
          if (nodeName === componentName) {
            // 目标节点设置为亮色
            try {
              node.color = Cesium.Color.LIME
              found = true
            } catch (error) {
              console.warn('无法设置节点颜色:', error)
            }
          } else {
            // 其他节点设置为暗色
            try {
              node.color = Cesium.Color.GRAY.withAlpha(0.3)
            } catch (error) {
              // 忽略错误
            }
          }
        }
        
        if (!found) {
          console.warn(`未找到组件: ${componentName}`)
          resetHighlight()
          highlightedComponent.value = ''
        }
      }
    }
    
  } catch (error) {
    console.error('高亮组件失败:', error)
    resetHighlight()
    highlightedComponent.value = ''
  }
}

// 重置高亮
const resetHighlight = () => {
  if (!viewer || !currentModelEntity) return
  
  const model = currentModelEntity.model
  if (!model || !model._runtime || !model._runtime._model) return
  
  const cesiumModel = model._runtime._model
  
  try {
    // 关闭轮廓线
    cesiumModel.silhouetteSize = 0.0
    
    // 重置透视效果
    viewer.scene.globe.depthTestAgainstTerrain = true
    
    // 重置样式
    if (cesiumModel.style) {
      cesiumModel.style = new Cesium.Cesium3DTileStyle({
        color: "color('white')"
      })
    }
    
    // 重置节点颜色
    if (cesiumModel._sceneGraph && cesiumModel._sceneGraph._runtimeNodes) {
      const runtimeNodes = cesiumModel._sceneGraph._runtimeNodes
      for (const node of runtimeNodes) {
        try {
          node.color = Cesium.Color.WHITE
        } catch (error) {
          // 忽略错误
        }
      }
    }
  } catch (error) {
    console.error('重置高亮失败:', error)
  }
}


const addPointsToCesium = () => {
  if (!viewer) return
  
  // 清理旧点
  for (const ent of pointEntities.values()) {
    viewer.entities.remove(ent)
  }
  pointEntities.clear()
  
  // 不再添加测点到Cesium，因为缺少正确的元数据
  // 测点显示将在以后解决
}

// 简化resetView函数
const resetView = () => {
  if (!viewer) return
  
  viewer.camera.setView({
    destination: Cesium.Cartesian3.fromDegrees(118.7460, 32.0600, 1000),
    orientation: {
      heading: Cesium.Math.toRadians(0),
      pitch: Cesium.Math.toRadians(-45),
      roll: 0
    }
  })
}

// 简化toggleFullscreen函数
const toggleFullscreen = () => {
  const container = document.querySelector('.monitor-container')
  if (!document.fullscreenElement) {
    container.requestFullscreen().catch(err => {
      console.error('全屏失败:', err)
    })
  } else {
    document.exitFullscreen()
  }
}
const flyToPoint = (point) => {}

const loadAndRenderUpstreamChart = async () => {
  if (!upstreamChart) return
  
  try {
    const selectedYear = parseInt(upstreamYear.value)
    
    // 使用改进后的summary API获取数据
    const summaryData = await getMeasurementsSummary({
      interval: 'month',
      instrument_id: '上游',
      end_time: `${selectedYear}-12-31 23:59:59`,
      limit: 12
    })
    
    // 准备月份数据
    const months = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
    const monthDataMap = {}
    
    // 初始化月份数据
    months.forEach(month => {
      monthDataMap[month] = null
    })
    
    // 填充API返回的数据
    summaryData.forEach(item => {
      // 解析period，格式为"YYYY-MM"
      const [year, month] = item.period.split('-')
      const monthKey = `${parseInt(month)}月`
      
      // 只处理当前年份的数据
      if (parseInt(year) === selectedYear && monthDataMap.hasOwnProperty(monthKey)) {
        monthDataMap[monthKey] = item.avg_value
      }
    })
    
    // 准备图表数据
    const data = months.map(month => monthDataMap[month])
    
    // 检查是否有任何数据
    const hasData = data.some(v => v !== null)
    
    if (!hasData) {
      // 如果没有数据，显示空图表
      upstreamChart.setOption({
        title: {
          text: `上游水位变化 (${upstreamYear.value})`,
          subtext: '暂无数据',
          left: 'center',
          textStyle: {
            fontSize: 12,
            color: '#a0cfff'
          }
        },
        xAxis: {
          type: 'category',
          data: months,
          axisLabel: {
            color: '#a0cfff'
          }
        },
        yAxis: {
          type: 'value',
          name: '水位 (m)',
          nameTextStyle: {
            color: '#a0cfff'
          },
          min: 130,
          max: 150
        },
        series: [{
          name: '上游水位',
          type: 'line',
          data: data,
          connectNulls: true
        }]
      })
      return
    }
    
    // 计算数据范围，设置合理的y轴范围
    const validData = data.filter(v => v !== null && !isNaN(v))
    const minValue = validData.length > 0 ? Math.min(...validData) : 130
    const maxValue = validData.length > 0 ? Math.max(...validData) : 150
    
    upstreamChart.setOption({
      title: {
        text: `上游水位变化 (${upstreamYear.value})`,
        left: 'center',
        textStyle: {
          fontSize: 12,
          color: '#a0cfff'
        }
      },
      tooltip: {
        trigger: 'axis',
        formatter: (params) => {
          const month = params[0].name
          const value = params[0].value
          return value !== null ? `${month}: ${value.toFixed(2)} m` : `${month}: 无数据`
        }
      },
      xAxis: {
        type: 'category',
        data: months,
        axisLabel: {
          color: '#a0cfff'
        },
        axisLine: {
          lineStyle: {
            color: 'rgba(64, 158, 255, 0.3)'
          }
        }
      },
      yAxis: {
        type: 'value',
        name: '水位 (m)',
        nameTextStyle: {
          color: '#a0cfff'
        },
        axisLabel: {
          color: '#a0cfff'
        },
        axisLine: {
          lineStyle: {
            color: 'rgba(64, 158, 255, 0.3)'
          }
        },
        splitLine: {
          lineStyle: {
            color: 'rgba(64, 158, 255, 0.1)'
          }
        },
        min: Math.floor(minValue * 0.95), // 最小值稍微低一点
        max: Math.ceil(maxValue * 1.05)   // 最大值稍微高一点
      },
      series: [{
        name: '上游水位',
        type: 'line',
        data: data,
        smooth: true,
        itemStyle: {
          color: '#5B8FF9'
        },
        lineStyle: {
          width: 3
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(91, 143, 249, 0.6)' },
            { offset: 1, color: 'rgba(91, 143, 249, 0.1)' }
          ])
        },
        connectNulls: true // 连接空数据点
      }],
      grid: {
        left: '10%',
        right: '10%',
        bottom: '15%',
        top: '20%',
        containLabel: true
      }
    })
  } catch (error) {
    console.error('加载上游水位数据失败:', error)
    // 如果API失败，显示空图表
    const months = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
    
    upstreamChart.setOption({
      title: {
        text: `上游水位变化 (${upstreamYear.value})`,
        subtext: '数据加载失败',
        left: 'center',
        textStyle: {
          fontSize: 12,
          color: '#a0cfff'
        }
      },
      xAxis: {
        type: 'category',
        data: months,
        axisLabel: {
          color: '#a0cfff'
        }
      },
      yAxis: {
        type: 'value',
        name: '水位 (m)',
        nameTextStyle: {
          color: '#a0cfff'
        },
        min: 130,
        max: 150
      },
      series: [{
        name: '上游水位',
        type: 'line',
        data: []
      }]
    })
  }
}

const loadAndRenderDownstreamChart = async () => {
  if (!downstreamChart) return
  
  try {
    const selectedYear = parseInt(downstreamYear.value)
    
    // 使用改进后的summary API获取数据
    const summaryData = await getMeasurementsSummary({
      interval: 'month',
      instrument_id: '下游',
      end_time: `${selectedYear}-12-31 23:59:59`,
      limit: 12
    })
    
    // 准备月份数据
    const months = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
    const monthDataMap = {}
    
    // 初始化月份数据
    months.forEach(month => {
      monthDataMap[month] = null
    })
    
    // 填充API返回的数据
    summaryData.forEach(item => {
      // 解析period，格式为"YYYY-MM"
      const [year, month] = item.period.split('-')
      const monthKey = `${parseInt(month)}月`
      
      // 只处理当前年份的数据
      if (parseInt(year) === selectedYear && monthDataMap.hasOwnProperty(monthKey)) {
        monthDataMap[monthKey] = item.avg_value
      }
    })
    
    // 准备图表数据
    const data = months.map(month => monthDataMap[month])
    
    // 检查是否有任何数据
    const hasData = data.some(v => v !== null)
    
    if (!hasData) {
      // 如果没有数据，显示空图表
      downstreamChart.setOption({
        title: {
          text: `下游水位变化 (${downstreamYear.value})`,
          subtext: '暂无数据',
          left: 'center',
          textStyle: {
            fontSize: 12,
            color: '#a0cfff'
          }
        },
        xAxis: {
          type: 'category',
          data: months,
          axisLabel: {
            color: '#a0cfff'
          }
        },
        yAxis: {
          type: 'value',
          name: '水位 (m)',
          nameTextStyle: {
            color: '#a0cfff'
          },
          min: 120,
          max: 140
        },
        series: [{
          name: '下游水位',
          type: 'line',
          data: data,
          connectNulls: true
        }]
      })
      return
    }
    
    // 计算数据范围，设置合理的y轴范围
    const validData = data.filter(v => v !== null && !isNaN(v))
    const minValue = validData.length > 0 ? Math.min(...validData) : 120
    const maxValue = validData.length > 0 ? Math.max(...validData) : 140
    
    downstreamChart.setOption({
      title: {
        text: `下游水位变化 (${downstreamYear.value})`,
        left: 'center',
        textStyle: {
          fontSize: 12,
          color: '#a0cfff'
        }
      },
      tooltip: {
        trigger: 'axis',
        formatter: (params) => {
          const month = params[0].name
          const value = params[0].value
          return value !== null ? `${month}: ${value.toFixed(2)} m` : `${month}: 无数据`
        }
      },
      xAxis: {
        type: 'category',
        data: months,
        axisLabel: {
          color: '#a0cfff'
        },
        axisLine: {
          lineStyle: {
            color: 'rgba(64, 158, 255, 0.3)'
          }
        }
      },
      yAxis: {
        type: 'value',
        name: '水位 (m)',
        nameTextStyle: {
          color: '#a0cfff'
        },
        axisLabel: {
          color: '#a0cfff'
        },
        axisLine: {
          lineStyle: {
            color: 'rgba(64, 158, 255, 0.3)'
          }
        },
        splitLine: {
          lineStyle: {
            color: 'rgba(64, 158, 255, 0.1)'
          }
        },
        min: Math.floor(minValue * 0.95), // 最小值稍微低一点
        max: Math.ceil(maxValue * 1.05)   // 最大值稍微高一点
      },
      series: [{
        name: '下游水位',
        type: 'line',
        data: data,
        smooth: true,
        itemStyle: {
          color: '#E86452'
        },
        lineStyle: {
          width: 3
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(232, 100, 82, 0.6)' },
            { offset: 1, color: 'rgba(232, 100, 82, 0.1)' }
          ])
        },
        connectNulls: true // 连接空数据点
      }],
      grid: {
        left: '10%',
        right: '10%',
        bottom: '15%',
        top: '20%',
        containLabel: true
      }
    })
  } catch (error) {
    console.error('加载下游水位数据失败:', error)
    // 如果API失败，显示空图表
    const months = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
    
    downstreamChart.setOption({
      title: {
        text: `下游水位变化 (${downstreamYear.value})`,
        subtext: '数据加载失败',
        left: 'center',
        textStyle: {
          fontSize: 12,
          color: '#a0cfff'
        }
      },
      xAxis: {
        type: 'category',
        data: months,
        axisLabel: {
          color: '#a0cfff'
        }
      },
      yAxis: {
        type: 'value',
        name: '水位 (m)',
        nameTextStyle: {
          color: '#a0cfff'
        },
        min: 120,
        max: 140
      },
      series: [{
        name: '下游水位',
        type: 'line',
        data: []
      }]
    })
  }
}

// 监听上游年份变化
watch(upstreamYear, () => {
  loadAndRenderUpstreamChart()
})

// 监听下游年份变化
watch(downstreamYear, () => {
  loadAndRenderDownstreamChart()
})

// 监听趋势时间范围变化
watch(trendTimeRange, () => {
  if (selectedPoint.value && trendChart) {
    renderTrendChart(selectedPoint.value.instrument_id)
  }
})

// 初始化新增图表
const initAdditionalCharts = () => {
  // 初始化上游水位图表
  if (upstreamChartEl.value) {
    if (upstreamChart) {
      upstreamChart.dispose()
    }
    upstreamChart = echarts.init(upstreamChartEl.value)
    loadAndRenderUpstreamChart()
  }
  
  // 初始化下游水位图表
  if (downstreamChartEl.value) {
    if (downstreamChart) {
      downstreamChart.dispose()
    }
    downstreamChart = echarts.init(downstreamChartEl.value)
    loadAndRenderDownstreamChart()
  }
}

// 数据导出功能
const exportData = async () => {
  if (!selectedPoint.value) return
  
  try {
    // 获取选定仪器的所有数据
    const allData = await getMeasurements({
      instrument_id: selectedPoint.value.instrument_id,
      limit: 1000 // 获取最多1000条数据
    })
    
    // 准备CSV内容
    const headers = ['测量时间', '监测类型', '仪器编号', '测量值', '单位', '水位值']
    const csvRows = [
      headers.join(','),
      ...allData.map(item => [
        `"${item.measure_time}"`,
        `"${item.type_name}"`,
        `"${item.instrument_id}"`,
        item.value,
        `"${item.unit}"`,
        item.water_level || ''
      ].join(','))
    ]
    
    const csvContent = csvRows.join('\n')
    
    // 创建下载链接
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    
    link.setAttribute('href', url)
    link.setAttribute('download', `${selectedPoint.value.name}_${selectedPoint.value.instrument_id}_数据.csv`)
    link.style.visibility = 'hidden'
    
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    ElMessage.success('数据导出成功')
  } catch (error) {
    console.error('导出数据失败:', error)
    ElMessage.error('导出数据失败')
  }
}

// 生命周期
onMounted(async () => {
  // 加载用户信息
  try {
    userInfo.value = await getCurrentUser()
  } catch (error) {
    console.error('加载用户信息失败:', error)
    const storedUser = localStorage.getItem('user_info')
    if (storedUser) {
      try {
        userInfo.value = JSON.parse(storedUser)
      } catch {
        userInfo.value = { username: '用户', role: 'user' }
      }
    }
  }
  
  // 初始化时间更新
  updateTime()
  const timeInterval = setInterval(updateTime, 1000)
  
  // 加载初始数据
  await Promise.all([
    loadStatistics(),
    loadMonitoringTypes(),
    loadInstruments(),
    loadLatestMeasurements()
  ])
  
  // 初始化Cesium
  initCesiumViewer()
  
  // 初始化新增图表
  initAdditionalCharts()
  
  // 监听全屏变化
  document.addEventListener('fullscreenchange', () => {
    isFullscreen.value = !!document.fullscreenElement
  })
  
  // 清理定时器
  onBeforeUnmount(() => {
    clearInterval(timeInterval)
    if (viewer) {
      viewer.destroy()
    }
    if (upstreamChart) {
      upstreamChart.dispose()
    }
    if (downstreamChart) {
      downstreamChart.dispose()
    }
    if (usageChart) {
      usageChart.dispose()
    }
    if (monthlyTrendChart) {
      monthlyTrendChart.dispose()
    }
    document.removeEventListener('fullscreenchange', () => {})
  })
})
</script>

<style scoped>
@import '../styles/monitor.css';
</style>
