import { apiClient } from './client'
import { InterviewSession, InterviewQuestion, InterviewFeedback } from '@/types'

export const interviewService = {
  // Start Interview
  startInterview: async (setup: {
    interviewType?: string
    interviewMode?: string
    difficulty?: string
    durationMinutes?: number
    companyFocus?: string
    roleFocus?: string
    categories?: string[]
    topics?: string[]
    allowFollowUp?: boolean
    allowHints?: boolean
    showFeedbackImmediately?: boolean
  }) => {
    return apiClient.post<InterviewSession>('/interview/sessions/start', setup)
  },

  // Company-specific Interview
  startCompanyInterview: async (company: string, role?: string, difficulty?: string) => {
    return apiClient.post<InterviewSession>(`/interview/company/${company}/start`, {
      role,
      difficulty,
    })
  },

  // Session Management
  getSession: async (sessionId: string) => {
    return apiClient.get<InterviewSession>(`/interview/sessions/${sessionId}`)
  },

  pauseSession: async (sessionId: string) => {
    return apiClient.post(`/interview/sessions/${sessionId}/pause`)
  },

  resumeSession: async (sessionId: string) => {
    return apiClient.post<InterviewSession>(`/interview/sessions/${sessionId}/resume`)
  },

  endSession: async (sessionId: string) => {
    return apiClient.post(`/interview/sessions/${sessionId}/end`)
  },

  // Questions
  getCurrentQuestion: async (sessionId: string) => {
    return apiClient.get<InterviewQuestion>(`/interview/sessions/${sessionId}/current-question`)
  },

  submitResponse: async (
    sessionId: string,
    questionId: string,
    timeTaken: number,
    text?: string,
    audio?: Blob
  ) => {
    const formData = new FormData()
    formData.append('session_id', sessionId)
    formData.append('question_id', questionId)
    if (text) formData.append('text_response', text)
    if (audio) formData.append('audio', audio, 'response.webm')
    formData.append('time_taken_seconds', timeTaken.toString())

    return apiClient.post(`/interview/sessions/${sessionId}/respond`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },

  getHint: async (sessionId: string, questionId: string) => {
    return apiClient.get(`/interview/sessions/${sessionId}/question/${questionId}/hint`)
  },

  // Feedback
  getFeedback: async (sessionId: string, detailed: boolean = false) => {
    return apiClient.get<InterviewFeedback>(
      `/interview/sessions/${sessionId}/feedback?include_detailed=${detailed}`
    )
  },

  // Templates
  getTemplates: async (mode?: string, company?: string) => {
    let url = '/interview/templates'
    const params = new URLSearchParams()
    if (mode) params.append('mode', mode)
    if (company) params.append('company', company)
    if (params.toString()) url += `?${params.toString()}`
    return apiClient.get(url)
  },

  getTemplate: async (templateId: string) => {
    return apiClient.get(`/interview/templates/${templateId}`)
  },

  // History
  getHistory: async (limit: number = 10) => {
    return apiClient.get(`/interview/history?limit=${limit}`)
  },

  // Analysis
  getVoiceAnalysis: async (responseId: string) => {
    return apiClient.get(`/interview/analysis/voice/${responseId}`)
  },

  getVideoAnalysis: async (responseId: string) => {
    return apiClient.get(`/interview/analysis/video/${responseId}`)
  },

  // WebSocket connection
  connectWebSocket: (sessionId: string, token: string): WebSocket => {
    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'
    return new WebSocket(`${wsUrl}/interview/ws/${sessionId}?token=${token}`)
  },
}
