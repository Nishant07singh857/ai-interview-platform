import { useAppDispatch, useAppSelector } from '@/store/store'
import {
  startQuickQuiz,
  startTopicPractice,
  startMockTest,
  startCompanyPractice,
  submitAnswer,
  skipQuestion,
  pauseSession,
  resumeSession,
  endSession,
  fetchSession,
  fetchSessionResults,
  fetchPracticeHistory,
  fetchLeaderboard,
  submitFeedback,
  clearCurrentSession,
  advanceToNextQuestion,
} from '@/store/slices/practiceSlice'
import { useRouter } from 'next/navigation'
import toast from 'react-hot-toast'

export const usePractice = () => {
  const dispatch = useAppDispatch()
  const router = useRouter()
  const {
    currentSession,
    currentQuestion,
    nextQuestion,
    history,
    leaderboard,
    isLoading,
    error,
  } = useAppSelector((state) => state.practice)

  const getSessionId = (result: any): string | null => {
    const id = result?.session_id || result?.sessionId || result?.id
    return id ? String(id).trim() : null
  }

  const handleStartQuickQuiz = async (config?: {
    totalQuestions?: number
    timeLimit?: number
    subjects?: string[]
  }) => {
    try {
      const result = await dispatch(startQuickQuiz(config || {})).unwrap()
      const sessionId = getSessionId(result)
      
      if (!sessionId || sessionId === 'undefined' || sessionId === 'null' || sessionId === '') {
        throw new Error('No valid session ID returned from server')
      }
      
      router.push(`/practice/session/${sessionId}`)
      return result
    } catch (error: any) {
      toast.error(error?.message || 'Failed to start quiz')
      throw error
    }
  }

  const handleStartTopicPractice = async (config: {
    subject: string
    topic: string
    subtopics?: string[]
    totalQuestions?: number
    difficulty?: string
  }) => {
    try {
      const result = await dispatch(startTopicPractice(config)).unwrap()
      
      const sessionId = getSessionId(result)
      
      if (!sessionId || sessionId === 'undefined' || sessionId === 'null' || sessionId === '') {
        throw new Error('No valid session ID returned from server')
      }
      
      router.push(`/practice/session/${sessionId}`)
      
      return result
    } catch (error: any) {
      toast.error(error?.message || 'Failed to start practice')
      throw error
    }
  }

  const handleStartMockTest = async (config: {
    subject: string
    title?: string
    totalQuestions?: number
    timeLimit?: number
  }) => {
    try {
      const result = await dispatch(startMockTest(config)).unwrap()
      const sessionId = getSessionId(result)
      
      if (!sessionId || sessionId === 'undefined' || sessionId === 'null' || sessionId === '') {
        throw new Error('No valid session ID returned from server')
      }
      
      router.push(`/practice/session/${sessionId}`)
      return result
    } catch (error: any) {
      if (error?.status === 403) {
        toast.error('Mock tests are a Pro feature. Upgrade to access.')
        return null
      }
      toast.error(error?.message || 'Failed to start mock test')
      throw error
    }
  }

  const handleStartCompanyPractice = async (config: {
    company: string
    role?: string
    totalQuestions?: number
  }) => {
    try {
      const result = await dispatch(startCompanyPractice(config)).unwrap()
      const sessionId = getSessionId(result)
      
      if (!sessionId || sessionId === 'undefined' || sessionId === 'null' || sessionId === '') {
        throw new Error('No valid session ID returned from server')
      }
      
      router.push(`/practice/session/${sessionId}`)
      return result
    } catch (error: any) {
      if (error?.status === 403) {
        toast.error('Company practice is a Pro feature. Upgrade to access.')
        return null
      }
      toast.error(error?.message || 'Failed to start company practice')
      throw error
    }
  }

  const handleSubmitAnswer = async (answer: any, timeTaken: number) => {
    if (!currentSession || !currentQuestion) {
      toast.error('No active session')
      return
    }

    try {
      const result = await dispatch(
        submitAnswer({
          sessionId: currentSession.sessionId,
          questionId: (currentQuestion as any)?.questionId || (currentQuestion as any)?.question_id || (currentQuestion as any)?.id,
          answer,
          timeTaken,
        })
      ).unwrap()

      return result
    } catch (error: any) {
      toast.error(error?.message || 'Failed to submit answer')
      throw error
    }
  }

  const handleSkipQuestion = async () => {
    if (!currentSession) {
      toast.error('No active session')
      return
    }

    try {
      const result = await dispatch(skipQuestion(currentSession.sessionId)).unwrap()

      if (result.sessionCompleted) {
        toast.success('Practice session completed!')
        router.push(`/practice/results/${currentSession.sessionId}`)
      }

      return result
    } catch (error: any) {
      toast.error(error?.message || 'Failed to skip question')
      throw error
    }
  }

  const handlePauseSession = async () => {
    if (!currentSession) return

    try {
      await dispatch(pauseSession(currentSession.sessionId)).unwrap()
      toast.success('Session paused')
    } catch (error: any) {
      toast.error(error?.message || 'Failed to pause session')
      throw error
    }
  }

  const handleResumeSession = async () => {
    if (!currentSession) return

    try {
      await dispatch(resumeSession(currentSession.sessionId)).unwrap()
    } catch (error: any) {
      toast.error(error?.message || 'Failed to resume session')
      throw error
    }
  }

  const handleEndSession = async () => {
    if (!currentSession) return

    try {
      await dispatch(endSession(currentSession.sessionId)).unwrap()
      router.push(`/practice/results/${currentSession.sessionId}`)
    } catch (error: any) {
      toast.error(error?.message || 'Failed to end session')
      throw error
    }
  }

  const handleAdvanceToNextQuestion = () => {
    dispatch(advanceToNextQuestion())
  }

  const handleLoadSession = async (sessionId: string) => {
    if (!sessionId || sessionId === 'undefined' || sessionId === 'null' || sessionId === '') {
      router.push('/practice')
      return
    }

    try {
      await dispatch(fetchSession(sessionId)).unwrap()
    } catch (error: any) {
      router.push('/practice')
      throw error
    }
  }

  const handleLoadResults = async (sessionId: string) => {
    if (!sessionId || sessionId === 'undefined' || sessionId === 'null' || sessionId === '') {
      router.push('/practice')
      return
    }

    try {
      const result = await dispatch(fetchSessionResults(sessionId)).unwrap()
      return result
    } catch (error: any) {
      toast.error(error?.message || 'Failed to load results')
      throw error
    }
  }

  const handleLoadHistory = async (days?: number, type?: any) => {
    try {
      await dispatch(fetchPracticeHistory({ days, type })).unwrap()
    } catch (error: any) {
      toast.error(error?.message || 'Failed to load history')
      throw error
    }
  }

  const handleLoadLeaderboard = async (subject: string, period?: string, limit?: number) => {
    try {
      await dispatch(fetchLeaderboard({ subject, period, limit })).unwrap()
    } catch (error: any) {
      toast.error(error?.message || 'Failed to load leaderboard')
      throw error
    }
  }

  const handleSubmitFeedback = async (rating: number, feedback?: string) => {
    if (!currentSession) return

    try {
      await dispatch(
        submitFeedback({
          sessionId: currentSession.sessionId,
          rating,
          feedback,
        })
      ).unwrap()
      toast.success('Thank you for your feedback!')
    } catch (error: any) {
      toast.error(error?.message || 'Failed to submit feedback')
      throw error
    }
  }

  const handleClearSession = () => {
    dispatch(clearCurrentSession())
  }

  return {
    currentSession,
    currentQuestion,
    nextQuestion,
    history,
    leaderboard,
    isLoading,
    error,
    startQuickQuiz: handleStartQuickQuiz,
    startTopicPractice: handleStartTopicPractice,
    startMockTest: handleStartMockTest,
    startCompanyPractice: handleStartCompanyPractice,
    submitAnswer: handleSubmitAnswer,
    skipQuestion: handleSkipQuestion,
    pauseSession: handlePauseSession,
    resumeSession: handleResumeSession,
    endSession: handleEndSession,
    advanceToNextQuestion: handleAdvanceToNextQuestion,
    loadSession: handleLoadSession,
    loadResults: handleLoadResults,
    loadHistory: handleLoadHistory,
    loadLeaderboard: handleLoadLeaderboard,
    submitFeedback: handleSubmitFeedback,
    clearSession: handleClearSession,
  }
}
