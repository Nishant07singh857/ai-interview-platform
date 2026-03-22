import { useCallback } from 'react'
import { useAppDispatch, useAppSelector } from '@/store/store'
import {
  fetchAnalyticsSummary,
  fetchPerformanceTrends,
  fetchSubjectPerformance,
  fetchTopicMastery,
  fetchCompanyReadiness,
  fetchDifficultyPerformance,
  fetchQuestionTypePerformance,
  fetchTimeAnalysis,
  exportAnalytics,
  fetchDashboardData,
} from '@/store/slices/analyticsSlice'

export const useAnalytics = () => {
  const dispatch = useAppDispatch()
  const {
    summary,
    trends,
    subjectPerformance,
    topicMastery,
    companyReadiness,
    difficultyPerformance,
    questionTypePerformance,
    timeAnalysis,
    recommendations,
    streakInfo,
    recentActivity,
    isLoading,
    error,
  } = useAppSelector((state) => state.analytics)

  const handleFetchAnalyticsSummary = useCallback(() => {
    return dispatch(fetchAnalyticsSummary()).unwrap()
  }, [dispatch])

  const handleFetchPerformanceTrends = useCallback((days: number) => {
    return dispatch(fetchPerformanceTrends(days)).unwrap()
  }, [dispatch])

  const handleFetchSubjectPerformance = useCallback(() => {
    return dispatch(fetchSubjectPerformance()).unwrap()
  }, [dispatch])

  const handleFetchTopicMastery = useCallback((subject?: string) => {
    return dispatch(fetchTopicMastery(subject)).unwrap()
  }, [dispatch])

  const handleFetchCompanyReadiness = useCallback(() => {
    return dispatch(fetchCompanyReadiness()).unwrap()
  }, [dispatch])

  const handleFetchDifficultyPerformance = useCallback(() => {
    return dispatch(fetchDifficultyPerformance()).unwrap()
  }, [dispatch])

  const handleFetchQuestionTypePerformance = useCallback(() => {
    return dispatch(fetchQuestionTypePerformance()).unwrap()
  }, [dispatch])

  const handleFetchTimeAnalysis = useCallback(() => {
    return dispatch(fetchTimeAnalysis()).unwrap()
  }, [dispatch])

  const handleExportAnalytics = useCallback((format: string, timeframe?: string) => {
    return dispatch(exportAnalytics({ format, timeframe })).unwrap()
  }, [dispatch])

  const handleFetchDashboardData = useCallback(() => {
    return dispatch(fetchDashboardData()).unwrap()
  }, [dispatch])

  return {
    summary,
    trends,
    subjectPerformance,
    topicMastery,
    companyReadiness,
    difficultyPerformance,
    questionTypePerformance,
    timeAnalysis,
    recommendations,
    streakInfo,
    recentActivity,
    isLoading,
    error,
    fetchAnalyticsSummary: handleFetchAnalyticsSummary,
    fetchPerformanceTrends: handleFetchPerformanceTrends,
    fetchSubjectPerformance: handleFetchSubjectPerformance,
    fetchTopicMastery: handleFetchTopicMastery,
    fetchCompanyReadiness: handleFetchCompanyReadiness,
    fetchDifficultyPerformance: handleFetchDifficultyPerformance,
    fetchQuestionTypePerformance: handleFetchQuestionTypePerformance,
    fetchTimeAnalysis: handleFetchTimeAnalysis,
    exportAnalytics: handleExportAnalytics,
    fetchDashboardData: handleFetchDashboardData,
  }
}
