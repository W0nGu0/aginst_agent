import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', {
  state: () => ({
    isLoading: false,
    currentScene: null,
    sceneList: [],
    currentTheme: 'night',
    user: null,
    isAuthenticated: false
  }),
  
  actions: {
    setLoading(status) {
      this.isLoading = status
    },
    
    setCurrentScene(scene) {
      this.currentScene = scene
    },
    
    setSceneList(list) {
      this.sceneList = list
    },
    
    toggleTheme() {
      this.currentTheme = this.currentTheme === 'night' ? 'light' : 'night'
      document.documentElement.setAttribute('data-theme', this.currentTheme)
    },

    login(username) {
      this.user = username
      this.isAuthenticated = true
    },

    logout() {
      this.user = null
      this.isAuthenticated = false
    }
  },
  
  getters: {
    isSceneLoaded: (state) => !!state.currentScene
  }
}) 