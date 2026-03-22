import { createSlice, PayloadAction } from '@reduxjs/toolkit'

interface UIState {
  theme: 'light' | 'dark' | 'system'
  sidebarOpen: boolean
  mobileMenuOpen: boolean
  modalOpen: boolean
  modalContent: string | null
  modalProps: Record<string, any>
  toast: {
    visible: boolean
    message: string
    type: 'success' | 'error' | 'info' | 'warning'
  }
  loading: {
    global: boolean
    overlay: boolean
    requests: number
  }
  viewMode: 'grid' | 'list'
  fontSize: 'small' | 'medium' | 'large'
  compactMode: boolean
  announcements: Array<{
    id: string
    message: string
    type: 'info' | 'success' | 'warning' | 'error'
    read: boolean
  }>
  lastNotification: number
}

const initialState: UIState = {
  theme: 'system',
  sidebarOpen: true,
  mobileMenuOpen: false,
  modalOpen: false,
  modalContent: null,
  modalProps: {},
  toast: {
    visible: false,
    message: '',
    type: 'info',
  },
  loading: {
    global: false,
    overlay: false,
    requests: 0,
  },
  viewMode: 'grid',
  fontSize: 'medium',
  compactMode: false,
  announcements: [],
  lastNotification: Date.now(),
}

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    setTheme: (state, action: PayloadAction<'light' | 'dark' | 'system'>) => {
      state.theme = action.payload
      localStorage.setItem('theme', action.payload)
    },
    toggleSidebar: (state) => {
      state.sidebarOpen = !state.sidebarOpen
    },
    setSidebarOpen: (state, action: PayloadAction<boolean>) => {
      state.sidebarOpen = action.payload
    },
    toggleMobileMenu: (state) => {
      state.mobileMenuOpen = !state.mobileMenuOpen
    },
    setMobileMenuOpen: (state, action: PayloadAction<boolean>) => {
      state.mobileMenuOpen = action.payload
    },
    openModal: (state, action: PayloadAction<{ content: string; props?: Record<string, any> }>) => {
      state.modalOpen = true
      state.modalContent = action.payload.content
      state.modalProps = action.payload.props || {}
    },
    closeModal: (state) => {
      state.modalOpen = false
      state.modalContent = null
      state.modalProps = {}
    },
    showToast: (state, action: PayloadAction<{ message: string; type?: 'success' | 'error' | 'info' | 'warning' }>) => {
      state.toast = {
        visible: true,
        message: action.payload.message,
        type: action.payload.type || 'info',
      }
    },
    hideToast: (state) => {
      state.toast.visible = false
    },
    startGlobalLoading: (state) => {
      state.loading.global = true
      state.loading.requests += 1
    },
    stopGlobalLoading: (state) => {
      state.loading.requests = Math.max(0, state.loading.requests - 1)
      state.loading.global = state.loading.requests > 0
    },
    setOverlayLoading: (state, action: PayloadAction<boolean>) => {
      state.loading.overlay = action.payload
    },
    setViewMode: (state, action: PayloadAction<'grid' | 'list'>) => {
      state.viewMode = action.payload
    },
    setFontSize: (state, action: PayloadAction<'small' | 'medium' | 'large'>) => {
      state.fontSize = action.payload
      document.documentElement.style.fontSize = 
        action.payload === 'small' ? '14px' : 
        action.payload === 'medium' ? '16px' : '18px'
    },
    setCompactMode: (state, action: PayloadAction<boolean>) => {
      state.compactMode = action.payload
    },
    addAnnouncement: (state, action: PayloadAction<{ id: string; message: string; type?: 'info' | 'success' | 'warning' | 'error' }>) => {
      state.announcements.unshift({
        id: action.payload.id,
        message: action.payload.message,
        type: action.payload.type || 'info',
        read: false,
      })
    },
    markAnnouncementRead: (state, action: PayloadAction<string>) => {
      const announcement = state.announcements.find(a => a.id === action.payload)
      if (announcement) {
        announcement.read = true
      }
    },
    clearAnnouncements: (state) => {
      state.announcements = []
    },
    updateLastNotification: (state) => {
      state.lastNotification = Date.now()
    },
    resetUI: () => initialState,
  },
})

export const {
  setTheme,
  toggleSidebar,
  setSidebarOpen,
  toggleMobileMenu,
  setMobileMenuOpen,
  openModal,
  closeModal,
  showToast,
  hideToast,
  startGlobalLoading,
  stopGlobalLoading,
  setOverlayLoading,
  setViewMode,
  setFontSize,
  setCompactMode,
  addAnnouncement,
  markAnnouncementRead,
  clearAnnouncements,
  updateLastNotification,
  resetUI,
} = uiSlice.actions

export default uiSlice.reducer