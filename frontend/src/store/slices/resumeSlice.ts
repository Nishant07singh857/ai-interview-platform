import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
import { resumeService } from '@/services/api/resume'
import { Resume, ParsedResume, GapAnalysis, LearningRoadmap } from '@/types'
import toast from 'react-hot-toast'

interface ResumeState {
  resumes: Resume[]
  currentResume: Resume | null
  parsedResume: ParsedResume | null
  analysis: any | null
  gapAnalysis: GapAnalysis | null
  roadmap: LearningRoadmap | null
  companyMatches: any[]
  skillAssessment: any[]
  isLoading: boolean
  uploadProgress: number
  error: string | null
}

const initialState: ResumeState = {
  resumes: [],
  currentResume: null,
  parsedResume: null,
  analysis: null,
  gapAnalysis: null,
  roadmap: null,
  companyMatches: [],
  skillAssessment: [],
  isLoading: false,
  uploadProgress: 0,
  error: null,
}

// Async thunks
export const uploadResume = createAsyncThunk(
  'resume/upload',
  async (file: File, { dispatch, rejectWithValue }) => {
    try {
      const response = await resumeService.uploadResume(file, (progress) => {
        dispatch(setUploadProgress(progress))
      })
      toast.success('Resume uploaded successfully!')
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to upload resume')
    }
  }
)

export const fetchResumes = createAsyncThunk('resume/fetchAll', async (_, { rejectWithValue }) => {
  try {
    const response = await resumeService.listResumes()
    return response.data
  } catch (error: any) {
    return rejectWithValue(error.response?.data?.detail || 'Failed to fetch resumes')
  }
})

export const fetchResume = createAsyncThunk(
  'resume/fetchOne',
  async (resumeId: string, { rejectWithValue }) => {
    try {
      const response = await resumeService.getResume(resumeId)
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch resume')
    }
  }
)

export const deleteResume = createAsyncThunk(
  'resume/delete',
  async (resumeId: string, { rejectWithValue }) => {
    try {
      await resumeService.deleteResume(resumeId)
      toast.success('Resume deleted successfully')
      return resumeId
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to delete resume')
    }
  }
)

export const parseResume = createAsyncThunk(
  'resume/parse',
  async (resumeId: string, { rejectWithValue }) => {
    try {
      const response = await resumeService.parseResume(resumeId)
      toast.success('Resume parsed successfully!')
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to parse resume')
    }
  }
)

export const analyzeResume = createAsyncThunk(
  'resume/analyze',
  async ({ resumeId, targetCompany, targetRole }: { resumeId: string; targetCompany?: string; targetRole?: string }, { rejectWithValue }) => {
    try {
      const response = await resumeService.analyzeResume(resumeId, targetCompany, targetRole)
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to analyze resume')
    }
  }
)

export const analyzeGaps = createAsyncThunk(
  'resume/analyzeGaps',
  async ({ resumeId, targetCompany, targetRole, jobDescription }: 
    { resumeId: string; targetCompany: string; targetRole: string; jobDescription?: string }, 
    { rejectWithValue }
  ) => {
    try {
      const response = await resumeService.analyzeGaps(resumeId, targetCompany, targetRole, jobDescription)
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to analyze gaps')
    }
  }
)

export const generateRoadmap = createAsyncThunk(
  'resume/generateRoadmap',
  async ({ resumeId, targetCompany, targetRole, targetInterviewDate, hoursPerWeek }: 
    { resumeId: string; targetCompany: string; targetRole: string; targetInterviewDate?: string; hoursPerWeek?: number }, 
    { rejectWithValue }
  ) => {
    try {
      const response = await resumeService.generateRoadmap(resumeId, targetCompany, targetRole, targetInterviewDate, hoursPerWeek)
      toast.success('Learning roadmap generated!')
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to generate roadmap')
    }
  }
)

export const getCompanyMatches = createAsyncThunk(
  'resume/getCompanyMatches',
  async (resumeId: string | undefined, { rejectWithValue }) => {
    try {
      const response = await resumeService.getCompanyMatches(resumeId)
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to get company matches')
    }
  }
)

export const assessSkills = createAsyncThunk('resume/assessSkills', async (_, { rejectWithValue }) => {
  try {
    const response = await resumeService.assessSkills()
    return response.data
  } catch (error: any) {
    return rejectWithValue(error.response?.data?.detail || 'Failed to assess skills')
  }
})

export const analyzeJobDescription = createAsyncThunk(
  'resume/analyzeJobDescription',
  async (jobDescription: string, { rejectWithValue }) => {
    try {
      const response = await resumeService.analyzeJobDescription(jobDescription)
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to analyze job description')
    }
  }
)

export const optimizeForJob = createAsyncThunk(
  'resume/optimizeForJob',
  async ({ resumeId, jobDescription }: { resumeId: string; jobDescription: string }, { rejectWithValue }) => {
    try {
      const response = await resumeService.optimizeForJob(resumeId, jobDescription)
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to optimize resume')
    }
  }
)

export const updateMilestone = createAsyncThunk(
  'resume/updateMilestone',
  async ({ roadmapId, milestoneId, completed }: { roadmapId: string; milestoneId: string; completed: boolean }, { rejectWithValue }) => {
    try {
      const response = await resumeService.updateMilestone(roadmapId, milestoneId, completed)
      if (completed) {
        toast.success('Milestone completed! 🎉')
      }
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to update milestone')
    }
  }
)

const resumeSlice = createSlice({
  name: 'resume',
  initialState,
  reducers: {
    setCurrentResume: (state, action: PayloadAction<Resume>) => {
      state.currentResume = action.payload
    },
    setUploadProgress: (state, action: PayloadAction<number>) => {
      state.uploadProgress = action.payload
    },
    clearResumeData: (state) => {
      state.currentResume = null
      state.parsedResume = null
      state.analysis = null
      state.gapAnalysis = null
      state.roadmap = null
    },
    clearError: (state) => {
      state.error = null
    },
  },
  extraReducers: (builder) => {
    // Upload Resume
    builder.addCase(uploadResume.pending, (state) => {
      state.isLoading = true
      state.error = null
      state.uploadProgress = 0
    })
    builder.addCase(uploadResume.fulfilled, (state, action) => {
      state.isLoading = false
      state.uploadProgress = 100
      state.resumes.unshift(action.payload)
      state.currentResume = action.payload
    })
    builder.addCase(uploadResume.rejected, (state, action) => {
      state.isLoading = false
      state.error = action.payload as string
      toast.error(action.payload as string)
    })

    // Fetch Resumes
    builder.addCase(fetchResumes.pending, (state) => {
      state.isLoading = true
    })
    builder.addCase(fetchResumes.fulfilled, (state, action) => {
      state.isLoading = false
      state.resumes = action.payload
    })
    builder.addCase(fetchResumes.rejected, (state, action) => {
      state.isLoading = false
      state.error = action.payload as string
    })

    // Fetch Resume
    builder.addCase(fetchResume.fulfilled, (state, action) => {
      state.currentResume = action.payload
    })

    // Delete Resume
    builder.addCase(deleteResume.fulfilled, (state, action) => {
      state.resumes = state.resumes.filter(r => r.resumeId !== action.payload)
      if (state.currentResume?.resumeId === action.payload) {
        state.currentResume = null
      }
    })

    // Parse Resume
    builder.addCase(parseResume.pending, (state) => {
      state.isLoading = true
    })
    builder.addCase(parseResume.fulfilled, (state, action) => {
      state.isLoading = false
      state.parsedResume = action.payload
      if (state.currentResume) {
        state.currentResume.status = 'parsed'
        state.currentResume.parsedAt = new Date().toISOString()
      }
    })
    builder.addCase(parseResume.rejected, (state, action) => {
      state.isLoading = false
      state.error = action.payload as string
    })

    // Analyze Resume
    builder.addCase(analyzeResume.pending, (state) => {
      state.isLoading = true
    })
    builder.addCase(analyzeResume.fulfilled, (state, action) => {
      state.isLoading = false
      state.analysis = action.payload
      if (state.currentResume) {
        state.currentResume.status = 'analyzed'
        state.currentResume.analyzedAt = new Date().toISOString()
      }
    })
    builder.addCase(analyzeResume.rejected, (state, action) => {
      state.isLoading = false
      state.error = action.payload as string
    })

    // Analyze Gaps
    builder.addCase(analyzeGaps.pending, (state) => {
      state.isLoading = true
    })
    builder.addCase(analyzeGaps.fulfilled, (state, action) => {
      state.isLoading = false
      state.gapAnalysis = action.payload
    })
    builder.addCase(analyzeGaps.rejected, (state, action) => {
      state.isLoading = false
      state.error = action.payload as string
    })

    // Generate Roadmap
    builder.addCase(generateRoadmap.pending, (state) => {
      state.isLoading = true
    })
    builder.addCase(generateRoadmap.fulfilled, (state, action) => {
      state.isLoading = false
      state.roadmap = action.payload
    })
    builder.addCase(generateRoadmap.rejected, (state, action) => {
      state.isLoading = false
      state.error = action.payload as string
    })

    // Get Company Matches
    builder.addCase(getCompanyMatches.fulfilled, (state, action) => {
      state.companyMatches = action.payload
    })

    // Assess Skills
    builder.addCase(assessSkills.fulfilled, (state, action) => {
      state.skillAssessment = action.payload
    })

    // Analyze Job Description
    builder.addCase(analyzeJobDescription.fulfilled, (state, action) => {
      // Handle job description analysis
    })

    // Optimize for Job
    builder.addCase(optimizeForJob.fulfilled, (state, action) => {
      // Handle optimization suggestions
    })

    // Update Milestone
    builder.addCase(updateMilestone.fulfilled, (state, action) => {
      if (state.roadmap) {
        const milestone = state.roadmap.milestones.find(m => m.milestone_id === action.meta.arg.milestoneId)
        if (milestone) {
          milestone.completed = action.meta.arg.completed
          if (action.meta.arg.completed) {
            milestone.completed_at = new Date().toISOString()
          }
        }
        if (typeof action.payload.overall_progress === 'number') {
          state.roadmap.overall_progress = action.payload.overall_progress
        }
      }
    })
  },
})

export const { setCurrentResume, setUploadProgress, clearResumeData, clearError } = resumeSlice.actions
export default resumeSlice.reducer
