/**
 * 监控数据API模块（新Flask后端）
 */
import http from './auth.js'

/**
 * 获取监测类型列表
 * @returns {Promise} 监测类型列表
 */
export async function getMonitoringTypes() {
  const response = await http.get('/api/types')
  return response.data
}

/**
 * 获取仪器列表
 * @returns {Promise} 仪器列表
 */
export async function getInstruments() {
  const response = await http.get('/api/instruments')
  return response.data
}

/**
 * 获取测量数据
 * @param {Object} params - 查询参数
 * @param {number} params.type_id - 监测类型ID（可选）
 * @param {string} params.instrument_id - 仪器ID（可选）
 * @param {string} params.start_time - 开始时间（可选）
 * @param {string} params.end_time - 结束时间（可选）
 * @param {number} params.limit - 返回记录数（可选，默认100）
 * @param {number} params.offset - 偏移量（可选，默认0）
 * @returns {Promise} 测量数据列表
 */
export async function getMeasurements(params = {}) {
  const response = await http.get('/api/measurements', { params })
  return response.data
}

/**
 * 获取统计数据
 * @returns {Promise} 统计数据
 */
export async function getStatistics() {
  const response = await http.get('/api/statistics')
  return response.data
}

/**
 * 获取数据摘要
 * @param {Object} params - 查询参数
 * @param {string} params.interval - 时间间隔（day/week/month/year，默认month）
 * @param {number} params.type_id - 监测类型ID（可选）
 * @param {string} params.instrument_id - 仪器ID（可选）
 * @param {string} params.end_time - 结束时间（可选，用于确定查询的时间范围）
 * @param {number} params.limit - 返回记录数（可选，默认12）
 * @returns {Promise} 数据摘要
 */
export async function getMeasurementsSummary(params = {}) {
  const response = await http.get('/api/measurements/summary', { params })
  return response.data
}

/**
 * 创建新的测量记录（需要管理员权限）
 * @param {Object} data - 测量记录数据
 * @param {number} data.type_id - 监测类型ID
 * @param {string} data.instrument_id - 仪器ID
 * @param {string} data.measure_time - 测量时间（格式：YYYY-MM-DD HH:MM:SS）
 * @param {number} data.value - 测量值
 * @param {number} data.water_level - 水位值（可选，仅引张线数据）
 * @returns {Promise} 创建的测量记录
 */
export async function createMeasurement(data) {
  const response = await http.post('/api/measurements', data)
  return response.data
}

/**
 * 更新测量记录（需要管理员权限）
 * @param {number} measurementId - 测量记录ID
 * @param {Object} data - 要更新的数据
 * @param {number} data.value - 测量值（可选）
 * @param {string} data.measure_time - 测量时间（可选）
 * @param {number} data.water_level - 水位值（可选）
 * @returns {Promise} 更新后的测量记录
 */
export async function updateMeasurement(measurementId, data) {
  const response = await http.put(`/api/measurements/${measurementId}`, data)
  return response.data
}

/**
 * 删除测量记录（需要管理员权限）
 * @param {number} measurementId - 测量记录ID
 * @returns {Promise}
 */
export async function deleteMeasurement(measurementId) {
  const response = await http.delete(`/api/measurements/${measurementId}`)
  return response.data
}

/**
 * 获取健康状态
 * @returns {Promise} 健康状态信息
 */
export async function getHealthStatus() {
  const response = await http.get('/api/health')
  return response.data
}

/**
 * 获取API基本信息
 * @returns {Promise} API基本信息
 */
export async function getApiInfo() {
  const response = await http.get('/')
  return response.data
}
