import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
import { userService } from '@/services/api/user'
import { User, UserStats, UserPreferences, Skill } from '@/types'
import toast from 'react-hot-toast'

interface UserState {
  profile: User | null
  stats: UserStats | null
  preferences: UserPreferences | null
  skills: Record<string, Skill[]>
  recentActivity: any[]
  isLoading: boolean
  error: string | null
}

const initialState: UserState = {
  profile: null,
  stats: null,
  preferences: null,
  skills: {
    technical: [],
    soft: [],
    domain: [],
    tools: [],
    languages: [],
  },
  recentActivity: [],
  isLoading: false,
  error: null,
}

// Async thunks
export const fetchUserProfile = createAsyncThunk('user/fetchProfile', async (_, { rejectWithValue }) => {
  try {
    const response = await userService.getProfile()
    return response.data
  } catch (error: any) {
    return rejectWithValue(error.response?.data?.detail || 'Failed to fetch profile')
  }
})

export const updateUserProfile = createAsyncThunk(
  'user/updateProfile',
  async (profileData: Partial<User>, { rejectWithValue }) => {
    try {
      const response = await userService.updateProfile(profileData)
      toast.success('Profile updated successfully!')
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to update profile')
    }
  }
)

export const fetchUserStats = createAsyncThunk('user/fetchStats', async (_, { rejectWithValue }) => {
  try {
    const response = await userService.getStats()
    return response.data
  } catch (error: any) {
    return rejectWithValue(error.response?.data?.detail || 'Failed to fetch stats')
  }
})

export const fetchUserPreferences = createAsyncThunk('user/fetchPreferences', async (_, { rejectWithValue }) => {
  try {
    const response = await userService.getPreferences()
    return response.data
  } catch (error: any) {
    return rejectWithValue(error.response?.data?.detail || 'Failed to fetch preferences')
  }
})

export const updateUserPreferences = createAsyncThunk(
  'user/updatePreferences',
  async (preferences: Partial<UserPreferences>, { rejectWithValue }) => {
    try {
      const response = await userService.updatePreferences(preferences)
      toast.success('Preferences updated!')
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to update preferences')
    }
  }
)

export const fetchUserSkills = createAsyncThunk('user/fetchSkills', async (_, { rejectWithValue }) => {
  try {
    const response = await userService.getSkills()
    return response.data
  } catch (error: any) {
    return rejectWithValue(error.response?.data?.detail || 'Failed to fetch skills')
  }
})

export const updateUserSkills = createAsyncThunk(
  'user/updateSkills',
  async (skills: Record<string, Skill[]>, { rejectWithValue }) => {
    try {
      const response = await userService.updateSkills(skills)
      toast.success('Skills updated!')
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to update skills')
    }
  }
)

export const fetchRecentActivity = createAsyncThunk(
  'user/fetchRecentActivity',
  async (limit: number = 10, { rejectWithValue }) => {
    try {
      const response = await userService.getRecentActivity(limit)
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch activity')
    }
  }
)

export const updateTargets = createAsyncThunk(
  'user/updateTargets',
  async (targets: { companies: string[]; roles: string[]; interviewDate?: string }, { rejectWithValue }) => {
    try {
      const response = await userService.updateTargets(targets)
      toast.success('Targets updated!')
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to update targets')
    }
  }
)

export const uploadProfilePicture = createAsyncThunk(
  'user/uploadProfilePicture',
  async (file: File, { rejectWithValue }) => {
    try {
      const response = await userService.uploadProfilePicture(file)
      toast.success('Profile picture updated!')
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to upload picture')
    }
  }
)

export const deleteAccount = createAsyncThunk('user/deleteAccount', async (_, { rejectWithValue }) => {
  try {
    const response = await userService.deleteAccount()
    toast.success('Account deleted successfully')
    return response.data
  } catch (error: any) {
    return rejectWithValue(error.response?.data?.detail || 'Failed to delete account')
  }
})

const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    clearUserData: (state) => {
      state.profile = null
      state.stats = null
      state.preferences = null
      state.skills = {
        technical: [],
        soft: [],
        domain: [],
        tools: [],
        languages: [],
      }
      state.recentActivity = []
    },
    updateLocalProfile: (state, action: PayloadAction<Partial<User>>) => {
      if (state.profile) {
        state.profile = { ...state.profile, ...action.payload }
      }
    },
  },
  extraReducers: (builder) => {
    // Fetch Profile
    builder.addCase(fetchUserProfile.pending, (state) => {
      state.isLoading = true
      state.error = null
    })
    builder.addCase(fetchUserProfile.fulfilled, (state, action) => {
      state.isLoading = false
      state.profile = action.payload
    })
    builder.addCase(fetchUserProfile.rejected, (state, action) => {
      state.isLoading = false
      state.error = action.payload as string
    })

    // Update Profile
    builder.addCase(updateUserProfile.pending, (state) => {
      state.isLoading = true
    })
    builder.addCase(updateUserProfile.fulfilled, (state, action) => {
      state.isLoading = false
      state.profile = { ...state.profile, ...action.payload }
    })
    builder.addCase(updateUserProfile.rejected, (state, action) => {
      state.isLoading = false
      state.error = action.payload as string
    })

    // Fetch Stats
    builder.addCase(fetchUserStats.fulfilled, (state, action) => {
      state.stats = action.payload
    })

    // Fetch Preferences
    builder.addCase(fetchUserPreferences.fulfilled, (state, action) => {
      state.preferences = action.payload
    })
    builder.addCase(updateUserPreferences.fulfilled, (state, action) => {
      state.preferences = { ...state.preferences, ...action.payload }
    })

    // Fetch Skills
    builder.addCase(fetchUserSkills.fulfilled, (state, action) => {
      state.skills = action.payload
    })
    builder.addCase(updateUserSkills.fulfilled, (state, action) => {
      state.skills = action.payload
    })

    // Fetch Recent Activity
    builder.addCase(fetchRecentActivity.fulfilled, (state, action) => {
      state.recentActivity = action.payload.activities || []
    })

    // Update Targets
    builder.addCase(updateTargets.fulfilled, (state, action) => {
      if (state.profile) {
        state.profile.targetCompanies = action.payload.targetCompanies
        state.profile.targetRoles = action.payload.targetRoles
        state.profile.targetInterviewDate = action.payload.targetInterviewDate
      }
    })

    // Upload Profile Picture
    builder.addCase(uploadProfilePicture.fulfilled, (state, action) => {
      if (state.profile) {
        state.profile.photoURL = action.payload.photo_url
      }
    })
  },
})

export const { clearUserData, updateLocalProfile } = userSlice.actions
export default userSlice.reducer