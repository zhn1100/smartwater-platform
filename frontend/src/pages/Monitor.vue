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
          <el-select v-model="selectedPointType" placeholder="类型筛选" size="mini" style="width: 100px;">
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
                <el-radio-group v-model="trendTimeRange" size="mini">
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
                <el-button size="mini" @click="exportData" type="primary">
                  <i class="el-icon-download"></i>
                  导出CSV
                </el-button>
              </div>
            </div>
            
            <!-- 最近二十条数据表格 -->
            <div class="measurements-table">
              <el-table :data="pointMeasurements" size="mini" height="200">
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
          <el-select v-model="selectedModel" placeholder="选择模型" size="mini" @change="switchModel">
            <el-option label="大坝模型1 (dam1.glb)" value="dam1" />
            <el-option label="大坝模型2 (dam2.glb)" value="dam2" />
            <el-option label="大坝模型3 (dam3.glb)" value="dam3" />
          </el-select>
          <el-button size="mini" @click="resetView">重置视角</el-button>
          <el-button size="mini" @click="toggleFullscreen">
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
  getInstruments
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

// Cesium相关
let viewer = null
let currentModelEntity = null
let pointEntities = new Map()

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
    const data = await getInstruments()
    // API返回的是按instrument_id分组的仪器列表
    // 我们需要确保每个仪器都有正确的字段
    const instrumentsWithLatestValue = []
    
    for (const item of data) {
      try {
        // 获取每个仪器的最新一条数据
        const latestData = await getMeasurements({
          instrument_id: item.instrument_id,
          limit: 1,
          order_by: 'measure_time desc'
        })
        
        instrumentsWithLatestValue.push({
          id: instrumentsWithLatestValue.length + 1, // 为前端生成一个唯一的ID
          instrument_id: item.instrument_id, // 这是API返回的仪器ID
          name: `仪器 ${item.instrument_id}`, // 生成显示名称
          type_id: item.type_id,
          type_name: item.type_name,
          latest_value: latestData.length > 0 ? latestData[0].value : null,
          unit: item.unit || 'mm' // 使用API返回的单位或默认值
        })
      } catch (error) {
        console.error(`获取仪器 ${item.instrument_id} 最新数据失败:`, error)
        // 如果获取失败，仍然添加仪器但没有最新值
        instrumentsWithLatestValue.push({
          id: instrumentsWithLatestValue.length + 1,
          instrument_id: item.instrument_id,
          name: `仪器 ${item.instrument_id}`,
          type_id: item.type_id,
          type_name: item.type_name,
          latest_value: null,
          unit: item.unit || 'mm'
        })
      }
    }
    
    instruments.value = instrumentsWithLatestValue
  } catch (error) {
    console.error('加载仪器列表失败:', error)
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
    // 获取2018-2024年的所有数据
    const years = ['2018', '2019', '2020', '2021', '2022', '2023', '2024']
    const yearData = {}
    
    // 初始化年份数据
    years.forEach(year => {
      yearData[year] = 0
    })
    
    // 为每个年份获取数据
    for (const year of years) {
      try {
        const startTime = `${year}-01-01 00:00:00`
        const endTime = `${year}-12-31 23:59:59`
        
        // 获取该年份的数据
        const yearDataResponse = await getMeasurements({
          instrument_id: pointId,
          start_time: startTime,
          end_time: endTime,
          limit: 1000 // 水位等数据一年不止100次采集，设为1000
        })
        
        // 统计实际数量
        yearData[year] = yearDataResponse.length
      } catch (error) {
        console.error(`获取${year}年数据失败:`, error)
        yearData[year] = 0
      }
    }
    
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
    console.log('开始加载趋势数据，仪器ID:', pointId)
    
    // 数据只到2024年，所以我们应该从2024年往前计算
    const endDate = new Date('2024-12-31') // 数据截止到2024年底
    const startDate = new Date('2024-12-31')
    
    // 根据选择的时间范围设置开始时间
    if (trendTimeRange.value === 'month') {
      startDate.setDate(startDate.getDate() - 30) // 最近30天
    } else {
      startDate.setFullYear(startDate.getFullYear() - 1) // 最近一年
    }
    
    const startTime = startDate.toISOString().replace('T', ' ').substring(0, 19)
    const endTime = endDate.toISOString().replace('T', ' ').substring(0, 19)
    
    console.log('时间范围:', startTime, '到', endTime)
    
    // 获取数据 - API会自动按时间排序
    const recentData = await getMeasurements({
      instrument_id: pointId,
      start_time: startTime,
      end_time: endTime,
      limit: 100 // 获取最多100条数据
    })
    
    console.log('API返回数据:', recentData)
    
    // 如果没有数据，显示空图表而不是模拟数据
    if (!recentData || recentData.length === 0) {
      console.warn('API返回空数据，显示空图表')
      trendChart.setOption({
        title: {
          text: trendTimeRange.value === 'month' ? '最新一个月数据趋势' : '最近一年数据趋势',
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
    
    // 直接使用API返回的数据，按时间排序
    const sortedData = [...recentData].sort((a, b) => 
      new Date(a.measure_time) - new Date(b.measure_time)
    )
    
    console.log('排序后数据:', sortedData)
    
    // 准备图表数据
    const times = sortedData.map(item => {
      const date = new Date(item.measure_time)
      if (trendTimeRange.value === 'month') {
        // 显示日期
        return `${date.getMonth() + 1}/${date.getDate()}`
      } else {
        // 显示月份
        return `${date.getMonth() + 1}月`
      }
    })
    
    const values = sortedData.map(item => parseFloat(item.value.toFixed(2)))
    
    console.log('图表数据 - 时间:', times)
    console.log('图表数据 - 数值:', values)
    
    // 计算数据范围，设置合理的y轴范围
    const validValues = values.filter(v => !isNaN(v))
    const minValue = validValues.length > 0 ? Math.min(...validValues) : 0
    const maxValue = validValues.length > 0 ? Math.max(...validValues) : 100
    
    console.log('数据范围 - 最小值:', minValue, '最大值:', maxValue)
    
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
    
    console.log('y轴范围 - 最小值:', yMin, '最大值:', yMax)
    
    trendChart.setOption({
      title: {
        text: trendTimeRange.value === 'month' ? '最新一个月数据趋势' : '最近一年数据趋势',
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
          rotate: trendTimeRange.value === 'month' ? 45 : 0
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
        bottom: trendTimeRange.value === 'month' ? '20%' : '15%',
        top: '20%',
        containLabel: true
      }
    })
    
    console.log('图表渲染完成')
  } catch (error) {
    console.error('加载趋势数据失败:', error)
    // 如果API失败，显示空图表而不是模拟数据
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
  flyToPoint(point)
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

const flyToPoint = (point) => {
  if (!viewer || !pointEntities.has(point.id)) return
  
  const entity = pointEntities.get(point.id)
  viewer.flyTo(entity, {
    duration: 1.5,
    offset: new Cesium.HeadingPitchRange(0, Cesium.Math.toRadians(-45), 200)
  })
}

const resetView = () => {
  if (!viewer) return
  
  viewer.camera.flyTo({
    destination: Cesium.Cartesian3.fromDegrees(118.7460, 32.0600, 1000),
    orientation: {
      heading: Cesium.Math.toRadians(0),
      pitch: Cesium.Math.toRadians(-45),
      roll: 0
    },
    duration: 1.5
  })
}

const toggleFullscreen = () => {
  isFullscreen.value = !isFullscreen.value
  if (isFullscreen.value) {
    document.documentElement.requestFullscreen()
  } else {
    document.exitFullscreen()
  }
}

// 新增图表方法
const initAdditionalCharts = () => {
  if (upstreamChartEl.value) {
    upstreamChart = echarts.init(upstreamChartEl.value)
    loadAndRenderUpstreamChart()
  }
  
  if (downstreamChartEl.value) {
    downstreamChart = echarts.init(downstreamChartEl.value)
    loadAndRenderDownstreamChart()
  }
}

const loadAndRenderUpstreamChart = async () => {
  if (!upstreamChart) return
  
  try {
    const selectedYear = parseInt(upstreamYear.value)
    
    // 为每个月份获取数据，确保获取所有数据
    const months = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
    const monthlyData = {}
    
    // 初始化月份数据
    months.forEach(month => {
      monthlyData[month] = { sum: 0, count: 0 }
    })
    
    // 为每个月份获取数据
    for (let month = 1; month <= 12; month++) {
      try {
        const startTime = `${selectedYear}-${String(month).padStart(2, '0')}-01 00:00:00`
        const endTime = `${selectedYear}-${String(month).padStart(2, '0')}-31 23:59:59`
        
        // 获取上游水位数据
        const monthData = await getMeasurements({
          type_id: 3, // 水位监测类型
          instrument_id: '上游',
          start_time: startTime,
          end_time: endTime,
          limit: 100 // 每个月最多100条数据
        })
        
        if (monthData.length > 0) {
          const monthKey = `${month}月`
          monthlyData[monthKey].sum = monthData.reduce((sum, item) => sum + item.value, 0)
          monthlyData[monthKey].count = monthData.length
        }
      } catch (error) {
        console.error(`获取${selectedYear}年${month}月上游水位数据失败:`, error)
      }
    }
    
    // 准备图表数据
    const data = months.map(month => {
      if (monthlyData[month].count > 0) {
        const avg = monthlyData[month].sum / monthlyData[month].count
        return parseFloat(avg.toFixed(2))
      }
      return null // 没有数据
    })
    
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
          return value !== null ? `${month}: ${value} m` : `${month}: 无数据`
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
    
    // 为每个月份获取数据，确保获取所有数据
    const months = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
    const monthlyData = {}
    
    // 初始化月份数据
    months.forEach(month => {
      monthlyData[month] = { sum: 0, count: 0 }
    })
    
    // 为每个月份获取数据
    for (let month = 1; month <= 12; month++) {
      try {
        const startTime = `${selectedYear}-${String(month).padStart(2, '0')}-01 00:00:00`
        const endTime = `${selectedYear}-${String(month).padStart(2, '0')}-31 23:59:59`
        
        // 获取下游水位数据
        const monthData = await getMeasurements({
          type_id: 3, // 水位监测类型
          instrument_id: '下游',
          start_time: startTime,
          end_time: endTime,
          limit: 100 // 每个月最多100条数据
        })
        
        if (monthData.length > 0) {
          const monthKey = `${month}月`
          monthlyData[monthKey].sum = monthData.reduce((sum, item) => sum + item.value, 0)
          monthlyData[monthKey].count = monthData.length
        }
      } catch (error) {
        console.error(`获取${selectedYear}年${month}月下游水位数据失败:`, error)
      }
    }
    
    // 准备图表数据
    const data = months.map(month => {
      if (monthlyData[month].count > 0) {
        const avg = monthlyData[month].sum / monthlyData[month].count
        return parseFloat(avg.toFixed(2))
      }
      return null // 没有数据
    })
    
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
          return value !== null ? `${month}: ${value} m` : `${month}: 无数据`
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

// 监听年份变化
watch([upstreamYear, downstreamYear], () => {
  loadAndRenderUpstreamChart()
  loadAndRenderDownstreamChart()
})

// 监听趋势时间范围变化
watch(trendTimeRange, () => {
  if (selectedPoint.value && trendChart) {
    renderTrendChart(selectedPoint.value.instrument_id)
  }
})

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
