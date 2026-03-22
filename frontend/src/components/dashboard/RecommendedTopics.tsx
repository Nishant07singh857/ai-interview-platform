'use client'

import { motion } from 'framer-motion'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card/Card'
import { Button } from '@/components/ui/button/Button'
import { Badge } from '@/components/ui/badge/Badge'
import { 
  LightBulbIcon, 
  ArrowRightIcon,
  AcademicCapIcon,
  ClockIcon 
} from '@heroicons/react/24/outline'

interface RecommendedTopicsProps {
  recommendations: Array<{
    topic: string
    reason: string
    priority: 'high' | 'medium' | 'low'
    estimatedTime?: string
    questionCount?: number
  }>
  isLoading?: boolean
  onTopicClick?: (topic: string) => void
}

export const RecommendedTopics = ({
  recommendations,
  isLoading = false,
  onTopicClick,
}: RecommendedTopicsProps) => {
  const priorityColors = {
    high: 'error',
    medium: 'warning',
    low: 'success',
  } as const

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
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="animate-pulse">
                <div className="flex justify-between mb-2">
                  <div className="h-5 w-32 bg-gray-200 dark:bg-gray-700 rounded"></div>
                  <div className="h-5 w-16 bg-gray-200 dark:bg-gray-700 rounded"></div>
                </div>
                <div className="h-4 w-full bg-gray-200 dark:bg-gray-700 rounded mb-2"></div>
                <div className="h-8 w-24 bg-gray-200 dark:bg-gray-700 rounded"></div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  if (recommendations.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Recommended Topics</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <div className="mx-auto w-12 h-12 bg-primary-100 dark:bg-primary-900/20 rounded-full flex items-center justify-center mb-4">
              <AcademicCapIcon className="h-6 w-6 text-primary-600 dark:text-primary-400" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              All Caught Up!
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              You're doing great! Check back later for new recommendations.
            </p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center space-x-2">
          <LightBulbIcon className="h-5 w-5 text-yellow-500" />
          <CardTitle>Recommended for You</CardTitle>
        </div>
        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
          Based on your performance and goals
        </p>
      </CardHeader>

      <CardContent>
        <div className="space-y-4">
          {recommendations.map((rec, index) => (
            <motion.div
              key={rec.topic}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="group relative p-4 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-primary-300 dark:hover:border-primary-600 transition-colors cursor-pointer"
              onClick={() => onTopicClick?.(rec.topic)}
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-1">
                    <h4 className="text-base font-semibold text-gray-900 dark:text-white">
                      {rec.topic}
                    </h4>
                    <Badge variant={priorityColors[rec.priority]} size="sm">
                      {rec.priority} priority
                    </Badge>
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {rec.reason}
                  </p>
                </div>
                <ArrowRightIcon className="h-5 w-5 text-gray-400 group-hover:text-primary-500 transition-colors" />
              </div>

              <div className="flex items-center space-x-4 mt-3 text-xs text-gray-500 dark:text-gray-500">
                {rec.estimatedTime && (
                  <span className="flex items-center">
                    <ClockIcon className="h-3.5 w-3.5 mr-1" />
                    {rec.estimatedTime}
                  </span>
                )}
                {rec.questionCount && (
                  <span className="flex items-center">
                    <AcademicCapIcon className="h-3.5 w-3.5 mr-1" />
                    {rec.questionCount} questions
                  </span>
                )}
              </div>

              <div className="mt-3">
                <Button size="sm" variant="outline" className="w-full">
                  Start Practicing
                </Button>
              </div>
            </motion.div>
          ))}
        </div>

        <div className="mt-4 text-center">
          <Button variant="ghost" size="sm">
            View All Recommendations
            <ArrowRightIcon className="h-4 w-4 ml-1" />
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}