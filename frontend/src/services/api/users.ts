import { apiClient } from './client'
import { User, UserStats, UserPreferences, Skill } from '@/types'

export const userService = {
  // Profile
  getProfile: async () => {
    return apiClient.get<User>('/users/me')
  },

  updateProfile: async (data: Partial<User>) => {
    return apiClient.put<User>('/users/me', data)
  },

  deleteAccount: async () => {
    return apiClient.delete('/users/me')
  },

  // Profile picture
  uploadProfilePicture: async (file: File) => {
    return apiClient.upload('/users/me/profile-picture', file)
  },

  // Public profile
  getPublicProfile: async (userId: string) => {
    return apiClient.get(`/users/${userId}/profile`)
  },

  // Stats
  getStats: async () => {
    return apiClient.get<UserStats>('/users/me/stats')
  },

  // Preferences
  getPreferences: async () => {
    return apiClient.get<UserPreferences>('/users/me/preferences')
  },

  updatePreferences: async (preferences: Partial<UserPreferences>) => {
    return apiClient.put('/users/me/preferences', preferences)
  },

  // Skills
  getSkills: async () => {
    return apiClient.get<Record<string, Skill[]>>('/users/me/skills')
  },

  updateSkills: async (skills: Record<string, Skill[]>) => {
    return apiClient.put('/users/me/skills', skills)
  },

  // Targets
  updateTargets: async (targets: { companies: string[]; roles: string[]; interviewDate?: string }) => {
    return apiClient.put('/users/me/targets', targets)
  },

  // Progress
  getProgress: async (days: number = 30) => {
    return apiClient.get(`/users/me/progress?days=${days}`)
  },

  getRecentActivity: async (limit: number = 10) => {
    return apiClient.get(`/users/me/activity?limit=${limit}`)
  },

  // Achievements
  getAchievements: async () => {
    return apiClient.get('/users/me/achievements')
  },

  // Weak areas
  getWeakAreas: async () => {
    return apiClient.get('/users/me/weak-areas')
  },

  // Recommendations
  getRecommendations: async (limit: number = 10) => {
    return apiClient.get(`/users/me/recommendations?limit=${limit}`)
  },

  // Admin endpoints
  getAllUsers: async (skip: number = 0, limit: number = 50, role?: string) => {
    let url = `/users?skip=${skip}&limit=${limit}`
    if (role) url += `&role=${role}`
    return apiClient.get(url)
  },

  getUserById: async (userId: string) => {
    return apiClient.get(`/users/${userId}`)
  },

  updateUserRole: async (userId: string, role: string) => {
    return apiClient.put(`/users/${userId}/role`, { role })
  },

  suspendUser: async (userId: string, reason: string) => {
    return apiClient.post(`/users/${userId}/suspend`, { reason })
  },

  activateUser: async (userId: string) => {
    return apiClient.post(`/users/${userId}/activate`)
  },

  searchUsers: async (query: string, limit: number = 10) => {
    return apiClient.get(`/users/search/${query}?limit=${limit}`)
  },
}