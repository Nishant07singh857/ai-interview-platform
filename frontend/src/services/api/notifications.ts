import { apiClient } from './client'

export const notificationService = {
  // Get notifications
  getNotifications: async (limit: number = 50, offset: number = 0) => {
    return apiClient.get(`/notifications?limit=${limit}&offset=${offset}`)
  },

  // Mark as read
  markAsRead: async (notificationId: string) => {
    return apiClient.post(`/notifications/${notificationId}/read`)
  },

  // Mark all as read
  markAllAsRead: async () => {
    return apiClient.post('/notifications/read-all')
  },

  // Delete notification
  deleteNotification: async (notificationId: string) => {
    return apiClient.delete(`/notifications/${notificationId}`)
  },

  // Get preferences
  getPreferences: async () => {
    return apiClient.get('/notifications/preferences')
  },

  // Update preferences
  updatePreferences: async (preferences: {
    email?: boolean
    push?: boolean
    dailyReminder?: boolean
    weeklyReport?: boolean
  }) => {
    return apiClient.put('/notifications/preferences', preferences)
  },

  // Subscribe to push notifications
  subscribePush: async (subscription: PushSubscription) => {
    return apiClient.post('/notifications/push/subscribe', subscription)
  },

  // Unsubscribe from push notifications
  unsubscribePush: async () => {
    return apiClient.post('/notifications/push/unsubscribe')
  },
}