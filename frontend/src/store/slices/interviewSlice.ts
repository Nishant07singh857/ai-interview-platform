import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
import { interviewService } from '@/services/api/interview'
import { InterviewSession, InterviewQuestion, InterviewFeedback } from '@/types'
import toast from 'react-hot-toast'

interface InterviewState {
  currentSession: InterviewSession | null
  sessions: InterviewSession[]
  currentQuestion: InterviewQuestion | null
  feedback: InterviewFeedback | null
  templates: any[]
  history: any[]
  voiceAnalysis: any | null
  videoAnalysis: any | null
  isLoading: boolean
  isRecording: boolean
  error: string | null
}

const initialState: InterviewState = {
  currentSession: null,
  sessions: [],
  currentQuestion: null,
  feedback: null,
  templates: [],
  history: [],
  voiceAnalysis: null,
  videoAnalysis: null,
  isLoading: false,
  isRecording: false,
  error: null,
}

// Async thunks
export const startInterview = createAsyncThunk(
  'interview/start',
  async (setup: {
    interviewType?: string;
    interviewMode?: string;
    difficulty?: string;
    durationMinutes?: number;
    companyFocus?: string;
    roleFocus?: string;
    categories?: string[];
  }, { rejectWithValue }) => {
    try {
      const response = await interviewService.startInterview(setup)
      return response.data
    } catch (error: any) {
      const status = error?.response?.status
      const message = error.response?.data?.detail || 'Failed to start interview'
      return rejectWithValue({ message, status })
    }
  }
)

export const startCompanyInterview = createAsyncThunk(
  'interview/startCompany',
  async ({ company, role, difficulty }: { company: string; role?: string; difficulty?: string }, { rejectWithValue }) => {
    try {
      const response = await interviewService.startCompanyInterview(company, role, difficulty)
      return response.data
    } catch (error: any) {
      const status = error?.response?.status
      const message = error.response?.data?.detail || 'Failed to start company interview'
      return rejectWithValue({ message, status })
    }
  }
)

export const fetchSession = createAsyncThunk(
  'interview/fetchSession',
  async (sessionId: string, { rejectWithValue }) => {
    try {
      const response = await interviewService.getSession(sessionId)
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch session')
    }
  }
)

export const pauseSession = createAsyncThunk(
  'interview/pause',
  async (sessionId: string, { rejectWithValue }) => {
    try {
      const response = await interviewService.pauseSession(sessionId)
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to pause interview')
    }
  }
)

export const resumeSession = createAsyncThunk(
  'interview/resume',
  async (sessionId: string, { rejectWithValue }) => {
    try {
      const response = await interviewService.resumeSession(sessionId)
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to resume interview')
    }
  }
)

export const endSession = createAsyncThunk(
  'interview/end',
  async (sessionId: string, { rejectWithValue }) => {
    try {
      const response = await interviewService.endSession(sessionId)
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to end interview')
    }
  }
)

export const getCurrentQuestion = createAsyncThunk(
  'interview/getCurrentQuestion',
  async (sessionId: string, { rejectWithValue }) => {
    try {
      const response = await interviewService.getCurrentQuestion(sessionId)
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to get question')
    }
  }
)

export const submitResponse = createAsyncThunk(
  'interview/submitResponse',
  async ({ sessionId, questionId, text, audio, timeTaken }: 
    { sessionId: string; questionId: string; text?: string; audio?: Blob; timeTaken: number }, 
    { rejectWithValue }
  ) => {
    try {
      const response = await interviewService.submitResponse(sessionId, questionId, timeTaken, text, audio)
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to submit response')
    }
  }
)

export const getHint = createAsyncThunk(
  'interview/getHint',
  async ({ sessionId, questionId }: { sessionId: string; questionId: string }, { rejectWithValue }) => {
    try {
      const response = await interviewService.getHint(sessionId, questionId)
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to get hint')
    }
  }
)

export const getFeedback = createAsyncThunk(
  'interview/getFeedback',
  async ({ sessionId, detailed }: { sessionId: string; detailed?: boolean }, { rejectWithValue }) => {
    try {
      const response = await interviewService.getFeedback(sessionId, detailed)
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to get feedback')
    }
  }
)

export const fetchTemplates = createAsyncThunk(
  'interview/fetchTemplates',
  async ({ mode, company }: { mode?: string; company?: string } = {}, { rejectWithValue }) => {
    try {
      const response = await interviewService.getTemplates(mode, company)
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch templates')
    }
  }
)

export const fetchHistory = createAsyncThunk(
  'interview/fetchHistory',
  async (limit: number = 10, { rejectWithValue }) => {
    try {
      const response = await interviewService.getHistory(limit)
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch history')
    }
  }
)

export const getVoiceAnalysis = createAsyncThunk(
  'interview/getVoiceAnalysis',
  async (responseId: string, { rejectWithValue }) => {
    try {
      const response = await interviewService.getVoiceAnalysis(responseId)
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to get voice analysis')
    }
  }
)

export const getVideoAnalysis = createAsyncThunk(
  'interview/getVideoAnalysis',
  async (responseId: string, { rejectWithValue }) => {
    try {
      const response = await interviewService.getVideoAnalysis(responseId)
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to get video analysis')
    }
  }
)

const interviewSlice = createSlice({
  name: 'interview',
  initialState,
  reducers: {
    setCurrentSession: (state, action: PayloadAction<InterviewSession>) => {
      state.currentSession = action.payload
    },
    setCurrentQuestion: (state, action: PayloadAction<InterviewQuestion>) => {
      state.currentQuestion = action.payload
    },
    setIsRecording: (state, action: PayloadAction<boolean>) => {
      state.isRecording = action.payload
    },
    clearCurrentSession: (state) => {
      state.currentSession = null
      state.currentQuestion = null
      state.feedback = null
    },
    clearError: (state) => {
      state.error = null
    },
  },
  extraReducers: (builder) => {
    // Start Interview
    builder.addCase(startInterview.pending, (state) => {
      state.isLoading = true
      state.error = null
    })
    builder.addCase(startInterview.fulfilled, (state, action) => {
      state.isLoading = false
      state.currentSession = action.payload
      state.currentQuestion = action.payload.currentQuestion ?? null
    })
    builder.addCase(startInterview.rejected, (state, action) => {
      state.isLoading = false
      const payload = action.payload as any
      const message = payload?.message || (action.payload as string)
      state.error = message
      if (message && payload?.status !== 403) {
        toast.error(message)
      }
    })

    // Start Company Interview
    builder.addCase(startCompanyInterview.fulfilled, (state, action) => {
      state.currentSession = action.payload
      state.currentQuestion = action.payload.currentQuestion ?? null
    })
    builder.addCase(startCompanyInterview.rejected, (state, action) => {
      const payload = action.payload as any
      const message = payload?.message || (action.payload as string)
      state.error = message
      if (message && payload?.status !== 403) {
        toast.error(message)
      }
    })

    // Fetch Session
    builder.addCase(fetchSession.fulfilled, (state, action) => {
      state.currentSession = action.payload
      if (action.payload.currentQuestion) {
        state.currentQuestion = action.payload.currentQuestion
      }
    })

    // Pause Session
    builder.addCase(pauseSession.fulfilled, (state) => {
      if (state.currentSession) {
        state.currentSession.status = 'paused'
      }
    })

    // Resume Session
    builder.addCase(resumeSession.fulfilled, (state, action) => {
      state.currentSession = action.payload
      state.currentQuestion = action.payload.currentQuestion ?? null
    })

    // End Session
    builder.addCase(endSession.fulfilled, (state) => {
      if (state.currentSession) {
        state.currentSession.status = 'completed'
        state.currentSession.completedAt = new Date().toISOString()
      }
    })

    // Get Current Question
    builder.addCase(getCurrentQuestion.fulfilled, (state, action) => {
      state.currentQuestion = action.payload
    })

    // Submit Response
    builder.addCase(submitResponse.fulfilled, (state, action) => {
      if (state.currentSession) {
        state.currentSession.questionsAnswered += 1
        
        if (action.payload.next_question) {
          state.currentQuestion = action.payload.next_question
        }
        
        if (action.payload.session_completed) {
          state.currentSession.status = 'completed'
        }
      }
    })

    // Get Hint
    builder.addCase(getHint.fulfilled, (state, action) => {
      // Handle hint display
    })

    // Get Feedback
    builder.addCase(getFeedback.fulfilled, (state, action) => {
      state.feedback = action.payload
    })

    // Fetch Templates
    builder.addCase(fetchTemplates.fulfilled, (state, action) => {
      state.templates = action.payload
    })

    // Fetch History
    builder.addCase(fetchHistory.fulfilled, (state, action) => {
      state.history = action.payload
    })

    // Get Voice Analysis
    builder.addCase(getVoiceAnalysis.fulfilled, (state, action) => {
      state.voiceAnalysis = action.payload
    })

    // Get Video Analysis
    builder.addCase(getVideoAnalysis.fulfilled, (state, action) => {
      state.videoAnalysis = action.payload
    })
  },
})

export const { setCurrentSession, setCurrentQuestion, setIsRecording, clearCurrentSession, clearError } = interviewSlice.actions
export default interviewSlice.reducer
