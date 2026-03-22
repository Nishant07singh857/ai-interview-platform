import { useCallback } from 'react'
import { useAppDispatch, useAppSelector } from '@/store/store'
import {
  uploadResume,
  parseResume,
  analyzeResume,
  analyzeGaps,
  generateRoadmap,
  fetchResumes,
  fetchResume,
  deleteResume,
} from '@/store/slices/resumeSlice'

export const useResume = () => {
  const dispatch = useAppDispatch()
  const {
    resumes,
    currentResume,
    parsedResume,
    analysis,
    gapAnalysis,
    roadmap,
    isLoading,
    uploadProgress,
    error,
  } = useAppSelector((state) => state.resume)

  const handleUploadResume = useCallback((file: File) => {
    return dispatch(uploadResume(file)).unwrap()
  }, [dispatch])

  const handleParseResume = useCallback((resumeId: string) => {
    return dispatch(parseResume(resumeId)).unwrap()
  }, [dispatch])

  const handleAnalyzeResume = useCallback((resumeId: string, targetCompany?: string, targetRole?: string) => {
    return dispatch(analyzeResume({ resumeId, targetCompany, targetRole })).unwrap()
  }, [dispatch])

  const handleAnalyzeGaps = useCallback((resumeId: string, targetCompany: string, targetRole: string, jobDescription?: string) => {
    return dispatch(analyzeGaps({ resumeId, targetCompany, targetRole, jobDescription })).unwrap()
  }, [dispatch])

  const handleGenerateRoadmap = useCallback((
    resumeId: string,
    targetCompany: string,
    targetRole: string,
    targetInterviewDate?: string,
    hoursPerWeek?: number
  ) => {
    return dispatch(generateRoadmap({ resumeId, targetCompany, targetRole, targetInterviewDate, hoursPerWeek })).unwrap()
  }, [dispatch])

  const handleFetchResumes = useCallback(() => {
    return dispatch(fetchResumes()).unwrap()
  }, [dispatch])

  const handleFetchResume = useCallback((resumeId: string) => {
    return dispatch(fetchResume(resumeId)).unwrap()
  }, [dispatch])

  const handleDeleteResume = useCallback((resumeId: string) => {
    return dispatch(deleteResume(resumeId)).unwrap()
  }, [dispatch])

  return {
    resumes,
    currentResume,
    parsedResume,
    analysis,
    gapAnalysis,
    roadmap,
    isLoading,
    uploadProgress,
    error,
    uploadResume: handleUploadResume,
    parseResume: handleParseResume,
    analyzeResume: handleAnalyzeResume,
    analyzeGaps: handleAnalyzeGaps,
    generateRoadmap: handleGenerateRoadmap,
    fetchResumes: handleFetchResumes,
    fetchResume: handleFetchResume,
    deleteResume: handleDeleteResume,
  }
}
