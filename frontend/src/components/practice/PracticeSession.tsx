'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { QuestionCard } from './QuestionCard'
import { ProgressBar } from './ProgressBar'
import { ExplanationBox } from './ExplanationBox'
import { usePractice } from '@/hooks/usePractice'
import { Button } from '@/components/ui/button/Button'
import { Card } from '@/components/ui/card/Card'
import { Spinner } from '@/components/ui/spinner/Spinner'
import {
  PauseIcon,
  PlayIcon,
  FlagIcon,
} from '@heroicons/react/24/outline'

interface PracticeSessionProps {
  sessionId: string
}

export const PracticeSession = ({ sessionId }: PracticeSessionProps) => {
  const router = useRouter()
  const {
    currentSession,
    currentQuestion,
    nextQuestion,
    isLoading,
    submitAnswer,
    skipQuestion,
    pauseSession,
    resumeSession,
    endSession,
    advanceToNextQuestion,
  } = usePractice()

  const [isPaused, setIsPaused] = useState(false)
  const [showExplanation, setShowExplanation] = useState(false)
  const [answerExplanation, setAnswerExplanation] = useState<string>('')
  const [sessionCompleted, setSessionCompleted] = useState(false)

  if (isLoading || !currentSession || !currentQuestion) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Spinner size="lg" />
      </div>
    )
  }

  const handleAnswer = async (answer: any) => {
    const timeSpent = calculateTimeSpent()
    const result = await submitAnswer(answer, timeSpent)
    if (typeof result?.isCorrect === 'boolean') {
      setAnswerExplanation(result?.explanation ?? currentQuestion.explanation ?? '')
      setShowExplanation(true)
    }
    setSessionCompleted(Boolean(result?.sessionCompleted))
    return result
  }

  const handleNext = () => {
    setShowExplanation(false)
    setAnswerExplanation('')
    if (sessionCompleted) {
      router.push(`/practice/results/${sessionId}`)
      return
    }
    if (nextQuestion) {
      advanceToNextQuestion()
    }
  }

  const handleSkip = async () => {
    await skipQuestion()
    setShowExplanation(false)
    setAnswerExplanation('')
    setSessionCompleted(false)
  }

  const handlePause = async () => {
    await pauseSession()
    setIsPaused(true)
  }

  const handleResume = async () => {
    await resumeSession()
    setIsPaused(false)
  }

  const handleEnd = async () => {
    if (confirm('Are you sure you want to end this session?')) {
      await endSession()
      router.push(`/practice/results/${sessionId}`)
    }
  }

  const calculateTimeSpent = (): number => {
    // This would calculate actual time spent on question
    return 60 // Placeholder
  }

  const progress = (currentSession.questionsAnswered / currentSession.totalQuestions) * 100

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            {currentSession.title}
          </h1>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            {currentSession.description}
          </p>
        </div>
        <div className="flex items-center space-x-2">
          {!isPaused ? (
            <Button variant="outline" onClick={handlePause}>
              <PauseIcon className="h-4 w-4 mr-2" />
              Pause
            </Button>
          ) : (
            <Button variant="outline" onClick={handleResume}>
              <PlayIcon className="h-4 w-4 mr-2" />
              Resume
            </Button>
          )}
          <Button variant="ghost" onClick={handleEnd}>
            <FlagIcon className="h-4 w-4 mr-2" />
            End
          </Button>
        </div>
      </div>

      {/* Progress Bar */}
      <Card className="p-4">
        <ProgressBar
          progress={progress}
          current={currentSession.questionsAnswered}
          total={currentSession.totalQuestions}
          correct={currentSession.correctAnswers}
          incorrect={currentSession.incorrectAnswers}
          timeElapsed={currentSession.timeElapsed || 0}
          timeLimit={currentSession.timeLimit}
        />
      </Card>

      {/* Question */}
      <QuestionCard
        question={currentQuestion}
        totalQuestions={currentSession.totalQuestions}
        currentIndex={currentSession.currentQuestionIndex}
        timeLimit={currentSession.timeLimit}
        onAnswer={handleAnswer}
        onNext={handleNext}
        onPrevious={() => {}} // Would implement
        onSkip={handleSkip}
      />

      {/* Explanation */}
      {showExplanation && (
        <ExplanationBox
          explanation={answerExplanation || currentQuestion.explanation}
          detailedExplanation={currentQuestion.detailedExplanation}
          references={currentQuestion.references}
          commonMistakes={currentQuestion.commonMistakes}
        />
      )}
    </div>
  )
}
