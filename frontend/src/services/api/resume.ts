import { apiClient } from './client'
import { Resume, ParsedResume, GapAnalysis, LearningRoadmap } from '@/types'

export const resumeService = {
  // Upload
  uploadResume: async (file: File, onProgress?: (progress: number) => void) => {
    return apiClient.upload<Resume>('/resume/upload', file, onProgress)
  },

  // List
  listResumes: async () => {
    return apiClient.get<Resume[]>('/resume/list')
  },

  // Get single
  getResume: async (resumeId: string) => {
    return apiClient.get<Resume>(`/resume/${resumeId}`)
  },

  // Delete
  deleteResume: async (resumeId: string) => {
    return apiClient.delete(`/resume/${resumeId}`)
  },

  // Parse
  parseResume: async (resumeId: string) => {
    return apiClient.post<ParsedResume>(`/resume/${resumeId}/parse`)
  },

  getParsedResume: async (resumeId: string) => {
    return apiClient.get<ParsedResume>(`/resume/${resumeId}/parsed`)
  },

  // Analyze
  analyzeResume: async (resumeId: string, targetCompany?: string, targetRole?: string) => {
    return apiClient.post(`/resume/${resumeId}/analyze`, {
      target_company: targetCompany,
      target_role: targetRole,
    })
  },

  getAnalysis: async (resumeId: string) => {
    return apiClient.get(`/resume/${resumeId}/analysis`)
  },

  // Gap Analysis
  analyzeGaps: async (resumeId: string, targetCompany: string, targetRole: string, jobDescription?: string) => {
    return apiClient.post<GapAnalysis>(`/resume/${resumeId}/gap-analysis`, {
      target_company: targetCompany,
      target_role: targetRole,
      job_description: jobDescription,
    })
  },

  getGapAnalysis: async (resumeId: string, company: string) => {
    return apiClient.get<GapAnalysis>(`/resume/${resumeId}/gap-analysis/${company}`)
  },

  // Roadmap
  generateRoadmap: async (
    resumeId: string,
    targetCompany: string,
    targetRole: string,
    targetInterviewDate?: string,
    hoursPerWeek?: number
  ) => {
    return apiClient.post<LearningRoadmap>(`/resume/${resumeId}/roadmap`, {
      target_company: targetCompany,
      target_role: targetRole,
      target_interview_date: targetInterviewDate,
      hours_per_week: hoursPerWeek,
    })
  },

  getCurrentRoadmap: async () => {
    return apiClient.get<LearningRoadmap>('/resume/roadmap/current')
  },

  updateMilestone: async (roadmapId: string, milestoneId: string, completed: boolean) => {
    return apiClient.put(`/resume/roadmap/${roadmapId}/milestone/${milestoneId}?completed=${completed}`)
  },

  // Company Matches
  getCompanyMatches: async (resumeId?: string) => {
    let url = '/resume/company-matches'
    if (resumeId) url += `?resume_id=${resumeId}`
    return apiClient.get(url)
  },

  // Skills
  assessSkills: async () => {
    return apiClient.get('/resume/skills/assessment')
  },

  // Job Description
  analyzeJobDescription: async (jobDescription: string) => {
    return apiClient.post('/resume/analyze-job-description', { job_description: jobDescription })
  },

  optimizeForJob: async (resumeId: string, jobDescription: string) => {
    return apiClient.post(`/resume/${resumeId}/optimize`, { job_description: jobDescription })
  },

  // Export
  exportAnalysis: async (resumeId: string, format: 'pdf' | 'json' | 'csv') => {
    return apiClient.get(`/resume/${resumeId}/export/${format}`)
  },
}