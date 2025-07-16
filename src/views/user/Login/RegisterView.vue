<template>
  <LoginLayout title="注册新账户">
    <form class="space-y-4 w-full" @submit.prevent="submit">
      <input v-model="username" type="text" placeholder="用户名" class="input input-bordered w-full" />
      <input v-model="password" type="password" placeholder="密码" class="input input-bordered w-full" />
      <input v-model="confirm" type="password" placeholder="确认密码" class="input input-bordered w-full" />
      <button class="btn btn-primary w-full" type="submit">注册</button>
    </form>
    <p v-if="errorMsg" class="text-error text-sm text-center mt-2">{{ errorMsg }}</p>
    <div class="text-sm text-center mt-4">
      <RouterLink to="/" class="text-primary hover:underline">已有账号? 去登录</RouterLink>
    </div>
  </LoginLayout>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import LoginLayout from './LoginLayoutWrapper.vue'

const router = useRouter()
const username = ref('')
const password = ref('')
const confirm = ref('')
const errorMsg = ref('')

function submit() {
  if (!username.value || !password.value) {
    errorMsg.value = '请完整填写表单'
    return
  }
  if (password.value !== confirm.value) {
    errorMsg.value = '两次密码不一致'
    return
  }
  // 简单模拟成功，跳转登录
  router.push('/')
}
</script> 