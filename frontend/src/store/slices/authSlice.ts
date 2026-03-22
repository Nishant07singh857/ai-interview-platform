import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
import { authService } from '@/services/api/auth'
import { setAuthToken } from '@/services/api/client'
import { User } from '@/types'
import toast from 'react-hot-toast'

interface AuthState {
  user: User | null
  isLoading: boolean
  error: string | null
  isAuthenticated: boolean
  token: string | null
  refreshToken: string | null
  sessionExpiresAt: string | null
}

const initialState: AuthState = {
  user: null,
  isLoading: false,
  error: null,
  isAuthenticated: false,
  token: null,
  refreshToken: null,
  sessionExpiresAt: null,
}

// Async thunks
export const login = createAsyncThunk(
  'auth/login',
  async ({ email, password }: { email: string; password: string }, { rejectWithValue }) => {
    try {
      const response = await authService.login(email, password)
      setAuthToken(response.data.access_token)
      
      if (typeof window !== 'undefined') {
        const sessionExpiresAt = new Date(Date.now() + response.data.expires_in * 1000).toISOString()
        localStorage.setItem('auth.accessToken', response.data.access_token)
        localStorage.setItem('auth.refreshToken', response.data.refresh_token)
        localStorage.setItem('auth.sessionExpiresAt', sessionExpiresAt)
      }
      
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Login failed')
    }
  }
)

export const register = createAsyncThunk(
  'auth/register',
  async (userData: { email: string; password: string; displayName?: string }, { rejectWithValue }) => {
    try {
      const response = await authService.register(userData)
      toast.success('Registration successful! Please verify your email.')
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Registration failed')
    }
  }
)

export const logout = createAsyncThunk('auth/logout', async (_, { rejectWithValue }) => {
  try {
    await authService.logout()
    setAuthToken(null)
    
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth.accessToken')
      localStorage.removeItem('auth.refreshToken')
      localStorage.removeItem('auth.sessionExpiresAt')
    }
    
    toast.success('Logged out successfully')
  } catch (error: any) {
    return rejectWithValue(error.response?.data?.detail || 'Logout failed')
  }
})

export const refreshToken = createAsyncThunk('auth/refreshToken', async (_, { rejectWithValue }) => {
  try {
    const response = await authService.refreshToken()
    setAuthToken(response.data.access_token)
    
    if (typeof window !== 'undefined') {
      const sessionExpiresAt = new Date(Date.now() + response.data.expires_in * 1000).toISOString()
      localStorage.setItem('auth.accessToken', response.data.access_token)
      localStorage.setItem('auth.refreshToken', response.data.refresh_token)
      localStorage.setItem('auth.sessionExpiresAt', sessionExpiresAt)
    }
    
    return response.data
  } catch (error: any) {
    return rejectWithValue(error.response?.data?.detail || 'Token refresh failed')
  }
})

export const verifyEmail = createAsyncThunk(
  'auth/verifyEmail',
  async (token: string, { rejectWithValue }) => {
    try {
      const response = await authService.verifyEmail(token)
      toast.success('Email verified successfully!')
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Email verification failed')
    }
  }
)

export const forgotPassword = createAsyncThunk(
  'auth/forgotPassword',
  async (email: string, { rejectWithValue }) => {
    try {
      const response = await authService.forgotPassword(email)
      toast.success('Password reset email sent!')
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to send reset email')
    }
  }
)

export const resetPassword = createAsyncThunk(
  'auth/resetPassword',
  async ({ token, newPassword }: { token: string; newPassword: string }, { rejectWithValue }) => {
    try {
      const response = await authService.resetPassword(token, newPassword)
      toast.success('Password reset successfully!')
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Password reset failed')
    }
  }
)

export const changePassword = createAsyncThunk(
  'auth/changePassword',
  async ({ currentPassword, newPassword }: { currentPassword: string; newPassword: string }, { rejectWithValue }) => {
    try {
      const response = await authService.changePassword(currentPassword, newPassword)
      toast.success('Password changed successfully!')
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Password change failed')
    }
  }
)

export const setupMFA = createAsyncThunk('auth/setupMFA', async (_, { rejectWithValue }) => {
  try {
    const response = await authService.setupMFA()
    return response.data
  } catch (error: any) {
    return rejectWithValue(error.response?.data?.detail || 'MFA setup failed')
  }
})

export const verifyMFA = createAsyncThunk(
  'auth/verifyMFA',
  async (code: string, { rejectWithValue }) => {
    try {
      const response = await authService.verifyMFA(code)
      toast.success('MFA enabled successfully!')
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'MFA verification failed')
    }
  }
)

export const disableMFA = createAsyncThunk('auth/disableMFA', async (_, { rejectWithValue }) => {
  try {
    const response = await authService.disableMFA()
    toast.success('MFA disabled successfully!')
    return response.data
  } catch (error: any) {
    return rejectWithValue(error.response?.data?.detail || 'MFA disable failed')
  }
})

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setCredentials: (
      state,
      action: PayloadAction<{
        user: User | null
        token: string
        refreshToken: string
        expiresIn: number
      }>
    ) => {
      state.user = action.payload.user
      state.token = action.payload.token
      state.refreshToken = action.payload.refreshToken
      state.isAuthenticated = true
      state.sessionExpiresAt = new Date(Date.now() + action.payload.expiresIn * 1000).toISOString()
      state.error = null
    },
    hydrateSession: (
      state,
      action: PayloadAction<{
        token: string
        refreshToken?: string | null
        sessionExpiresAt?: string | null
        user?: User | null
      }>
    ) => {
      state.token = action.payload.token
      state.refreshToken = action.payload.refreshToken ?? state.refreshToken
      state.sessionExpiresAt = action.payload.sessionExpiresAt ?? state.sessionExpiresAt
      state.user = action.payload.user ?? state.user
      state.isAuthenticated = true
      state.error = null
    },
    clearCredentials: (state) => {
      state.user = null
      state.token = null
      state.refreshToken = null
      state.isAuthenticated = false
      state.sessionExpiresAt = null
    },
    updateUser: (state, action: PayloadAction<Partial<User>>) => {
      if (state.user) {
        state.user = { ...state.user, ...action.payload }
      }
    },
    setError: (state, action: PayloadAction<string>) => {
      state.error = action.payload
    },
    clearError: (state) => {
      state.error = null
    },
  },
  extraReducers: (builder) => {
    // Login
    builder.addCase(login.pending, (state) => {
      state.isLoading = true
      state.error = null
    })
    builder.addCase(login.fulfilled, (state, action) => {
      state.isLoading = false
      state.user = action.payload.user
      state.token = action.payload.access_token
      state.refreshToken = action.payload.refresh_token
      state.isAuthenticated = true
      state.sessionExpiresAt = new Date(Date.now() + action.payload.expires_in * 1000).toISOString()
    })
    builder.addCase(login.rejected, (state, action) => {
      state.isLoading = false
      state.error = action.payload as string
    })

    // Register
    builder.addCase(register.pending, (state) => {
      state.isLoading = true
      state.error = null
    })
    builder.addCase(register.fulfilled, (state) => {
      state.isLoading = false
    })
    builder.addCase(register.rejected, (state, action) => {
      state.isLoading = false
      state.error = action.payload as string
    })

    // Logout
    builder.addCase(logout.pending, (state) => {
      state.isLoading = true
    })
    builder.addCase(logout.fulfilled, (state) => {
      state.isLoading = false
      state.user = null
      state.token = null
      state.refreshToken = null
      state.isAuthenticated = false
      state.sessionExpiresAt = null
    })
    builder.addCase(logout.rejected, (state) => {
      state.isLoading = false
      // Still clear credentials even if API call fails
      state.user = null
      state.token = null
      state.refreshToken = null
      state.isAuthenticated = false
      state.sessionExpiresAt = null
    })

    // Refresh Token
    builder.addCase(refreshToken.fulfilled, (state, action) => {
      state.token = action.payload.access_token
      state.refreshToken = action.payload.refresh_token
      state.sessionExpiresAt = new Date(Date.now() + action.payload.expires_in * 1000).toISOString()
    })

    // Verify Email
    builder.addCase(verifyEmail.fulfilled, (state) => {
      if (state.user) {
        state.user.emailVerified = true
      }
    })

    // MFA Setup
    builder.addCase(setupMFA.fulfilled, (state, action) => {
      // Handle MFA setup data
    })
    builder.addCase(verifyMFA.fulfilled, (state) => {
      if (state.user) {
        state.user.mfaEnabled = true
      }
    })
    builder.addCase(disableMFA.fulfilled, (state) => {
      if (state.user) {
        state.user.mfaEnabled = false
      }
    })
  },
})

export const { setCredentials, hydrateSession, clearCredentials, updateUser, setError, clearError } = authSlice.actions
export default authSlice.reducer