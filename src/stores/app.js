import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', {
  state: () => ({
    isLoading: false,
    currentScene: null,
    sceneList: [],
    currentTheme: 'night'
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
    }
  },
  
  getters: {
    isSceneLoaded: (state) => !!state.currentScene
  }
}) 