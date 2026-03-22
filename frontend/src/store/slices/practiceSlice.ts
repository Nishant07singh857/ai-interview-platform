import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
import { practiceService } from '@/services/api/practice'
import {
  PracticeSession,
  PracticeResult,
  Question,
  QuestionAttempt,
  PracticeType,
} from '@/types'
import toast from 'react-hot-toast'

interface PracticeState {
  currentSession: PracticeSession | null
  sessions: PracticeSession[]
  results: PracticeResult[]
  currentQuestion: Question | null
  nextQuestion: Question | null
  questionHistory: QuestionAttempt[]
  history: {
    totalSessions: number
    totalTimeSpent: number
    averageScore: number
    averageAccuracy: number
    recentSessions: PracticeSession[]
  }
  leaderboard: any[]
  isLoading: boolean
  error: string | null
}

const initialState: PracticeState = {
  currentSession: null,
  sessions: [],
  results: [],
  currentQuestion: null,
  nextQuestion: null,
  questionHistory: [],
  history: {
    totalSessions: 0,
    totalTimeSpent: 0,
    averageScore: 0,
    averageAccuracy: 0,
    recentSessions: [],
  },
  leaderboard: [],
  isLoading: false,
  error: null,
}

export const startQuickQuiz = createAsyncThunk(
  'practice/startQuickQuiz',
  async (config: { totalQuestions?: number; timeLimit?: number; subjects?: string[] }, { rejectWithValue }) => {
    try {
      const response = await practiceService.startQuickQuiz(config)
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to start quiz')
    }
  }
)

export const startTopicPractice = createAsyncThunk(
  'practice/startTopicPractice',
  async (config: { 
    subject: string; 
    topic: string; 
    subtopics?: string[]; 
    totalQuestions?: number;
    difficulty?: string;
    timeLimit?: number;
  }, { rejectWithValue }) => {
    try {
      const backendConfig = {
        subject: config.subject,
        topic: config.topic,
        subtopics: config.subtopics || [],
        total_questions: config.totalQuestions || 10,
        time_limit_minutes: config.timeLimit || 30,
        difficulty: config.difficulty || 'medium',
        include_explanations: true,
        shuffle: true
      };
      const response = await practiceService.startTopicPractice(backendConfig);
      return response.data;
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to start practice';
      return rejectWithValue(errorMessage);
    }
  }
)

export const startMockTest = createAsyncThunk(
  'practice/startMockTest',
  async (config: { subject: string; title?: string; totalQuestions?: number; timeLimit?: number }, { rejectWithValue }) => {
    try {
      const response = await practiceService.startMockTest(config)
      return response.data
    } catch (error: any) {
      const status = error?.response?.status
      const message = error.response?.data?.detail || 'Failed to start mock test'
      return rejectWithValue({ message, status })
    }
  }
)

export const startCompanyPractice = createAsyncThunk(
  'practice/startCompanyPractice',
  async (config: { company: string; role?: string; totalQuestions?: number }, { rejectWithValue }) => {
    try {
      const response = await practiceService.startCompanyPractice(config)
      return response.data
    } catch (error: any) {
      const status = error?.response?.status
      const message = error.response?.data?.detail || 'Failed to start company practice'
      return rejectWithValue({ message, status })
    }
  }
)

export const submitAnswer = createAsyncThunk(
  'practice/submitAnswer',
  async (
    { sessionId, questionId, answer, timeTaken }: 
    { sessionId: string; questionId: string; answer: any; timeTaken: number },
    { rejectWithValue }
  ) => {
    try {
      const response = await practiceService.submitAnswer(sessionId, questionId, answer, timeTaken)
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to submit answer')
    }
  }
)

export const skipQuestion = createAsyncThunk(
  'practice/skipQuestion',
  async (sessionId: string, { rejectWithValue }) => {
    try {
      const response = await practiceService.skipQuestion(sessionId)
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to skip question')
    }
  }
)

export const pauseSession = createAsyncThunk(
  'practice/pauseSession',
  async (sessionId: string, { rejectWithValue }) => {
    try {
      const response = await practiceService.pauseSession(sessionId)
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to pause session')
    }
  }
)

export const resumeSession = createAsyncThunk(
  'practice/resumeSession',
  async (sessionId: string, { rejectWithValue }) => {
    try {
      const response = await practiceService.resumeSession(sessionId)
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to resume session')
    }
  }
)

export const endSession = createAsyncThunk(
  'practice/endSession',
  async (sessionId: string, { rejectWithValue }) => {
    try {
      const response = await practiceService.endSession(sessionId)
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to end session')
    }
  }
)

export const fetchSession = createAsyncThunk(
  'practice/fetchSession',
  async (sessionId: string, { rejectWithValue }) => {
    try {
      const response = await practiceService.getSession(sessionId)
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch session')
    }
  }
)

export const fetchSessionResults = createAsyncThunk(
  'practice/fetchSessionResults',
  async (sessionId: string, { rejectWithValue }) => {
    try {
      const response = await practiceService.getSessionResults(sessionId)
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch results')
    }
  }
)

export const fetchPracticeHistory = createAsyncThunk(
  'practice/fetchHistory',
  async (params: { days?: number; type?: PracticeType }, { rejectWithValue }) => {
    try {
      const response = await practiceService.getHistory(params.days, params.type)
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch history')
    }
  }
)

export const fetchLeaderboard = createAsyncThunk(
  'practice/fetchLeaderboard',
  async (params: { subject: string; period?: string; limit?: number }, { rejectWithValue }) => {
    try {
      const response = await practiceService.getLeaderboard(params.subject, params.period, params.limit)
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch leaderboard')
    }
  }
)

export const submitFeedback = createAsyncThunk(
  'practice/submitFeedback',
  async (params: { sessionId: string; rating: number; feedback?: string }, { rejectWithValue }) => {
    try {
      const response = await practiceService.submitFeedback(params.sessionId, params.rating, params.feedback)
      toast.success('Thank you for your feedback!')
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to submit feedback')
    }
  }
)

const practiceSlice = createSlice({
  name: 'practice',
  initialState,
  reducers: {
    setCurrentQuestion: (state, action: PayloadAction<Question>) => {
      state.currentQuestion = action.payload
      state.nextQuestion = null
    },
    clearCurrentSession: (state) => {
      state.currentSession = null
      state.currentQuestion = null
      state.nextQuestion = null
    },
    updateSessionProgress: (state, action: PayloadAction<Partial<PracticeSession>>) => {
      if (state.currentSession) {
        state.currentSession = { ...state.currentSession, ...action.payload }
      }
    },
    addQuestionToHistory: (state, action: PayloadAction<QuestionAttempt>) => {
      state.questionHistory.unshift(action.payload)
      if (state.questionHistory.length > 50) {
        state.questionHistory.pop()
      }
    },
    clearError: (state) => {
      state.error = null
    },
    advanceToNextQuestion: (state) => {
      if (state.nextQuestion) {
        state.currentQuestion = state.nextQuestion
        state.nextQuestion = null
        if (state.currentSession) {
          const nextIndex = state.currentSession.currentQuestionIndex + 1
          state.currentSession.currentQuestionIndex = Math.min(
            nextIndex,
            Math.max(state.currentSession.totalQuestions - 1, 0)
          )
        }
      }
    },
  },
  extraReducers: (builder) => {
    builder.addCase(startQuickQuiz.pending, (state) => {
      state.isLoading = true
      state.error = null
    })
    builder.addCase(startQuickQuiz.fulfilled, (state, action) => {
      state.isLoading = false
      state.currentSession = action.payload
      state.currentQuestion = action.payload.currentQuestion ?? null
      state.nextQuestion = null
    })
    builder.addCase(startQuickQuiz.rejected, (state, action) => {
      state.isLoading = false
      state.error = action.payload as string
      toast.error(action.payload as string)
    })

    builder.addCase(startTopicPractice.pending, (state) => {
      state.isLoading = true
      state.error = null
    })
    builder.addCase(startTopicPractice.fulfilled, (state, action) => {
      state.isLoading = false
      state.currentSession = action.payload
      state.currentQuestion = action.payload.currentQuestion ?? null
      state.nextQuestion = null
      toast.success('Practice started!')
    })
    builder.addCase(startTopicPractice.rejected, (state, action) => {
      state.isLoading = false
      state.error = action.payload as string
      toast.error(action.payload as string)
    })

    builder.addCase(startMockTest.pending, (state) => {
      state.isLoading = true
    })
    builder.addCase(startMockTest.fulfilled, (state, action) => {
      state.isLoading = false
      state.currentSession = action.payload
      state.currentQuestion = action.payload.currentQuestion ?? null
      state.nextQuestion = null
    })
    builder.addCase(startMockTest.rejected, (state, action) => {
      state.isLoading = false
      const payload = action.payload as any
      const message = payload?.message || (action.payload as string)
      state.error = message
      if (message && payload?.status !== 403) {
        toast.error(message)
      }
    })

    builder.addCase(startCompanyPractice.pending, (state) => {
      state.isLoading = true
    })
    builder.addCase(startCompanyPractice.fulfilled, (state, action) => {
      state.isLoading = false
      state.currentSession = action.payload
      state.currentQuestion = action.payload.currentQuestion ?? null
      state.nextQuestion = null
    })
    builder.addCase(startCompanyPractice.rejected, (state, action) => {
      state.isLoading = false
      const payload = action.payload as any
      const message = payload?.message || (action.payload as string)
      state.error = message
      if (message && payload?.status !== 403) {
        toast.error(message)
      }
    })

    builder.addCase(submitAnswer.fulfilled, (state, action) => {
      if (state.currentSession) {
        const progress = action.payload.progress
        if (progress) {
          const answered = (progress.correct ?? 0) + (progress.incorrect ?? 0)
          state.currentSession.questionsAnswered = answered
          state.currentSession.correctAnswers = progress.correct ?? state.currentSession.correctAnswers
          state.currentSession.incorrectAnswers = progress.incorrect ?? state.currentSession.incorrectAnswers
        }

        state.nextQuestion = action.payload.nextQuestion ?? null

        if (action.payload.sessionCompleted) {
          state.currentSession.status = 'completed'
        }
      }
      
      state.questionHistory.unshift({
        questionId: action.meta.arg.questionId,
        isCorrect: action.payload.isCorrect,
        timeTaken: action.meta.arg.timeTaken,
        attemptedAt: new Date().toISOString(),
      })
    })

    builder.addCase(skipQuestion.fulfilled, (state, action) => {
      if (state.currentSession) {
        state.currentSession.questionsSkipped = (state.currentSession.questionsSkipped || 0) + 1

        const progress = action.payload.progress
        if (progress && typeof progress.current === 'number') {
          state.currentSession.currentQuestionIndex = Math.max(progress.current - 1, 0)
        }
        
        if (action.payload.nextQuestion) {
          state.currentQuestion = action.payload.nextQuestion
        }
        state.nextQuestion = null
        
        if (action.payload.sessionCompleted) {
          state.currentSession.status = 'completed'
        }
      }
    })

    builder.addCase(endSession.fulfilled, (state) => {
      if (state.currentSession) {
        state.currentSession.status = 'completed'
        state.currentSession.completedAt = new Date().toISOString()
      }
      if (state.currentSession) {
        state.sessions.unshift(state.currentSession)
      }
    })

    builder.addCase(fetchSession.fulfilled, (state, action) => {
      state.currentSession = action.payload
      if (action.payload.currentQuestion) {
        state.currentQuestion = action.payload.currentQuestion
      }
      state.nextQuestion = null
    })

    builder.addCase(fetchSessionResults.fulfilled, (state, action) => {
      state.results.unshift(action.payload)
    })

    builder.addCase(fetchPracticeHistory.fulfilled, (state, action) => {
      state.history = action.payload
    })
    builder.addCase(fetchPracticeHistory.rejected, (state, action) => {
      state.error = action.payload as string
      toast.error(action.payload as string)
    })

    builder.addCase(fetchLeaderboard.fulfilled, (state, action) => {
      state.leaderboard = action.payload.leaderboard || []
    })
    builder.addCase(fetchLeaderboard.rejected, (state, action) => {
      state.error = action.payload as string
      toast.error(action.payload as string)
    })

    builder.addCase(submitFeedback.fulfilled, (state) => {
      // No state update needed
    })
    builder.addCase(submitFeedback.rejected, (state, action) => {
      state.error = action.payload as string
      toast.error(action.payload as string)
    })
  },
})

export const {
  setCurrentQuestion,
  clearCurrentSession,
  updateSessionProgress,
  addQuestionToHistory,
  clearError,
  advanceToNextQuestion,
} = practiceSlice.actions

export default practiceSlice.reducer
