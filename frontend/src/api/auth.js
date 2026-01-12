/**
 * 认证API模块
 */
import axios from 'axios'

// 使用环境变量或默认值
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

// 创建axios实例
const http = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器：添加认证令牌
http.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器：处理令牌过期
http.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    
    // 如果是401错误且不是刷新令牌请求，尝试刷新令牌
    if (error.response?.status === 401 && !originalRequest._retry && originalRequest.url !== '/api/auth/refresh') {
      originalRequest._retry = true
      
      try {
        const refreshToken = localStorage.getItem('refresh_token')
        if (!refreshToken) {
          throw new Error('没有刷新令牌')
        }
        
        const response = await http.post('/api/auth/refresh', {
          refresh_token: refreshToken
        })
        
        const { access_token } = response.data.data
        localStorage.setItem('access_token', access_token)
        
        // 重试原始请求
        originalRequest.headers.Authorization = `Bearer ${access_token}`
        return http(originalRequest)
      } catch (refreshError) {
        // 刷新失败，清除本地存储并跳转到登录页
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('user_info')
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }
    
    return Promise.reject(error)
  }
)

/**
 * 用户登录
 * @param {string} username - 用户名
 * @param {string} password - 密码
 * @returns {Promise} 登录结果
 */
export async function login(username, password) {
  const response = await http.post('/api/auth/login', {
    username,
    password
  })
  
  const { access_token, refresh_token, user_info } = response.data.data
  
  // 保存令牌和用户信息
  localStorage.setItem('access_token', access_token)
  localStorage.setItem('refresh_token', refresh_token)
  localStorage.setItem('user_info', JSON.stringify(user_info))
  
  return response.data
}

/**
 * 用户登出
 */
export async function logout() {
  try {
    await http.post('/api/auth/logout')
  } finally {
    // 无论登出请求是否成功，都清除本地存储
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user_info')
  }
}

/**
 * 获取当前用户信息
 * @returns {Promise} 用户信息
 */
export async function getCurrentUser() {
  const response = await http.get('/api/auth/me')
  return response.data.data.user
}

/**
 * 刷新令牌
 * @param {string} refreshToken - 刷新令牌
 * @returns {Promise} 新的访问令牌
 */
export async function refreshToken(refreshToken) {
  const response = await http.post('/api/auth/refresh', {
    refresh_token: refreshToken
  })
  
  const { access_token } = response.data.data
  localStorage.setItem('access_token', access_token)
  
  return response.data
}

/**
 * 获取用户列表（仅管理员）
 * @returns {Promise} 用户列表
 */
export async function getUsers() {
  const response = await http.get('/api/auth/users')
  return response.data.data.users  // 返回用户数组
}

/**
 * 创建新用户（仅管理员）
 * @param {Object} userData - 用户数据
 * @param {string} userData.username - 用户名
 * @param {string} userData.password - 密码
 * @param {string} userData.name - 姓名
 * @param {string} userData.email - 邮箱
 * @param {string} userData.role - 角色（admin/user）
 * @returns {Promise} 创建结果
 */
export async function createUser(userData) {
  const response = await http.post('/api/auth/users', userData)
  return response.data
}

/**
 * 更新用户信息（仅管理员）
 * @param {number} userId - 用户ID
 * @param {Object} userData - 要更新的用户数据
 * @returns {Promise} 更新结果
 */
export async function updateUser(userId, userData) {
  const response = await http.put(`/api/auth/users/${userId}`, userData)
  return response.data
}

/**
 * 删除用户（仅管理员）
 * @param {number} userId - 用户ID
 * @returns {Promise} 删除结果
 */
export async function deleteUser(userId) {
  const response = await http.delete(`/api/auth/users/${userId}`)
  return response.data
}

/**
 * 检查用户是否已登录
 * @returns {boolean} 是否已登录
 */
export function isAuthenticated() {
  return !!localStorage.getItem('access_token')
}

/**
 * 获取当前用户角色
 * @returns {string|null} 用户角色（admin/user）或null
 */
export function getUserRole() {
  const userInfo = localStorage.getItem('user_info')
  if (!userInfo) return null
  
  try {
    const user = JSON.parse(userInfo)
    return user.role
  } catch {
    return null
  }
}

/**
 * 检查当前用户是否是管理员
 * @returns {boolean} 是否是管理员
 */
export function isAdmin() {
  return getUserRole() === 'admin'
}

export default http
