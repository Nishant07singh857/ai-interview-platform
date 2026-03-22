import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
import { notificationService } from '@/services/api/notifications'
import toast from 'react-hot-toast'

interface Notification {
  id: string
  type: 'info' | 'success' | 'warning' | 'error'
  title: string
  message: string
  link?: string
  read: boolean
  createdAt: string
}

interface NotificationState {
  notifications: Notification[]
  unreadCount: number
  preferences: {
    email: boolean
    push: boolean
    dailyReminder: boolean
    weeklyReport: boolean
  }
  isLoading: boolean
  error: string | null
}

const initialState: NotificationState = {
  notifications: [],
  unreadCount: 0,
  preferences: {
    email: true,
    push: true,
    dailyReminder: true,
    weeklyReport: true,
  },
  isLoading: false,
  error: null,
}

// Async thunks
export const fetchNotifications = createAsyncThunk(
  'notifications/fetchAll',
  async (limit: number = 50, { rejectWithValue }) => {
    try {
      const response = await notificationService.getNotifications(limit)
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch notifications')
    }
  }
)

export const markAsRead = createAsyncThunk(
  'notifications/markRead',
  async (notificationId: string, { rejectWithValue }) => {
    try {
      const response = await notificationService.markAsRead(notificationId)
      return { id: notificationId, ...response.data }
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to mark as read')
    }
  }
)

export const markAllAsRead = createAsyncThunk('notifications/markAllRead', async (_, { rejectWithValue }) => {
  try {
    const response = await notificationService.markAllAsRead()
    return response.data
  } catch (error: any) {
    return rejectWithValue(error.response?.data?.detail || 'Failed to mark all as read')
  }
})

export const deleteNotification = createAsyncThunk(
  'notifications/delete',
  async (notificationId: string, { rejectWithValue }) => {
    try {
      await notificationService.deleteNotification(notificationId)
      return notificationId
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to delete notification')
    }
  }
)

export const fetchPreferences = createAsyncThunk('notifications/fetchPreferences', async (_, { rejectWithValue }) => {
  try {
    const response = await notificationService.getPreferences()
    return response.data
  } catch (error: any) {
    return rejectWithValue(error.response?.data?.detail || 'Failed to fetch preferences')
  }
})

export const updatePreferences = createAsyncThunk(
  'notifications/updatePreferences',
  async (preferences: Partial<NotificationState['preferences']>, { rejectWithValue }) => {
    try {
      const response = await notificationService.updatePreferences(preferences)
      toast.success('Notification preferences updated!')
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to update preferences')
    }
  }
)

const notificationSlice = createSlice({
  name: 'notifications',
  initialState,
  reducers: {
    addNotification: (state, action: PayloadAction<Notification>) => {
      state.notifications.unshift(action.payload)
      state.unreadCount += 1
    },
    clearNotifications: (state) => {
      state.notifications = []
      state.unreadCount = 0
    },
  },
  extraReducers: (builder) => {
    // Fetch Notifications
    builder.addCase(fetchNotifications.pending, (state) => {
      state.isLoading = true
    })
    builder.addCase(fetchNotifications.fulfilled, (state, action) => {
      state.isLoading = false
      state.notifications = action.payload.notifications || []
      state.unreadCount = action.payload.unread_count || 0
    })
    builder.addCase(fetchNotifications.rejected, (state, action) => {
      state.isLoading = false
      state.error = action.payload as string
    })

    // Mark as Read
    builder.addCase(markAsRead.fulfilled, (state, action) => {
      const notification = state.notifications.find(n => n.id === action.payload.id)
      if (notification && !notification.read) {
        notification.read = true
        state.unreadCount = Math.max(0, state.unreadCount - 1)
      }
    })

    // Mark All as Read
    builder.addCase(markAllAsRead.fulfilled, (state) => {
      state.notifications.forEach(n => { n.read = true })
      state.unreadCount = 0
    })

    // Delete Notification
    builder.addCase(deleteNotification.fulfilled, (state, action) => {
      const index = state.notifications.findIndex(n => n.id === action.payload)
      if (index !== -1) {
        if (!state.notifications[index].read) {
          state.unreadCount = Math.max(0, state.unreadCount - 1)
        }
        state.notifications.splice(index, 1)
      }
    })

    // Fetch Preferences
    builder.addCase(fetchPreferences.fulfilled, (state, action) => {
      state.preferences = { ...state.preferences, ...action.payload }
    })

    // Update Preferences
    builder.addCase(updatePreferences.fulfilled, (state, action) => {
      state.preferences = { ...state.preferences, ...action.payload }
    })
  },
})

export const { addNotification, clearNotifications } = notificationSlice.actions
export default notificationSlice.reducer
