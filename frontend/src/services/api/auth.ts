import { apiClient } from './client'
import { ApiResponse } from '@/types'

export interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  user: any
}

export interface RegisterResponse {
  uid: string
  email: string
  display_name: string
  role: string
  created_at: string
}

export const authService = {
  // Login
  login: async (email: string, password: string) => {
    return apiClient.post<LoginResponse>('/auth/login', { email, password })
  },

  // Register
  register: async (data: { email: string; password: string; displayName?: string }) => {
    return apiClient.post<RegisterResponse>('/auth/register', data)
  },

  // Logout
  logout: async () => {
    return apiClient.post('/auth/logout')
  },

  // Refresh token
  refreshToken: async () => {
    return apiClient.post<LoginResponse>('/auth/refresh')
  },

  // Email verification
  verifyEmail: async (token: string) => {
    return apiClient.post('/auth/verify-email', { token })
  },

  // Resend verification email
  resendVerification: async (email: string) => {
    return apiClient.post('/auth/resend-verification', { email })
  },

  // Password reset
  forgotPassword: async (email: string) => {
    return apiClient.post('/auth/forgot-password', { email })
  },

  resetPassword: async (token: string, newPassword: string) => {
    return apiClient.post('/auth/reset-password', { token, new_password: newPassword })
  },

  // Change password (authenticated)
  changePassword: async (currentPassword: string, newPassword: string) => {
    return apiClient.post('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    })
  },

  // Get current user
  getCurrentUser: async () => {
    return apiClient.get('/auth/me')
  },

  // MFA
  setupMFA: async () => {
    return apiClient.post('/auth/mfa/setup')
  },

  verifyMFA: async (code: string) => {
    return apiClient.post('/auth/mfa/verify', { code })
  },

  disableMFA: async () => {
    return apiClient.post('/auth/mfa/disable')
  },

  // Sessions
  getActiveSessions: async () => {
    return apiClient.get('/auth/sessions')
  },

  revokeSession: async (sessionId: string) => {
    return apiClient.delete(`/auth/sessions/${sessionId}`)
  },

  logoutAll: async () => {
    return apiClient.post('/auth/logout-all')
  },
}