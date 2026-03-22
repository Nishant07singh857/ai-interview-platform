'use client'

import { useState, useEffect } from 'react'
import { ClockIcon } from '@heroicons/react/24/outline'

interface TimerProps {
  initialTime: number // in seconds
  onTimeUp?: () => void
  isPaused?: boolean
  className?: string
}

export const Timer = ({ initialTime, onTimeUp, isPaused = false, className = '' }: TimerProps) => {
  const [timeLeft, setTimeLeft] = useState(initialTime)

  useEffect(() => {
    if (isPaused || timeLeft <= 0) return

    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          clearInterval(timer)
          onTimeUp?.()
          return 0
        }
        return prev - 1
      })
    }, 1000)

    return () => clearInterval(timer)
  }, [timeLeft, isPaused, onTimeUp])

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  const getTimerColor = () => {
    const percentage = (timeLeft / initialTime) * 100
    if (percentage <= 25) return 'text-error-600'
    if (percentage <= 50) return 'text-warning-600'
    return 'text-gray-700 dark:text-gray-300'
  }

  return (
    <div className={`flex items-center space-x-2 ${className}`}>
      <ClockIcon className={`h-5 w-5 ${getTimerColor()}`} />
      <span className={`font-mono font-medium ${getTimerColor()}`}>
        {formatTime(timeLeft)}
      </span>
    </div>
  )
}