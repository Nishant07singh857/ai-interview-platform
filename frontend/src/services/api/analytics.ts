import { apiClient } from './client'
import type { AxiosResponse } from 'axios'
import {
  AnalyticsSummary,
  PerformanceTrend,
  TopicMastery,
  CompanyReadiness,
} from '@/types'

const withData = <T>(response: AxiosResponse<any>, data: T): AxiosResponse<T> => {
  return { ...response, data }
}

const normalizeSummary = (data: any): AnalyticsSummary => {
  return {
    overallAccuracy: data?.overallAccuracy ?? data?.overall_accuracy ?? 0,
    totalQuestions: data?.totalQuestions ?? data?.total_questions ?? 0,
    currentStreak: data?.currentStreak ?? data?.current_streak ?? 0,
    longestStreak: data?.longestStreak ?? data?.longest_streak ?? 0,
    totalPracticeTime: data?.totalPracticeTime ?? data?.total_practice_time ?? 0,
    averageDailyTime: data?.averageDailyTime ?? data?.average_daily_time ?? 0,
  }
}

const normalizeTrends = (data: any): PerformanceTrend => {
  return {
    dates: data?.dates ?? [],
    accuracy: data?.accuracy ?? [],
    volume: data?.volume ?? [],
    timeSpent: data?.timeSpent ?? data?.time_spent ?? [],
  }
}

const normalizeBucket = (data: any) => {
  return {
    total: data?.total ?? 0,
    correct: data?.correct ?? 0,
    incorrect: data?.incorrect ?? 0,
    accuracy: data?.accuracy ?? 0,
    timeSpent: data?.timeSpent ?? data?.time_spent ?? 0,
    averageTime: data?.averageTime ?? data?.average_time ?? 0,
    trend: data?.trend ?? [],
  }
}

const normalizeBucketMap = (data: any) => {
  if (!data || typeof data !== 'object') return {}
  const result: Record<string, any> = {}
  Object.entries(data).forEach(([key, value]) => {
    result[key] = normalizeBucket(value)
  })
  return result
}

const normalizeTopicMastery = (data: any): TopicMastery => {
  const mapItem = (item: any) => ({
    topic: item?.topic ?? '',
    accuracy: item?.accuracy ?? 0,
    attempts: item?.attempts ?? item?.total ?? 0,
    masteryLevel: item?.masteryLevel ?? item?.mastery_level ?? item?.status ?? 'not_started',
    lastPracticed: item?.lastPracticed ?? item?.last_practiced ?? undefined,
  })

  return {
    masteredTopics: (data?.masteredTopics ?? data?.mastered_topics ?? []).map(mapItem),
    inProgressTopics: (data?.inProgressTopics ?? data?.in_progress_topics ?? []).map(mapItem),
    notStartedTopics: (data?.notStartedTopics ?? data?.not_started_topics ?? []).map(mapItem),
  }
}

const normalizeCompanyReadiness = (company: any): CompanyReadiness => {
  return {
    company: company?.company ?? '',
    readinessLevel: company?.readinessLevel ?? company?.readiness_level ?? 'not_ready',
    overallScore: company?.overallScore ?? company?.overall_score ?? 0,
    technicalScore: company?.technicalScore ?? company?.technical_score ?? 0,
    behavioralScore: company?.behavioralScore ?? company?.behavioral_score ?? 0,
    systemDesignScore: company?.systemDesignScore ?? company?.system_design_score ?? 0,
    interviewSuccessProbability:
      company?.interviewSuccessProbability ??
      company?.interview_success_probability ??
      0,
    estimatedPreparationTime:
      company?.estimatedPreparationTime ??
      company?.estimated_preparation_time ??
      0,
    criticalGaps: company?.criticalGaps ?? company?.critical_gaps ?? [],
    logo: company?.logo ?? undefined,
  }
}

const normalizeStreak = (data: any) => {
  return {
    currentStreak: data?.currentStreak ?? data?.current_streak ?? 0,
    longestStreak: data?.longestStreak ?? data?.longest_streak ?? 0,
    streakDates: data?.streakDates ?? data?.streak_dates ?? [],
    lastActive: data?.lastActive ?? data?.last_active ?? null,
  }
}

const normalizeTimeAnalysis = (data: any) => {
  return {
    averageTime: data?.averageTime ?? data?.average_time ?? 0,
    medianTime: data?.medianTime ?? data?.median_time ?? 0,
    fastestTime: data?.fastestTime ?? data?.fastest_time ?? 0,
    slowestTime: data?.slowestTime ?? data?.slowest_time ?? 0,
    byDifficulty: normalizeBucketMap(data?.byDifficulty ?? data?.by_difficulty ?? {}),
    byType: normalizeBucketMap(data?.byType ?? data?.by_type ?? {}),
  }
}

const normalizeDashboard = (data: any) => {
  const subjectPerformanceRaw =
    data?.subjectPerformance ??
    data?.subject_performance ??
    data?.subjects ??
    {}
  const subjectData = subjectPerformanceRaw?.subjects ?? subjectPerformanceRaw

  return {
    user: data?.user ?? undefined,
    summary: normalizeSummary(data?.summary ?? {}),
    trends: normalizeTrends(data?.trends ?? {}),
    subjectPerformance: normalizeBucketMap(subjectData),
    weakTopics: data?.weakTopics ?? data?.weak_topics ?? [],
    strongTopics: data?.strongTopics ?? data?.strong_topics ?? [],
    streak: normalizeStreak(data?.streak ?? {}),
    recommendations: data?.recommendations ?? [],
    recentActivity: data?.recentActivity ?? data?.recent_activity ?? [],
    companyReadiness: data?.companyReadiness ?? data?.company_readiness ?? undefined,
  }
}

export const analyticsService = {
  // Summary
  getSummary: async () => {
    const response = await apiClient.get<AnalyticsSummary>('/analytics/summary')
    return withData(response, normalizeSummary(response.data))
  },

  // Trends
  getTrends: async (days: number = 30) => {
    const response = await apiClient.get<PerformanceTrend>(`/analytics/trends?days=${days}`)
    return withData(response, normalizeTrends(response.data))
  },

  // Subject Performance
  getSubjectPerformance: async () => {
    const response = await apiClient.get('/analytics/subjects')
    const subjectData = response.data?.subjects ?? response.data
    return withData(response, normalizeBucketMap(subjectData))
  },

  getSubjectDetails: async (subject: string) => {
    return apiClient.get(`/analytics/subjects/${subject}`)
  },

  // Topic Mastery
  getTopicMastery: async (subject?: string) => {
    let url = '/analytics/topics/mastery'
    if (subject) url += `?subject=${subject}`
    const response = await apiClient.get<TopicMastery>(url)
    return withData(response, normalizeTopicMastery(response.data))
  },

  getWeakTopics: async (limit: number = 5) => {
    return apiClient.get(`/analytics/topics/weak?limit=${limit}`)
  },

  getStrongTopics: async (limit: number = 5) => {
    return apiClient.get(`/analytics/topics/strong?limit=${limit}`)
  },

  // Company Readiness
  getCompanyReadiness: async () => {
    const response = await apiClient.get<{ companies: CompanyReadiness[] }>('/analytics/companies/readiness')
    const companies = (response.data?.companies ?? []).map(normalizeCompanyReadiness)
    return withData(response, { ...response.data, companies })
  },

  getCompanyDetails: async (company: string) => {
    return apiClient.get(`/analytics/companies/${company}/readiness`)
  },

  // Difficulty Analysis
  getDifficultyPerformance: async () => {
    const response = await apiClient.get('/analytics/difficulty')
    return withData(response, normalizeBucketMap(response.data))
  },

  // Question Type Analysis
  getQuestionTypePerformance: async () => {
    const response = await apiClient.get('/analytics/question-types')
    return withData(response, normalizeBucketMap(response.data))
  },

  // Time Analysis
  getTimeAnalysis: async () => {
    const response = await apiClient.get('/analytics/time')
    return withData(response, normalizeTimeAnalysis(response.data))
  },

  // Weekly Report
  getWeeklyReport: async (weekStart?: string) => {
    let url = '/analytics/reports/weekly'
    if (weekStart) url += `?week_start=${weekStart}`
    return apiClient.get(url)
  },

  // Learning Path
  generateLearningPath: async (targetRole?: string, targetCompanies?: string[]) => {
    let url = '/analytics/learning-path'
    const params = new URLSearchParams()
    if (targetRole) params.append('target_role', targetRole)
    if (targetCompanies?.length) params.append('target_companies', targetCompanies.join(','))
    if (params.toString()) url += `?${params.toString()}`
    return apiClient.get(url)
  },

  // Peer Comparison
  compareWithPeers: async (peerGroup: string = 'all', subjects?: string[]) => {
    let url = '/analytics/compare'
    const params = new URLSearchParams()
    params.append('peer_group', peerGroup)
    if (subjects?.length) params.append('subjects', subjects.join(','))
    return apiClient.get(`${url}?${params.toString()}`)
  },

  // Predictions
  getPredictions: async () => {
    return apiClient.get('/analytics/predictions')
  },

  // Skill Gaps
  getSkillGaps: async (targetRole?: string) => {
    let url = '/analytics/skill-gaps'
    if (targetRole) url += `?target_role=${targetRole}`
    return apiClient.get(url)
  },

  // Recommendations
  getRecommendations: async (limit: number = 5) => {
    return apiClient.get(`/analytics/recommendations?limit=${limit}`)
  },

  // Streak
  getStreakInfo: async () => {
    return apiClient.get('/analytics/streak')
  },

  // Heatmap
  getActivityHeatmap: async (year?: number) => {
    let url = '/analytics/heatmap'
    if (year) url += `?year=${year}`
    return apiClient.get(url)
  },

  // Milestones
  getMilestones: async () => {
    return apiClient.get('/analytics/milestones')
  },

  // Dashboard
  getDashboardData: async () => {
    const response = await apiClient.get('/analytics/dashboard')
    return withData(response, normalizeDashboard(response.data))
  },

  // Export
  exportAnalytics: async (format: string, timeframe?: string) => {
    let url = `/analytics/export/${format}`
    if (timeframe) url += `?timeframe=${timeframe}`
    return apiClient.get(url)
  },
}
