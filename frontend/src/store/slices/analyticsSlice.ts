import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
import { analyticsService } from '@/services/api/analytics'
import {
  AnalyticsSummary,
  PerformanceTrend,
  TopicMastery,
  CompanyReadiness,
} from '@/types'

interface AnalyticsState {
  summary: AnalyticsSummary | null
  trends: PerformanceTrend | null
  subjectPerformance: any | null
  topicMastery: TopicMastery | null
  companyReadiness: CompanyReadiness[]
  difficultyPerformance: any | null
  questionTypePerformance: any | null
  timeAnalysis: any | null
  weakTopics: any[]
  strongTopics: any[]
  weeklyReport: any | null
  learningPath: any | null
  peerComparison: any | null
  predictions: any | null
  skillGaps: any[]
  recommendations: any[]
  streakInfo: any | null
  recentActivity: any[]
  heatmap: any | null
  milestones: any[]
  isLoading: boolean
  error: string | null
}

const initialState: AnalyticsState = {
  summary: null,
  trends: null,
  subjectPerformance: null,
  topicMastery: null,
  companyReadiness: [],
  difficultyPerformance: null,
  questionTypePerformance: null,
  timeAnalysis: null,
  weakTopics: [],
  strongTopics: [],
  weeklyReport: null,
  learningPath: null,
  peerComparison: null,
  predictions: null,
  skillGaps: [],
  recommendations: [],
  streakInfo: null,
  recentActivity: [],
  heatmap: null,
  milestones: [],
  isLoading: false,
  error: null,
}

// Async thunks
export const fetchAnalyticsSummary = createAsyncThunk('analytics/fetchSummary', async (_, { rejectWithValue }) => {
  try {
    const response = await analyticsService.getSummary()
    return response.data
  } catch (error: any) {
    return rejectWithValue(error.response?.data?.detail || 'Failed to fetch analytics')
  }
})

export const fetchPerformanceTrends = createAsyncThunk(
  'analytics/fetchTrends',
  async (days: number = 30, { rejectWithValue }) => {
    try {
      const response = await analyticsService.getTrends(days)
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch trends')
    }
  }
)

export const fetchSubjectPerformance = createAsyncThunk(
  'analytics/fetchSubjectPerformance',
  async (_, { rejectWithValue }) => {
    try {
      const response = await analyticsService.getSubjectPerformance()
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch subject performance')
    }
  }
)

export const fetchTopicMastery = createAsyncThunk(
  'analytics/fetchTopicMastery',
  async (subject: string | undefined = undefined, { rejectWithValue }) => {
    try {
      const response = await analyticsService.getTopicMastery(subject)
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch topic mastery')
    }
  }
)

export const fetchCompanyReadiness = createAsyncThunk(
  'analytics/fetchCompanyReadiness',
  async (_, { rejectWithValue }) => {
    try {
      const response = await analyticsService.getCompanyReadiness()
      return response.data
    } catch (error: any) {
      const status = error?.response?.status
      if (status === 403) {
        return { companies: [] }
      }
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch company readiness')
    }
  }
)

export const fetchDifficultyPerformance = createAsyncThunk(
  'analytics/fetchDifficultyPerformance',
  async (_, { rejectWithValue }) => {
    try {
      const response = await analyticsService.getDifficultyPerformance()
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch difficulty performance')
    }
  }
)

export const fetchQuestionTypePerformance = createAsyncThunk(
  'analytics/fetchQuestionTypePerformance',
  async (_, { rejectWithValue }) => {
    try {
      const response = await analyticsService.getQuestionTypePerformance()
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch question type performance')
    }
  }
)

export const fetchTimeAnalysis = createAsyncThunk(
  'analytics/fetchTimeAnalysis',
  async (_, { rejectWithValue }) => {
    try {
      const response = await analyticsService.getTimeAnalysis()
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch time analysis')
    }
  }
)

export const fetchWeeklyReport = createAsyncThunk(
  'analytics/fetchWeeklyReport',
  async (weekStart: string | undefined = undefined, { rejectWithValue }) => {
    try {
      const response = await analyticsService.getWeeklyReport(weekStart)
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch weekly report')
    }
  }
)

export const generateLearningPath = createAsyncThunk(
  'analytics/generateLearningPath',
  async ({ targetRole, targetCompanies }: { targetRole?: string; targetCompanies?: string[] }, { rejectWithValue }) => {
    try {
      const response = await analyticsService.generateLearningPath(targetRole, targetCompanies)
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to generate learning path')
    }
  }
)

export const compareWithPeers = createAsyncThunk(
  'analytics/compareWithPeers',
  async ({ peerGroup, subjects }: { peerGroup?: string; subjects?: string[] }, { rejectWithValue }) => {
    try {
      const response = await analyticsService.compareWithPeers(peerGroup, subjects)
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to compare with peers')
    }
  }
)

export const fetchPredictions = createAsyncThunk('analytics/fetchPredictions', async (_, { rejectWithValue }) => {
  try {
    const response = await analyticsService.getPredictions()
    return response.data
  } catch (error: any) {
    return rejectWithValue(error.response?.data?.detail || 'Failed to fetch predictions')
  }
})

export const fetchSkillGaps = createAsyncThunk(
  'analytics/fetchSkillGaps',
  async (targetRole: string | undefined = undefined, { rejectWithValue }) => {
    try {
      const response = await analyticsService.getSkillGaps(targetRole)
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch skill gaps')
    }
  }
)

export const fetchRecommendations = createAsyncThunk(
  'analytics/fetchRecommendations',
  async (limit: number = 5, { rejectWithValue }) => {
    try {
      const response = await analyticsService.getRecommendations(limit)
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch recommendations')
    }
  }
)

export const fetchStreakInfo = createAsyncThunk('analytics/fetchStreakInfo', async (_, { rejectWithValue }) => {
  try {
    const response = await analyticsService.getStreakInfo()
    return response.data
  } catch (error: any) {
    return rejectWithValue(error.response?.data?.detail || 'Failed to fetch streak info')
  }
})

export const fetchActivityHeatmap = createAsyncThunk(
  'analytics/fetchHeatmap',
  async (year: number | undefined = undefined, { rejectWithValue }) => {
    try {
      const response = await analyticsService.getActivityHeatmap(year)
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch heatmap')
    }
  }
)

export const fetchMilestones = createAsyncThunk('analytics/fetchMilestones', async (_, { rejectWithValue }) => {
  try {
    const response = await analyticsService.getMilestones()
    return response.data
  } catch (error: any) {
    return rejectWithValue(error.response?.data?.detail || 'Failed to fetch milestones')
  }
})

export const fetchDashboardData = createAsyncThunk('analytics/fetchDashboardData', async (_, { rejectWithValue }) => {
  try {
    const response = await analyticsService.getDashboardData()
    return response.data
  } catch (error: any) {
    return rejectWithValue(error.response?.data?.detail || 'Failed to fetch dashboard data')
  }
})

export const exportAnalytics = createAsyncThunk(
  'analytics/export',
  async ({ format, timeframe }: { format: string; timeframe?: string }, { rejectWithValue }) => {
    try {
      const response = await analyticsService.exportAnalytics(format, timeframe)
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to export analytics')
    }
  }
)

const analyticsSlice = createSlice({
  name: 'analytics',
  initialState,
  reducers: {
    clearAnalyticsData: (state) => {
      state.summary = null
      state.trends = null
      state.subjectPerformance = null
      state.topicMastery = null
      state.companyReadiness = []
      state.recommendations = []
    },
    clearError: (state) => {
      state.error = null
    },
  },
  extraReducers: (builder) => {
    // Fetch Summary
    builder.addCase(fetchAnalyticsSummary.pending, (state) => {
      state.isLoading = true
    })
    builder.addCase(fetchAnalyticsSummary.fulfilled, (state, action) => {
      state.isLoading = false
      state.summary = action.payload
    })
    builder.addCase(fetchAnalyticsSummary.rejected, (state, action) => {
      state.isLoading = false
      state.error = action.payload as string
    })

    // Fetch Trends
    builder.addCase(fetchPerformanceTrends.fulfilled, (state, action) => {
      state.trends = action.payload
    })

    // Fetch Subject Performance
    builder.addCase(fetchSubjectPerformance.fulfilled, (state, action) => {
      state.subjectPerformance = action.payload
    })

    // Fetch Topic Mastery
    builder.addCase(fetchTopicMastery.fulfilled, (state, action) => {
      state.topicMastery = action.payload
    })

    // Fetch Company Readiness
    builder.addCase(fetchCompanyReadiness.fulfilled, (state, action) => {
      state.companyReadiness = action.payload.companies || []
    })

    // Fetch Difficulty Performance
    builder.addCase(fetchDifficultyPerformance.fulfilled, (state, action) => {
      state.difficultyPerformance = action.payload
    })

    // Fetch Question Type Performance
    builder.addCase(fetchQuestionTypePerformance.fulfilled, (state, action) => {
      state.questionTypePerformance = action.payload
    })

    // Fetch Time Analysis
    builder.addCase(fetchTimeAnalysis.fulfilled, (state, action) => {
      state.timeAnalysis = action.payload
    })

    // Fetch Weekly Report
    builder.addCase(fetchWeeklyReport.fulfilled, (state, action) => {
      state.weeklyReport = action.payload
    })

    // Generate Learning Path
    builder.addCase(generateLearningPath.fulfilled, (state, action) => {
      state.learningPath = action.payload
    })

    // Compare with Peers
    builder.addCase(compareWithPeers.fulfilled, (state, action) => {
      state.peerComparison = action.payload
    })

    // Fetch Predictions
    builder.addCase(fetchPredictions.fulfilled, (state, action) => {
      state.predictions = action.payload
    })

    // Fetch Skill Gaps
    builder.addCase(fetchSkillGaps.fulfilled, (state, action) => {
      state.skillGaps = action.payload.skill_gaps || []
    })

    // Fetch Recommendations
    builder.addCase(fetchRecommendations.fulfilled, (state, action) => {
      state.recommendations = action.payload.recommendations || []
    })

    // Fetch Streak Info
    builder.addCase(fetchStreakInfo.fulfilled, (state, action) => {
      state.streakInfo = action.payload
    })

    // Fetch Heatmap
    builder.addCase(fetchActivityHeatmap.fulfilled, (state, action) => {
      state.heatmap = action.payload
    })

    // Fetch Milestones
    builder.addCase(fetchMilestones.fulfilled, (state, action) => {
      state.milestones = action.payload.milestones || []
    })

    // Fetch Dashboard Data
    builder.addCase(fetchDashboardData.fulfilled, (state, action) => {
      state.summary = action.payload.summary
      state.trends = action.payload.trends
      state.subjectPerformance = action.payload.subjectPerformance
      state.weakTopics = action.payload.weakTopics
      state.strongTopics = action.payload.strongTopics
      state.streakInfo = action.payload.streak
      state.recommendations = action.payload.recommendations
      state.recentActivity = action.payload.recentActivity || action.payload.recent_activity || []
      if (action.payload.companyReadiness) {
        state.companyReadiness = action.payload.companyReadiness
      }
    })
  },
})

export const { clearAnalyticsData, clearError } = analyticsSlice.actions
export default analyticsSlice.reducer
