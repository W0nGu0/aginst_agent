<template>
  <LoginLayout title="找回密码">
    <form class="space-y-4 w-full" @submit.prevent="submit">
      <input v-model="username" type="text" placeholder="用户名 / 邮箱" class="input input-bordered w-full" />
      <button class="btn btn-primary w-full" type="submit">发送重置邮件</button>
    </form>
    <p v-if="msg" class="text-success text-sm text-center mt-2">{{ msg }}</p>
    <div class="text-sm text-center mt-4">
      <RouterLink to="/" class="text-primary hover:underline">返回登录</RouterLink>
    </div>
  </LoginLayout>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import LoginLayout from './LoginLayoutWrapper.vue'

const username = ref('')
const msg = ref('')

function submit() {
  if (!username.value) return
  msg.value = '如果账号存在，我们已向您的邮箱发送重置链接。'
}
</script> 