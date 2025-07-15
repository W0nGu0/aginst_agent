import { defineStore } from 'pinia'

export const useTopologyStore = defineStore('topology', {
  state: () => ({
    devices: {},
    connections: [],
    selectedObject: null,
    mode: 'select', // 'select', 'connect', 'pan'
    connecting: null,
    canvas: null,
    deviceColors: {
      'router': '#4CAF50',
      'firewall': '#F44336',
      'switch': '#2196F3',
      'server': '#FF9800',
      'pc': '#9C27B0',
      'ids': '#673AB7',
      'file': '#795548',
      'siem': '#607d8b',
      'vpn': '#009688',
      'db': '#3f51b5',
      'ubuntu': '#ff5722',
      'web': '#03a9f4',
      'dns': '#8bc34a',
      'mail': '#6d4c41',
      'cloud': '#00bcd4'
    },
    connectionTypes: {
      'ethernet': { color: '#2196F3', width: 2, dash: [] },
      'fiber': { color: '#FF9800', width: 2, dash: [] },
      'wireless': { color: '#4CAF50', width: 2, dash: [3, 3] }
    }
  }),
  
  actions: {
    setMode(mode) {
      if (['select', 'connect', 'pan'].includes(mode)) {
        this.mode = mode
        
        if (mode !== 'connect') {
          this.connecting = null
        }
        
        if (this.canvas) {
          if (mode === 'pan') {
            this.canvas.selection = false
            this.canvas.forEachObject(function(obj) {
              obj.selectable = false
            })
          } else {
            this.canvas.selection = true
            this.canvas.forEachObject(function(obj) {
              obj.selectable = true
            })
          }
        }
        
        return true
      }
      return false
    },
    
    setSelectedObject(object) {
      this.selectedObject = object
    },
    
    setCanvas(canvas) {
      this.canvas = canvas
    },
    
    addDevice(device, id) {
      this.devices[id] = device
    },
    
    removeDevice(id) {
      if (this.devices[id]) {
        delete this.devices[id]
      }
    },
    
    addConnection(connection) {
      this.connections.push(connection)
    },
    
    removeConnection(connection) {
      this.connections = this.connections.filter(conn => conn !== connection)
    },
    
    clearSelection() {
      this.selectedObject = null
      if (this.canvas) {
        this.canvas.discardActiveObject()
        this.canvas.requestRenderAll()
      }
    }
  },
  
  getters: {
    isConnectMode: (state) => state.mode === 'connect',
    isPanMode: (state) => state.mode === 'pan',
    hasSelection: (state) => !!state.selectedObject
  }
}) 