'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card/Card'
import { Tooltip } from '@/components/ui/tooltip/Tooltip'
import { ChevronLeftIcon, ChevronRightIcon } from '@heroicons/react/24/outline'

interface ActivityHeatmapProps {
  data: Array<{
    date: string
    count: number
    intensity: 0 | 1 | 2 | 3 | 4
  }>
  year?: number
  onYearChange?: (year: number) => void
  isLoading?: boolean
}

const intensityColors = {
  0: 'bg-gray-100 dark:bg-gray-800',
  1: 'bg-primary-200 dark:bg-primary-900',
  2: 'bg-primary-300 dark:bg-primary-700',
  3: 'bg-primary-500 dark:bg-primary-600',
  4: 'bg-primary-700 dark:bg-primary-500',
}

const monthNames = [
  'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
]

export const ActivityHeatmap = ({
  data,
  year = new Date().getFullYear(),
  onYearChange,
  isLoading = false,
}: ActivityHeatmapProps) => {
  const [hoveredDay, setHoveredDay] = useState<{ date: string; count: number } | null>(null)

  const getWeeksInYear = (year: number) => {
    const firstDay = new Date(year, 0, 1)
    const lastDay = new Date(year, 11, 31)
    const days = Math.ceil((lastDay.getTime() - firstDay.getTime()) / (1000 * 60 * 60 * 24))
    return Math.ceil((firstDay.getDay() + days + 1) / 7)
  }

  const weeks = getWeeksInYear(year)
  const days = Array.from({ length: 7 }, (_, i) => i)

  const getActivityForDate = (date: Date) => {
    const dateStr = date.toISOString().split('T')[0]
    return data.find(d => d.date === dateStr) || { count: 0, intensity: 0 }
  }

  const handlePreviousYear = () => {
    onYearChange?.(year - 1)
  }

  const handleNextYear = () => {
    onYearChange?.(year + 1)
  }

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <div className="animate-pulse">
            <div className="h-6 w-48 bg-gray-200 dark:bg-gray-700 rounded mb-2"></div>
            <div className="h-4 w-32 bg-gray-200 dark:bg-gray-700 rounded"></div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="h-[200px] animate-pulse bg-gray-100 dark:bg-gray-800 rounded-lg"></div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle>Activity Heatmap</CardTitle>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Your practice activity throughout the year
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={handlePreviousYear}
            className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
          >
            <ChevronLeftIcon className="h-5 w-5" />
          </button>
          <span className="text-lg font-medium">{year}</span>
          <button
            onClick={handleNextYear}
            className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            disabled={year >= new Date().getFullYear()}
          >
            <ChevronRightIcon className="h-5 w-5" />
          </button>
        </div>
      </CardHeader>

      <CardContent>
        <div className="overflow-x-auto">
          <div className="min-w-[800px]">
            <div className="flex mb-2">
              <div className="w-8"></div>
              {monthNames.map((month, index) => (
                <div
                  key={month}
                  className="flex-1 text-xs text-gray-500 dark:text-gray-400 text-center"
                  style={{
                    gridColumn: `span ${index === 0 ? 4 : index === 11 ? 4 : 5}`,
                  }}
                >
                  {month}
                </div>
              ))}
            </div>

            <div className="flex">
              <div className="flex flex-col mr-2 text-xs text-gray-500 dark:text-gray-400">
                {['Mon', 'Wed', 'Fri'].map((day, i) => (
                  <div key={day} className="h-4 flex items-center mb-1">
                    {day}
                  </div>
                ))}
              </div>

              <div className="flex-1 grid grid-cols-52 gap-1">
                {Array.from({ length: weeks }, (_, weekIndex) => (
                  <div key={weekIndex} className="grid grid-rows-7 gap-1">
                    {days.map((dayIndex) => {
                      const date = new Date(year, 0, 1 + weekIndex * 7 + dayIndex)
                      if (date.getFullYear() !== year) return null

                      const activity = getActivityForDate(date)
                      const isToday = date.toDateString() === new Date().toDateString()

                      return (
                        <Tooltip
                          key={date.toISOString()}
                          content={
                            <div className="text-center">
                              <div className="font-medium">{date.toDateString()}</div>
                              <div className="text-sm">
                                {activity.count} questions completed
                              </div>
                            </div>
                          }
                        >
                          <motion.div
                            whileHover={{ scale: 1.2 }}
                            className={`
                              w-4 h-4 rounded-sm cursor-pointer transition-all
                              ${intensityColors[activity.intensity]}
                              ${isToday ? 'ring-2 ring-primary-500 ring-offset-2' : ''}
                            `}
                          />
                        </Tooltip>
                      )
                    })}
                  </div>
                ))}
              </div>
            </div>

            <div className="flex items-center justify-end mt-4 space-x-3">
              <span className="text-sm text-gray-600 dark:text-gray-400">Less</span>
              {[0, 1, 2, 3, 4].map((intensity) => (
                <div
                  key={intensity}
                  className={`w-4 h-4 rounded-sm ${intensityColors[intensity as keyof typeof intensityColors]}`}
                />
              ))}
              <span className="text-sm text-gray-600 dark:text-gray-400">More</span>
            </div>

            {hoveredDay && (
              <div className="mt-4 text-center text-sm text-gray-600 dark:text-gray-400">
                <span className="font-medium">{hoveredDay.date}:</span>{' '}
                {hoveredDay.count} questions completed
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}