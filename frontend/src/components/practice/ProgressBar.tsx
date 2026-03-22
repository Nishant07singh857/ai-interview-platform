'use client'

import { Progress } from '@/components/ui/progress/Progress'

interface ProgressBarProps {
  progress: number
  current: number
  total: number
  correct: number
  incorrect: number
  timeElapsed: number
  timeLimit?: number
}

export const ProgressBar = ({
  progress,
  current,
  total,
  correct,
  incorrect,
  timeElapsed,
  timeLimit,
}: ProgressBarProps) => {
  const timeRemaining = timeLimit ? Math.max(timeLimit * 60 - timeElapsed, 0) : null

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between text-sm text-gray-600 dark:text-gray-400">
        <span>Question {current} of {total}</span>
        <span>{Math.round(progress)}% complete</span>
      </div>
      <Progress value={progress} variant="primary" />
      <div className="flex flex-wrap items-center justify-between text-xs text-gray-500 dark:text-gray-400 gap-2">
        <span>Correct: {correct}</span>
        <span>Incorrect: {incorrect}</span>
        <span>Time Elapsed: {Math.floor(timeElapsed / 60)}m</span>
        {timeRemaining !== null && (
          <span>Time Left: {Math.ceil(timeRemaining / 60)}m</span>
        )}
      </div>
    </div>
  )
}
