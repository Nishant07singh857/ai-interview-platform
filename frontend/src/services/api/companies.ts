import { apiClient } from './client'

export const companiesService = {
  // Get all companies
  getAllCompanies: async () => {
    return apiClient.get('/companies')
  },

  // Get company details
  getCompany: async (companyId: string) => {
    return apiClient.get(`/companies/${companyId}`)
  },

  // Get company questions
  getCompanyQuestions: async (companyId: string, params?: {
    role?: string
    difficulty?: string
    limit?: number
  }) => {
    const queryParams = new URLSearchParams()
    if (params?.role) queryParams.append('role', params.role)
    if (params?.difficulty) queryParams.append('difficulty', params.difficulty)
    if (params?.limit) queryParams.append('limit', params.limit.toString())

    return apiClient.get(`/companies/${companyId}/questions?${queryParams.toString()}`)
  },

  // Get company statistics
  getCompanyStats: async (companyId: string) => {
    return apiClient.get(`/companies/${companyId}/stats`)
  },

  // Get interview experiences
  getInterviewExperiences: async (companyId: string, role?: string) => {
    let url = `/companies/${companyId}/experiences`
    if (role) url += `?role=${role}`
    return apiClient.get(url)
  },

  // Submit interview experience
  submitExperience: async (data: {
    company: string
    role: string
    date: string
    rounds: Array<{
      type: string
      questions: string[]
      difficulty: string
      feedback?: string
    }>
    offer?: boolean
    salary?: {
      base: number
      stock?: number
      bonus?: number
    }
  }) => {
    return apiClient.post('/companies/experiences', data)
  },

  // Get company readiness
  getReadiness: async (companyId: string) => {
    return apiClient.get(`/companies/${companyId}/readiness`)
  },

  // Get preparation tips
  getPreparationTips: async (companyId: string) => {
    return apiClient.get(`/companies/${companyId}/tips`)
  },
}