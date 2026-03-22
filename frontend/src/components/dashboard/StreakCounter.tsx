'use client'

import { motion } from 'framer-motion'
import { Card } from '@/components/ui/card/Card'
import { FireIcon, TrophyIcon } from '@heroicons/react/24/solid'
import { CalendarDaysIcon } from '@heroicons/react/24/outline'

interface StreakCounterProps {
  currentStreak: number
  longestStreak: number
  lastActive?: string
  isLoading?: boolean
}

export const StreakCounter = ({
  currentStreak,
  longestStreak,
  lastActive,
  isLoading = false,
}: StreakCounterProps) => {
  const getStreakMessage = () => {
    if (currentStreak === 0) {
      return "Start your streak today!"
    }
    if (currentStreak < 3) {
      return "Keep it going!"
    }
    if (currentStreak < 7) {
      return "Great consistency!"
    }
    if (currentStreak < 30) {
      return "Amazing dedication!"
    }
    return "Incredible! You're on fire!"
  }

  const getStreakColor = () => {
    if (currentStreak >= 30) return 'text-purple-500'
    if (currentStreak >= 7) return 'text-orange-500'
    if (currentStreak >= 3) return 'text-yellow-500'
    return 'text-gray-500'
  }

  if (isLoading) {
    return (
      <Card className="bg-gradient-to-br from-primary-50 to-primary-100 dark:from-primary-900/20 dark:to-primary-800/20">
        <div className="p-6">
          <div className="animate-pulse space-y-4">
            <div className="h-8 w-32 bg-primary-200 dark:bg-primary-800 rounded"></div>
            <div className="h-12 w-24 bg-primary-300 dark:bg-primary-700 rounded"></div>
            <div className="h-4 w-48 bg-primary-200 dark:bg-primary-800 rounded"></div>
          </div>
        </div>
      </Card>
    )
  }

  return (
    <Card className="bg-gradient-to-br from-primary-50 to-primary-100 dark:from-primary-900/20 dark:to-primary-800/20 overflow-hidden relative">
      <div className="absolute top-0 right-0 w-32 h-32 transform translate-x-16 -translate-y-8">
        <FireIcon className="w-full h-full text-primary-200 dark:text-primary-800 opacity-30" />
      </div>

      <div className="p-6 relative z-10">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Practice Streak
          </h3>
          <div className="flex items-center space-x-2">
            <TrophyIcon className="h-5 w-5 text-yellow-500" />
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Best: {longestStreak}
            </span>
          </div>
        </div>

        <div className="flex items-end space-x-2 mb-2">
          <motion.span
            key={currentStreak}
            initial={{ scale: 0.5, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className={`text-6xl font-bold ${getStreakColor()}`}
          >
            {currentStreak}
          </motion.span>
          <span className="text-2xl font-medium text-gray-600 dark:text-gray-400 mb-2">
            days
          </span>
        </div>

        <p className="text-gray-700 dark:text-gray-300 font-medium">
          {getStreakMessage()}
        </p>

        {lastActive && (
          <div className="mt-4 flex items-center text-sm text-gray-600 dark:text-gray-400">
            <CalendarDaysIcon className="h-4 w-4 mr-1" />
            Last active: {new Date(lastActive).toLocaleDateString('en-US', {
              weekday: 'long',
              year: 'numeric',
              month: 'long',
              day: 'numeric',
            })}
          </div>
        )}

        {/* Streak flames */}
        <div className="mt-4 flex space-x-1">
          {[1, 2, 3, 4, 5, 6, 7].map((day) => (
            <motion.div
              key={day}
              initial={{ scale: 0 }}
              animate={{ scale: day <= currentStreak ? 1 : 0.8 }}
              className={`flex-1 h-1.5 rounded-full ${
                day <= currentStreak
                  ? 'bg-gradient-to-r from-orange-400 to-red-500'
                  : 'bg-gray-300 dark:bg-gray-700'
              }`}
            />
          ))}
        </div>
      </div>
    </Card>
  )
}