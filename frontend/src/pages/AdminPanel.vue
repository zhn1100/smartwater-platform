<template>
  <div class="admin-container">
    <!-- 顶部导航 -->
    <div class="admin-header">
      <div class="header-left">
        <h1>后台管理系统</h1>
        <p class="subtitle">管理员专用 · 数据管理 · 系统配置</p>
      </div>
      <div class="header-right">
        <div class="user-info">
          <el-avatar :size="36" :src="userAvatar" />
          <div class="user-details">
            <div class="username">{{ userInfo.name || userInfo.username }}</div>
            <div class="user-role">管理员</div>
          </div>
          <el-button type="primary" size="small" @click="goToMonitor">返回监控</el-button>
          <el-button size="small" @click="handleLogout">退出</el-button>
        </div>
      </div>
    </div>

    <!-- 主要内容 -->
    <div class="admin-content">
      <!-- 左侧菜单 -->
      <div class="admin-sidebar">
        <el-menu
          :default-active="activeMenu"
          class="admin-menu"
          @select="handleMenuSelect"
        >
          <el-menu-item index="dashboard">
            <el-icon><i class="el-icon-data-board"></i></el-icon>
            <span>数据概览</span>
          </el-menu-item>
          <el-menu-item index="measurements">
            <el-icon><i class="el-icon-s-data"></i></el-icon>
            <span>测量数据管理</span>
          </el-menu-item>
          <el-menu-item index="instruments">
            <el-icon><i class="el-icon-monitor"></i></el-icon>
            <span>仪器管理</span>
          </el-menu-item>
          <el-menu-item index="users">
            <el-icon><i class="el-icon-user"></i></el-icon>
            <span>用户管理</span>
          </el-menu-item>
        </el-menu>
      </div>

      <!-- 右侧内容区域 -->
      <div class="admin-main">
        <!-- 数据概览 -->
        <div v-if="activeMenu === 'dashboard'" class="dashboard-panel">
          <div class="stats-grid">
            <dv-border-box-8 class="stat-card">
              <div class="stat-content">
                <div class="stat-icon" style="color: #5B8FF9;">
                  <i class="el-icon-data-line"></i>
                </div>
                <div class="stat-details">
                  <div class="stat-value">{{ dashboardStats.totalMeasurements?.toLocaleString() || '0' }}</div>
                  <div class="stat-label">总测量记录</div>
                </div>
              </div>
            </dv-border-box-8>

            <dv-border-box-8 class="stat-card">
              <div class="stat-content">
                <div class="stat-icon" style="color: #5AD8A6;">
                  <i class="el-icon-monitor"></i>
                </div>
                <div class="stat-details">
                  <div class="stat-value">{{ dashboardStats.instrumentCount || '0' }}</div>
                  <div class="stat-label">监测仪器</div>
                </div>
              </div>
            </dv-border-box-8>

            <dv-border-box-8 class="stat-card">
              <div class="stat-content">
                <div class="stat-icon" style="color: #F6BD16;">
                  <i class="el-icon-user"></i>
                </div>
                <div class="stat-details">
                  <div class="stat-value">{{ dashboardStats.userCount || '0' }}</div>
                  <div class="stat-label">系统用户</div>
                </div>
              </div>
            </dv-border-box-8>

            <dv-border-box-8 class="stat-card">
              <div class="stat-content">
                <div class="stat-icon" style="color: #6F5EF9;">
                  <i class="el-icon-alarm-clock"></i>
                </div>
                <div class="stat-details">
                  <div class="stat-value">{{ dashboardStats.lastUpdate || '--' }}</div>
                  <div class="stat-label">最后更新</div>
                </div>
              </div>
            </dv-border-box-8>
          </div>

          <div class="charts-row">
            <div class="chart-card">
              <div class="chart-header">
                <h3>监测类型分布</h3>
              </div>
              <div ref="typeChartEl" class="chart-container"></div>
            </div>
            <div class="chart-card">
              <div class="chart-header">
                <div class="chart-title-controls">
                  <h3>采集数据量</h3>
                  <div class="chart-filters">
                    <el-select v-model="growthChartYear" placeholder="年份" size="small" style="width: 100px;">
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
              </div>
              <div ref="growthChartEl" class="chart-container"></div>
            </div>
          </div>
        </div>

        <!-- 测量数据管理 -->
        <div v-if="activeMenu === 'measurements'" class="measurements-panel">
          <div class="panel-header">
            <h2>测量数据管理</h2>
            <div class="panel-controls">
              <el-button type="primary" size="small" @click="openAddMeasurement">
                <el-icon><i class="el-icon-plus"></i></el-icon>
                新增记录
              </el-button>
              <el-button size="small" @click="refreshMeasurements">
                <el-icon><i class="el-icon-refresh"></i></el-icon>
                刷新
              </el-button>
            </div>
          </div>

          <div class="filter-bar">
            <el-form :inline="true" size="small">
              <el-form-item label="监测类型">
                <el-select v-model="filter.type_id" placeholder="全部类型" clearable>
                  <el-option
                    v-for="type in monitoringTypes"
                    :key="type.id"
                    :label="type.name"
                    :value="type.id"
                  />
                </el-select>
              </el-form-item>
              <el-form-item label="仪器编号">
                <el-select v-model="filter.instrument_id" placeholder="全部仪器" clearable filterable>
                  <el-option
                    v-for="inst in instruments"
                    :key="inst.instrument_id"
                    :label="`${inst.instrument_id} (${inst.type_name})`"
                    :value="inst.instrument_id"
                  />
                </el-select>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="searchMeasurements">查询</el-button>
                <el-button @click="resetFilter">重置</el-button>
              </el-form-item>
            </el-form>
          </div>

          <el-table
            :data="measurements"
            v-loading="loading"
            height="500"
            style="width: 100%"
            size="small"
          >
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="type_name" label="监测类型" width="120" />
            <el-table-column prop="instrument_id" label="仪器编号" width="120" />
            <el-table-column prop="measure_time" label="测量时间" width="180" />
            <el-table-column prop="value" label="测量值" width="120">
              <template #default="{ row }">
                {{ row.value.toFixed(2) }} {{ row.unit }}
              </template>
            </el-table-column>
            <el-table-column prop="water_level" label="水位值" width="120">
              <template #default="{ row }">
                {{ row.water_level ? row.water_level.toFixed(2) : '--' }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button size="small" @click="openEditMeasurement(row)">编辑</el-button>
                <el-popconfirm
                  title="确定删除这条记录吗？"
                  @confirm="deleteMeasurement(row.id)"
                >
                  <template #reference>
                    <el-button size="small" type="danger">删除</el-button>
                  </template>
                </el-popconfirm>
              </template>
            </el-table-column>
          </el-table>

          <div class="pagination">
            <el-pagination
              v-model:current-page="pagination.current"
              v-model:page-size="pagination.size"
              :total="pagination.total"
              :page-sizes="[10, 20, 50, 100]"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
            />
          </div>
        </div>

        <!-- 仪器管理 -->
        <div v-if="activeMenu === 'instruments'" class="instruments-panel">
          <div class="panel-header">
            <h2>仪器管理</h2>
            <div class="panel-controls">
              <el-button size="small" @click="refreshInstruments">
                <el-icon><i class="el-icon-refresh"></i></el-icon>
                刷新
              </el-button>
            </div>
          </div>

          <el-table :data="instruments" height="600" style="width: 100%" size="small">
            <el-table-column prop="instrument_id" label="仪器编号" width="150" />
            <el-table-column prop="type_name" label="监测类型" width="150" />
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <el-button size="small" @click="viewInstrumentData(row)">查看数据</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 用户管理 -->
        <div v-if="activeMenu === 'users'" class="users-panel">
          <div class="panel-header">
            <h2>用户管理</h2>
            <div class="panel-controls">
              <el-button type="primary" size="small" @click="openAddUser">
                <el-icon><i class="el-icon-plus"></i></el-icon>
                新增用户
              </el-button>
              <el-button size="small" @click="refreshUsers">
                <el-icon><i class="el-icon-refresh"></i></el-icon>
                刷新
              </el-button>
            </div>
          </div>

          <el-table :data="users" height="600" style="width: 100%" size="small">
            <el-table-column prop="username" label="用户名" width="150" />
            <el-table-column prop="name" label="姓名" width="150" />
            <el-table-column prop="email" label="邮箱" width="200" />
            <el-table-column prop="role" label="角色" width="120">
              <template #default="{ row }">
                <el-tag :type="row.role === 'admin' ? 'danger' : 'success'" size="small">
                  {{ row.role === 'admin' ? '管理员' : '普通用户' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-popconfirm
                  title="确定删除这个用户吗？"
                  @confirm="deleteUser(row.id)"
                >
                  <template #reference>
                    <el-button size="small" type="danger">删除</el-button>
                  </template>
                </el-popconfirm>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </div>

    <!-- 新增/编辑测量记录对话框 -->
    <el-dialog
      v-model="measurementDialog.visible"
      :title="measurementDialog.title"
      width="500px"
    >
      <el-form :model="measurementForm" :rules="measurementRules" ref="measurementFormRef" label-width="100px">
        <el-form-item label="监测类型" prop="type_id">
          <el-select v-model="measurementForm.type_id" placeholder="请选择监测类型" style="width: 100%">
            <el-option
              v-for="type in monitoringTypes"
              :key="type.id"
              :label="type.name"
              :value="type.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="仪器编号" prop="instrument_id">
          <el-input v-model="measurementForm.instrument_id" placeholder="请输入仪器编号" />
        </el-form-item>
        <el-form-item label="测量时间" prop="measure_time">
          <el-date-picker
            v-model="measurementForm.measure_time"
            type="datetime"
            placeholder="选择测量时间"
            style="width: 100%"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>
        <el-form-item label="测量值" prop="value">
          <el-input-number
            v-model="measurementForm.value"
            :precision="2"
            :step="0.01"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="水位值">
          <el-input-number
            v-model="measurementForm.water_level"
            :precision="2"
            :step="0.01"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="measurementDialog.visible = false">取消</el-button>
        <el-button type="primary" @click="saveMeasurement" :loading="measurementDialog.loading">
          保存
        </el-button>
      </template>
    </el-dialog>

    <!-- 新增用户对话框 -->
    <el-dialog
      v-model="userDialog.visible"
      :title="userDialog.title"
      width="500px"
    >
      <el-form :model="userForm" :rules="userRules" ref="userFormRef" label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="userForm.password" type="password" placeholder="请输入密码" />
        </el-form-item>
        <el-form-item label="姓名" prop="name">
          <el-input v-model="userForm.name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="userForm.role" placeholder="请选择角色" style="width: 100%">
            <el-option label="管理员" value="admin" />
            <el-option label="普通用户" value="user" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="userDialog.visible = false">取消</el-button>
        <el-button type="primary" @click="saveUser" :loading="userDialog.loading">
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onBeforeUnmount, computed, onActivated, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import { logout, getCurrentUser, getUsers, createUser, deleteUser as deleteUserApi } from '../api/auth.js'
import {
  getStatistics,
  getMonitoringTypes,
  getInstruments,
  getMeasurements,
  createMeasurement,
  updateMeasurement,
  deleteMeasurement as deleteMeasurementApi
} from '../api/monitoring_new.js'

const router = useRouter()

// 用户信息
const userInfo = ref({})
const userAvatar = computed(() => {
  return `https://api.dicebear.com/7.x/avataaars/svg?seed=${userInfo.value.username || 'admin'}`
})

// 菜单状态
const activeMenu = ref('dashboard')

// 数据概览
const dashboardStats = ref({
  totalMeasurements: 0,
  instrumentCount: 0,
  userCount: 0,
  lastUpdate: '--'
})

// 测量数据管理
const measurements = ref([])
const monitoringTypes = ref([])
const instruments = ref([])
const loading = ref(false)
const filter = reactive({
  type_id: null,
  instrument_id: null
})
const pagination = reactive({
  current: 1,
  size: 50,
  total: 0
})

// 用户管理
const users = ref([])
const userDialog = reactive({
  visible: false,
  title: '新增用户',
  loading: false,
  mode: 'add', // 'add' or 'edit'
  editingId: null
})

const userForm = reactive({
  username: '',
  password: '',
  name: '',
  email: '',
  role: 'user'
})

const userRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }]
}

const userFormRef = ref()

// 增长图表筛选
const growthChartYear = ref('2024')
const growthChartType = ref('all')

// 对话框状态
const measurementDialog = reactive({
  visible: false,
  title: '新增测量记录',
  loading: false,
  mode: 'add', // 'add' or 'edit'
  editingId: null
})

// 监听增长图表筛选变化
watch([growthChartYear, growthChartType], () => {
  renderGrowthChart()
})

const measurementForm = reactive({
  type_id: null,
  instrument_id: '',
  measure_time: '',
  value: 0,
  water_level: null
})

const measurementRules = {
  type_id: [{ required: true, message: '请选择监测类型', trigger: 'change' }],
  instrument_id: [{ required: true, message: '请输入仪器编号', trigger: 'blur' }],
  measure_time: [{ required: true, message: '请选择测量时间', trigger: 'change' }],
  value: [{ required: true, message: '请输入测量值', trigger: 'blur' }]
}

const measurementFormRef = ref()

// 图表引用
const typeChartEl = ref(null)
const growthChartEl = ref(null)
let typeChart = null
let growthChart = null

// 方法
const handleMenuSelect = (index) => {
  activeMenu.value = index
  if (index === 'dashboard') {
    loadDashboardData()
  } else if (index === 'measurements') {
    loadMeasurements()
    loadMonitoringTypes()
    loadInstruments()
  } else if (index === 'instruments') {
    loadInstruments()
  } else if (index === 'users') {
    loadUsers()
  }
}

const goToMonitor = () => {
  router.push('/monitor')
}

const handleLogout = async () => {
  try {
    await logout()
    router.push('/login')
  } catch (error) {
    console.error('登出失败:', error)
  }
}

// 数据概览相关
const loadDashboardData = async () => {
  try {
    const [stats, types, userList] = await Promise.all([
      getStatistics(),
      getMonitoringTypes(),
      getUsers()
    ])
    
    dashboardStats.value = {
      totalMeasurements: stats.total_measurements || 0,
      instrumentCount: stats.instrument_count || 0,
      userCount: userList.length || 0,
      lastUpdate: new Date().toLocaleTimeString('zh-CN')
    }
    
    renderTypeChart(stats.type_statistics || [])
    await renderGrowthChart()
  } catch (error) {
    console.error('加载仪表板数据失败:', error)
    ElMessage.error('加载数据失败')
  }
}

const renderTypeChart = (typeStats) => {
  if (!typeChartEl.value) return
  
  // 如果图表已存在，先销毁
  if (typeChart) {
    typeChart.dispose()
  }
  
  typeChart = echarts.init(typeChartEl.value)
  
  const data = typeStats.map(item => ({
    name: item.name,
    value: item.count
  }))
  
  typeChart.setOption({
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'center',
      data: data.map(item => item.name)
    },
    series: [{
      name: '监测类型',
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['35%', '50%'],
      itemStyle: {
        borderRadius: 10,
        borderColor: '#fff',
        borderWidth: 2
      },
      data: data
    }]
  })
}

const renderGrowthChart = async () => {
  if (!growthChartEl.value) return
  
  // 如果图表已存在，先销毁
  if (growthChart) {
    growthChart.dispose()
  }
  
  growthChart = echarts.init(growthChartEl.value)
  
  try {
    // 构建查询参数
    const params = {
      limit: 10000 // 获取足够的数据进行统计，水位等数据一年不止100次采集
    }
    
    // 添加类型筛选
    if (growthChartType.value !== 'all') {
      params.type_id = growthChartType.value
    }
    
    // 根据选择的年份设置时间范围
    if (growthChartYear.value !== 'all') {
      const selectedYear = growthChartYear.value
      params.start_time = `${selectedYear}-01-01 00:00:00`
      params.end_time = `${selectedYear}-12-31 23:59:59`
    }
    
    // 调用API获取测量数据
    const measurements = await getMeasurements(params)
    
    // 按月份分组统计数据量
    const monthlyData = {}
    
    // 初始化12个月的数据
    for (let month = 1; month <= 12; month++) {
      const monthKey = `${String(month).padStart(2, '0')}`
      monthlyData[monthKey] = 0
    }
    
    // 统计每个月份的数据量
    measurements.forEach(item => {
      const measureTime = new Date(item.measure_time)
      const month = String(measureTime.getMonth() + 1).padStart(2, '0')
      monthlyData[month] = (monthlyData[month] || 0) + 1
    })
    
    // 准备图表数据
    const months = []
    const data = []
    
    for (let month = 1; month <= 12; month++) {
      const monthKey = `${String(month).padStart(2, '0')}`
      months.push(`${month}月`)
      data.push(monthlyData[monthKey])
    }
    
    const chartTitle = `采集数据量${growthChartYear.value !== 'all' ? ` (${growthChartYear.value})` : ''}`
    
    growthChart.setOption({
      title: {
        text: chartTitle,
        left: 'center',
        textStyle: {
          fontSize: 14
        }
      },
      tooltip: {
        trigger: 'axis',
        formatter: function(params) {
          const month = params[0].axisValue
          const value = params[0].data
          return `${month}<br/>数据量: ${value} 条`
        }
      },
      xAxis: {
        type: 'category',
        data: months,
        axisLabel: {
          rotate: 45
        }
      },
      yAxis: {
        type: 'value',
        name: '数据量 (条)'
      },
      series: [{
        name: '数据量',
        type: 'line',
        data: data,
        smooth: true,
        itemStyle: {
          color: '#5B8FF9'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(91, 143, 249, 0.6)' },
            { offset: 1, color: 'rgba(91, 143, 249, 0.1)' }
          ])
        }
      }],
      grid: {
        left: '3%',
        right: '4%',
        bottom: '15%',
        top: '15%',
        containLabel: true
      }
    })
  } catch (error) {
    console.error('渲染增长图表失败:', error)
    // 如果API调用失败，显示空图表
    growthChart.setOption({
      title: {
        text: `采集数据量${growthChartYear.value !== 'all' ? ` (${growthChartYear.value})` : ''}`,
        left: 'center'
      },
      xAxis: {
        type: 'category',
        data: []
      },
      yAxis: {
        type: 'value'
      },
      series: [{
        name: '数据量',
        type: 'line',
        data: [],
        itemStyle: {
          color: '#5B8FF9'
        }
      }]
    })
  }
}

// 测量数据管理相关
const loadMeasurements = async () => {
  loading.value = true
  try {
    const params = {
      limit: pagination.size,
      offset: (pagination.current - 1) * pagination.size
    }
    
    if (filter.type_id) {
      params.type_id = filter.type_id
    }
    if (filter.instrument_id) {
      params.instrument_id = filter.instrument_id
    }
    
    const data = await getMeasurements(params)
    measurements.value = data
    pagination.total = 1000 // 模拟总数据量，实际应该从API获取
  } catch (error) {
    console.error('加载测量数据失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
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
    instruments.value = await getInstruments()
  } catch (error) {
    console.error('加载仪器列表失败:', error)
  }
}

const loadUsers = async () => {
  try {
    users.value = await getUsers()
  } catch (error) {
    console.error('加载用户列表失败:', error)
  }
}

const refreshMeasurements = () => {
  loadMeasurements()
}

const refreshInstruments = () => {
  loadInstruments()
}

const searchMeasurements = () => {
  pagination.current = 1
  loadMeasurements()
}

const resetFilter = () => {
  filter.type_id = null
  filter.instrument_id = null
  pagination.current = 1
  loadMeasurements()
}

const handleSizeChange = (size) => {
  pagination.size = size
  pagination.current = 1
  loadMeasurements()
}

const handleCurrentChange = (page) => {
  pagination.current = page
  loadMeasurements()
}

const openAddMeasurement = () => {
  measurementDialog.mode = 'add'
  measurementDialog.title = '新增测量记录'
  measurementDialog.editingId = null
  
  // 重置表单
  Object.assign(measurementForm, {
    type_id: null,
    instrument_id: '',
    measure_time: '',
    value: 0,
    water_level: null
  })
  
  measurementDialog.visible = true
}

const openEditMeasurement = (row) => {
  measurementDialog.mode = 'edit'
  measurementDialog.title = '编辑测量记录'
  measurementDialog.editingId = row.id
  
  // 填充表单数据
  Object.assign(measurementForm, {
    type_id: row.type_id,
    instrument_id: row.instrument_id,
    measure_time: row.measure_time,
    value: row.value,
    water_level: row.water_level
  })
  
  measurementDialog.visible = true
}

const saveMeasurement = async () => {
  if (!measurementFormRef.value) return
  
  try {
    await measurementFormRef.value.validate()
    measurementDialog.loading = true
    
    const formData = {
      type_id: measurementForm.type_id,
      instrument_id: measurementForm.instrument_id,
      measure_time: measurementForm.measure_time,
      value: measurementForm.value
    }
    
    if (measurementForm.water_level !== null) {
      formData.water_level = measurementForm.water_level
    }
    
    if (measurementDialog.mode === 'add') {
      await createMeasurement(formData)
      ElMessage.success('新增成功')
    } else {
      await updateMeasurement(measurementDialog.editingId, formData)
      ElMessage.success('更新成功')
    }
    
    measurementDialog.visible = false
    loadMeasurements()
  } catch (error) {
    console.error('保存测量记录失败:', error)
    if (error.response?.data?.message) {
      ElMessage.error(`保存失败: ${error.response.data.message}`)
    } else {
      ElMessage.error('保存失败')
    }
  } finally {
    measurementDialog.loading = false
  }
}

const deleteMeasurement = async (id) => {
  try {
    await deleteMeasurementApi(id)
    ElMessage.success('删除成功')
    loadMeasurements()
  } catch (error) {
    console.error('删除测量记录失败:', error)
    ElMessage.error('删除失败')
  }
}

const viewInstrumentData = (row) => {
  // 切换到测量数据管理，并过滤该仪器
  activeMenu.value = 'measurements'
  filter.instrument_id = row.instrument_id
  filter.type_id = row.type_id
  loadMeasurements()
}

// 图表重新渲染
const reRenderCharts = () => {
  if (typeChart && typeChartEl.value) {
    typeChart.resize()
  }
  if (growthChart && growthChartEl.value) {
    growthChart.resize()
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
        userInfo.value = { username: '管理员', role: 'admin' }
      }
    }
  }
  
  // 加载初始数据
  loadDashboardData()
  
  // 监听窗口大小变化
  window.addEventListener('resize', handleResize)
})

// 组件激活时重新渲染图表
onActivated(() => {
  reRenderCharts()
  // 重新加载数据
  if (activeMenu.value === 'dashboard') {
    loadDashboardData()
  }
})

const handleResize = () => {
  if (typeChart) {
    typeChart.resize()
  }
  if (growthChart) {
    growthChart.resize()
  }
}

// 用户管理相关
const refreshUsers = () => {
  loadUsers()
}

const openAddUser = () => {
  userDialog.mode = 'add'
  userDialog.title = '新增用户'
  userDialog.editingId = null
  
  // 重置表单
  Object.assign(userForm, {
    username: '',
    password: '',
    name: '',
    email: '',
    role: 'user'
  })
  
  userDialog.visible = true
}

const saveUser = async () => {
  if (!userFormRef.value) return
  
  try {
    await userFormRef.value.validate()
    userDialog.loading = true
    
    const formData = {
      username: userForm.username,
      password: userForm.password,
      name: userForm.name,
      email: userForm.email,
      role: userForm.role
    }
    
    // 使用我们创建的API函数
    await createUser(formData)
    ElMessage.success('用户创建成功')
    userDialog.visible = false
    loadUsers()
  } catch (error) {
    console.error('保存用户失败:', error)
    ElMessage.error(`保存失败: ${error.message}`)
  } finally {
    userDialog.loading = false
  }
}

const deleteUser = async (id) => {
  try {
    // 使用我们创建的API函数
    await deleteUserApi(id)
    ElMessage.success('用户删除成功')
    loadUsers()
  } catch (error) {
    console.error('删除用户失败:', error)
    ElMessage.error(`删除失败: ${error.message}`)
  }
}

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  if (typeChart) {
    typeChart.dispose()
  }
  if (growthChart) {
    growthChart.dispose()
  }
})
</script>

<style scoped>
.admin-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f0f2f5;
}

.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  height: 64px;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
}

.header-left h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #1890ff;
}

.subtitle {
  margin: 4px 0 0 0;
  font-size: 12px;
  color: #8c8c8c;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-details {
  display: flex;
  flex-direction: column;
}

.username {
  font-weight: 500;
  font-size: 14px;
}

.user-role {
  font-size: 12px;
  color: #8c8c8c;
}

.admin-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.admin-sidebar {
  width: 200px;
  background: #fff;
  border-right: 1px solid #f0f0f0;
}

.admin-menu {
  border-right: none;
}

.admin-main {
  flex: 1;
  padding: 16px;
  overflow: auto;
}

.dashboard-panel {
  height: 100%;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  height: 120px;
}

.stat-content {
  display: flex;
  align-items: center;
  padding: 24px;
  height: 100%;
}

.stat-icon {
  font-size: 40px;
  margin-right: 20px;
}

.stat-details {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 8px;
  color: #1f2d3d;
}

.stat-label {
  font-size: 14px;
  color: #5e6d82;
}

.charts-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.chart-card {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.chart-header {
  margin-bottom: 16px;
}

.chart-title-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-title-controls h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
  color: #1f2d3d;
}

.chart-filters {
  display: flex;
  gap: 8px;
}

.chart-container {
  height: 300px;
}

.measurements-panel,
.instruments-panel,
.users-panel {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.panel-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 500;
  color: #1f2d3d;
}

.filter-bar {
  margin-bottom: 16px;
  padding: 16px;
  background: #fafafa;
  border-radius: 4px;
}

.pagination {
  margin-top: 16px;
  text-align: right;
}

:deep(.el-table) {
  background: transparent;
}

:deep(.el-table th) {
  background: #fafafa !important;
  color: #1f2d3d !important;
}

:deep(.el-table tr) {
  background: transparent !important;
}

:deep(.el-table--enable-row-hover .el-table__body tr:hover > td) {
  background: #f5f7fa !important;
}

:deep(.el-menu-item) {
  height: 48px;
  line-height: 48px;
}

:deep(.el-menu-item.is-active) {
  background-color: #ecf5ff;
  color: #1890ff;
}

:deep(.el-menu-item:hover) {
  background-color: #f5f7fa;
}
</style>
