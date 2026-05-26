import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Chat from '../views/Chat.vue'

const routes = [
  {
    path: '/',
    name: 'Login',
    component: Login
  },
  {
    path: '/chat',
    name: 'Chat',
    component: Chat
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('chat_token')
  if (to.path === '/chat' && !token) {
    next('/')
  } else if (to.path === '/' && token) {
    next('/chat')
  } else {
    next()
  }
})

export default router