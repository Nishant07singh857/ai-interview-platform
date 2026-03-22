 'use client'

import { useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { InterviewSetup } from '@/components/interview/InterviewSetup'
import { InterviewSession } from '@/components/interview/InterviewSession'
import { Spinner } from '@/components/ui/spinner/Spinner'
import { Button } from '@/components/ui/button/Button'
import { useAppDispatch, useAppSelector } from '@/store/store'
import {
  startInterview,
  fetchSession,
  pauseSession,
  resumeSession,
  endSession,
  submitResponse,
  getCurrentQuestion,
  getHint,
  clearCurrentSession,
} from '@/store/slices/interviewSlice'
import toast from 'react-hot-toast'

export default function AiInterviewerPage() {
  const router = useRouter()
  const dispatch = useAppDispatch()
  const questionStartRef = useRef<number>(Date.now())

  const {
    currentSession,
    currentQuestion,
    isLoading,
  } = useAppSelector((state) => state.interview)

  useEffect(() => {
    if (currentQuestion?.questionId || (currentQuestion as any)?.question_id) {
      questionStartRef.current = Date.now()
    }
  }, [currentQuestion])

  const handleStart = async (data: any) => {
    try {
      const session = await dispatch(startInterview(data)).unwrap()
      const sessionId = session?.sessionId || session?.session_id
      if (sessionId) {
        await dispatch(fetchSession(sessionId))
      }
    } catch (error: any) {
      if (error?.status === 403) {
        toast.error('AI Interview is a Pro feature. Upgrade to access.')
        return
      }
      toast.error(error?.message || 'Failed to start interview')
    }
  }

  const handleResponse = async (response: { text?: string; audio?: Blob; video?: Blob }) => {
    if (!currentSession || !currentQuestion) return
    const sessionId = currentSession.sessionId || (currentSession as any).session_id
    const questionId = currentQuestion.questionId || (currentQuestion as any).question_id
    const timeTaken = Math.max(1, Math.round((Date.now() - questionStartRef.current) / 1000))

    await dispatch(
      submitResponse({
        sessionId,
        questionId,
        text: response.text,
        audio: response.audio,
        timeTaken,
      })
    ).unwrap()
  }

  const handleNext = async () => {
    if (!currentSession) return
    const sessionId = currentSession.sessionId || (currentSession as any).session_id
    await dispatch(getCurrentQuestion(sessionId))
  }

  const handlePause = async () => {
    if (!currentSession) return
    const sessionId = currentSession.sessionId || (currentSession as any).session_id
    await dispatch(pauseSession(sessionId))
  }

  const handleResume = async () => {
    if (!currentSession) return
    const sessionId = currentSession.sessionId || (currentSession as any).session_id
    await dispatch(resumeSession(sessionId))
  }

  const handleEnd = async () => {
    if (!currentSession) return
    const sessionId = currentSession.sessionId || (currentSession as any).session_id
    await dispatch(endSession(sessionId))
    dispatch(clearCurrentSession())
  }

  const handleHint = async () => {
    if (!currentSession || !currentQuestion) return
    const sessionId = currentSession.sessionId || (currentSession as any).session_id
    const questionId = currentQuestion.questionId || (currentQuestion as any).question_id
    await dispatch(getHint({ sessionId, questionId }))
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Spinner size="lg" />
      </div>
    )
  }

  if (!currentSession || !currentQuestion) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">AI Interview</h1>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Configure your interview and start practicing
          </p>
        </div>
        <InterviewSetup onSubmit={handleStart} isLoading={isLoading} />
      </div>
    )
  }

  const sessionId = currentSession.sessionId || (currentSession as any).session_id || ''
  const interviewType = currentSession.interviewType || (currentSession as any).interview_type || 'mixed'
  const questionNumber = (currentSession.currentQuestionIndex || (currentSession as any).current_question_index || 0) + 1
  const totalQuestions = currentSession.totalQuestions || (currentSession as any).total_questions || 0
  const timeElapsed = currentSession.timeElapsed || (currentSession as any).time_elapsed || 0
  const timeRemaining = currentSession.timeRemaining || (currentSession as any).time_remaining || 0
  const isPaused = currentSession.status === 'paused'

  const mappedQuestion = {
    questionId: currentQuestion.questionId || (currentQuestion as any).question_id || '',
    questionText: currentQuestion.questionText || (currentQuestion as any).question_text || (currentQuestion as any).question || '',
    context: (currentQuestion as any).context,
    category: currentQuestion.category || (currentQuestion as any).category || 'technical',
    difficulty: currentQuestion.difficulty || (currentQuestion as any).difficulty || 'intermediate',
    hint: (currentQuestion as any).hint,
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">AI Interview</h1>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Session in progress
          </p>
        </div>
        <Button variant="outline" onClick={() => router.push('/practice')}>
          Back to Practice
        </Button>
      </div>

      <InterviewSession
        sessionId={sessionId}
        interviewType={interviewType}
        currentQuestion={mappedQuestion}
        questionNumber={questionNumber}
        totalQuestions={totalQuestions}
        timeElapsed={timeElapsed}
        timeRemaining={timeRemaining}
        onResponse={handleResponse}
        onNext={handleNext}
        onPause={handlePause}
        onResume={handleResume}
        onEnd={handleEnd}
        onHint={handleHint}
        isLoading={isLoading}
        isPaused={isPaused}
      />
    </div>
  )
}
