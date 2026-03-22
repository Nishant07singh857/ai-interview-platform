import { apiClient } from './client'
import { Question, QuestionAttempt } from '@/types'

export const questionsService = {
  // Get questions
  getQuestions: async (params?: {
    subject?: string
    topic?: string
    difficulty?: string
    type?: string
    limit?: number
    offset?: number
  }) => {
    const queryParams = new URLSearchParams()
    if (params?.subject) queryParams.append('subject', params.subject)
    if (params?.topic) queryParams.append('topic', params.topic)
    if (params?.difficulty) queryParams.append('difficulty', params.difficulty)
    if (params?.type) queryParams.append('type', params.type)
    if (params?.limit) queryParams.append('limit', params.limit.toString())
    if (params?.offset) queryParams.append('offset', params.offset.toString())

    return apiClient.get<Question[]>(`/questions?${queryParams.toString()}`)
  },

  // Search questions
  searchQuestions: async (query: string, limit: number = 20) => {
    return apiClient.get<Question[]>(`/questions/search?query=${query}&limit=${limit}`)
  },

  // Get single question
  getQuestion: async (questionId: string) => {
    return apiClient.get<Question>(`/questions/${questionId}`)
  },

  // Get question with answers (pro)
  getQuestionWithAnswers: async (questionId: string) => {
    return apiClient.get<Question>(`/questions/${questionId}/with-answers`)
  },

  // Attempt question
  attemptQuestion: async (questionId: string, answer: any, timeTaken: number) => {
    return apiClient.post<QuestionAttempt>(`/questions/${questionId}/attempt`, {
      answer,
      time_taken_seconds: timeTaken,
    })
  },

  // Get hint
  getHint: async (questionId: string, hintNumber: number = 1) => {
    return apiClient.get(`/questions/${questionId}/hint?hint_number=${hintNumber}`)
  },

  // Topics
  getTopics: async (subject?: string) => {
    let url = '/questions/topics/all'
    if (subject) url += `?subject=${subject}`
    return apiClient.get(url)
  },

  getTopic: async (topicId: string) => {
    return apiClient.get(`/questions/topics/${topicId}`)
  },

  // Question Sets
  getPublicSets: async (type?: string, limit: number = 20) => {
    let url = `/questions/sets/public?limit=${limit}`
    if (type) url += `&type=${type}`
    return apiClient.get(url)
  },

  getQuestionSet: async (setId: string) => {
    return apiClient.get(`/questions/sets/${setId}`)
  },
}