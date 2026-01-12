<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h1>智慧水利监测平台</h1>
        <p>水利工程安全监测与数据分析系统</p>
      </div>
      
      <div class="login-form">
        <el-form
          ref="loginFormRef"
          :model="loginForm"
          :rules="loginRules"
          label-width="80px"
          size="large"
        >
          <el-form-item label="用户名" prop="username">
            <el-input
              v-model="loginForm.username"
              placeholder="请输入用户名"
              :prefix-icon="User"
            />
          </el-form-item>
          
          <el-form-item label="密码" prop="password">
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="请输入密码"
              :prefix-icon="Lock"
              show-password
              @keyup.enter="handleLogin"
            />
          </el-form-item>
          
          <el-form-item>
            <el-button
              type="primary"
              size="large"
              :loading="loading"
              @click="handleLogin"
              style="width: 100%;"
            >
              登录
            </el-button>
          </el-form-item>
        </el-form>
        
        <div class="login-tips">
          <p><strong>测试账号：</strong></p>
          <p>管理员：admin / admin123</p>
          <p>普通用户：user / user123</p>
        </div>
      </div>
      
      <div class="login-footer">
        <p>© 2024 河海大学智慧水利研究中心</p>
      </div>
    </div>
    
    <!-- 背景装饰 -->
    <div class="login-background">
      <div class="bg-water"></div>
      <div class="bg-dam"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { login, isAdmin } from '../api/auth.js'

const router = useRouter()
const loginFormRef = ref()
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  try {
    await loginFormRef.value.validate()
    loading.value = true
    
    // 调用登录API
    await login(loginForm.username, loginForm.password)
    
    ElMessage.success('登录成功')
    
    // 所有用户登录后都跳转到监控页面
    router.push('/monitor')
  } catch (error) {
    console.error('登录失败:', error)
    if (error.response?.data?.message) {
      ElMessage.error(`登录失败: ${error.response.data.message}`)
    } else {
      ElMessage.error('登录失败，请检查用户名和密码')
    }
  } finally {
    loading.value = false
  }
}

// 如果已经登录，直接跳转到监控页面
import { isAuthenticated } from '../api/auth.js'
if (isAuthenticated()) {
  router.push('/monitor')
}
</script>

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
  position: relative;
  overflow: hidden;
}

.login-card {
  width: 420px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  z-index: 10;
  position: relative;
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.login-header h1 {
  font-size: 28px;
  font-weight: 700;
  color: #1e3c72;
  margin-bottom: 8px;
}

.login-header p {
  font-size: 14px;
  color: #666;
}

.login-form {
  margin-bottom: 30px;
}

.login-tips {
  background: #f0f7ff;
  border-radius: 8px;
  padding: 16px;
  font-size: 13px;
  color: #555;
  border-left: 4px solid #1e3c72;
}

.login-tips p {
  margin: 4px 0;
}

.login-footer {
  text-align: center;
  padding-top: 20px;
  border-top: 1px solid #eee;
  font-size: 12px;
  color: #888;
}

.login-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1;
}

.bg-water {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 200px;
  background: linear-gradient(to top, rgba(30, 60, 114, 0.8), rgba(42, 82, 152, 0.3));
  clip-path: polygon(0% 100%, 100% 100%, 100% 30%, 90% 40%, 80% 20%, 70% 50%, 60% 30%, 50% 60%, 40% 40%, 30% 70%, 20% 50%, 10% 80%, 0% 60%);
}

.bg-dam {
  position: absolute;
  bottom: 150px;
  left: 50%;
  transform: translateX(-50%);
  width: 300px;
  height: 100px;
  background: linear-gradient(45deg, #4a6fa5, #2a5298);
  clip-path: polygon(0% 100%, 10% 0%, 90% 0%, 100% 100%);
  opacity: 0.6;
}
</style>
