'use client'

import { motion } from 'framer-motion'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card/Card'
import { Progress } from '@/components/ui/progress/Progress'
import { Badge } from '@/components/ui/badge/Badge'
import { 
  AcademicCapIcon, 
  ChartBarIcon, 
  ClockIcon,
  ArrowPathIcon 
} from '@heroicons/react/24/outline'

interface TopicMasteryProps {
  data: {
    masteredTopics: Array<{
      topic: string
      accuracy: number
      attempts: number
      lastPracticed?: string
    }>
    inProgressTopics: Array<{
      topic: string
      accuracy: number
      attempts: number
      lastPracticed?: string
    }>
    notStartedTopics: Array<{
      topic: string
    }>
  }
  isLoading?: boolean
  onTopicClick?: (topic: string) => void
}

export const TopicMastery = ({
  data,
  isLoading = false,
  onTopicClick,
}: TopicMasteryProps) => {
  const getMasteryColor = (accuracy: number) => {
    if (accuracy >= 80) return 'success'
    if (accuracy >= 60) return 'primary'
    if (accuracy >= 40) return 'warning'
    return 'error'
  }

  const getMasteryIcon = (accuracy: number) => {
    if (accuracy >= 80) return '🎯'
    if (accuracy >= 60) return '📊'
    if (accuracy >= 40) return '📝'
    return '🎯'
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
          <div className="space-y-6">
            {[1, 2, 3].map((i) => (
              <div key={i} className="space-y-3">
                <div className="h-5 w-32 bg-gray-200 dark:bg-gray-700 rounded"></div>
                <div className="space-y-2">
                  {[1, 2].map((j) => (
                    <div key={j} className="animate-pulse">
                      <div className="flex justify-between mb-1">
                        <div className="h-4 w-24 bg-gray-200 dark:bg-gray-700 rounded"></div>
                        <div className="h-4 w-12 bg-gray-200 dark:bg-gray-700 rounded"></div>
                      </div>
                      <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded"></div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Topic Mastery</CardTitle>
        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
          Your proficiency across different topics
        </p>
      </CardHeader>

      <CardContent>
        <div className="space-y-6">
          {/* Mastered Topics */}
          {data.masteredTopics.length > 0 && (
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <AcademicCapIcon className="h-5 w-5 text-success-500" />
                <h4 className="text-sm font-medium text-gray-900 dark:text-white">
                  Mastered ({data.masteredTopics.length})
                </h4>
              </div>
              <div className="space-y-3">
                {data.masteredTopics.map((topic, index) => (
                  <motion.div
                    key={topic.topic}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="group cursor-pointer"
                    onClick={() => onTopicClick?.(topic.topic)}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center space-x-2">
                        <span className="text-lg">{getMasteryIcon(topic.accuracy)}</span>
                        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                          {topic.topic}
                        </span>
                        <Badge variant={getMasteryColor(topic.accuracy)} size="sm">
                          {topic.accuracy}%
                        </Badge>
                      </div>
                      <div className="flex items-center space-x-3 text-xs text-gray-500 dark:text-gray-400">
                        <span className="flex items-center">
                          <ChartBarIcon className="h-3 w-3 mr-1" />
                          {topic.attempts} attempts
                        </span>
                        {topic.lastPracticed && (
                          <span className="flex items-center">
                            <ClockIcon className="h-3 w-3 mr-1" />
                            {new Date(topic.lastPracticed).toLocaleDateString()}
                          </span>
                        )}
                      </div>
                    </div>
                    <Progress 
                      value={topic.accuracy} 
                      variant={getMasteryColor(topic.accuracy)}
                      size="sm"
                    />
                  </motion.div>
                ))}
              </div>
            </div>
          )}

          {/* In Progress Topics */}
          {data.inProgressTopics.length > 0 && (
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <ArrowPathIcon className="h-5 w-5 text-primary-500" />
                <h4 className="text-sm font-medium text-gray-900 dark:text-white">
                  In Progress ({data.inProgressTopics.length})
                </h4>
              </div>
              <div className="space-y-3">
                {data.inProgressTopics.map((topic, index) => (
                  <motion.div
                    key={topic.topic}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="group cursor-pointer"
                    onClick={() => onTopicClick?.(topic.topic)}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center space-x-2">
                        <span className="text-lg">{getMasteryIcon(topic.accuracy)}</span>
                        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                          {topic.topic}
                        </span>
                        <Badge variant={getMasteryColor(topic.accuracy)} size="sm">
                          {topic.accuracy}%
                        </Badge>
                      </div>
                      <div className="flex items-center space-x-3 text-xs text-gray-500 dark:text-gray-400">
                        <span className="flex items-center">
                          <ChartBarIcon className="h-3 w-3 mr-1" />
                          {topic.attempts} attempts
                        </span>
                        {topic.lastPracticed && (
                          <span className="flex items-center">
                            <ClockIcon className="h-3 w-3 mr-1" />
                            {new Date(topic.lastPracticed).toLocaleDateString()}
                          </span>
                        )}
                      </div>
                    </div>
                    <Progress 
                      value={topic.accuracy} 
                      variant={getMasteryColor(topic.accuracy)}
                      size="sm"
                    />
                  </motion.div>
                ))}
              </div>
            </div>
          )}

          {/* Not Started Topics */}
          {data.notStartedTopics.length > 0 && (
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <ClockIcon className="h-5 w-5 text-gray-400" />
                <h4 className="text-sm font-medium text-gray-900 dark:text-white">
                  Not Started ({data.notStartedTopics.length})
                </h4>
              </div>
              <div className="flex flex-wrap gap-2">
                {data.notStartedTopics.map((topic) => (
                  <Badge
                    key={topic.topic}
                    variant="secondary"
                    className="cursor-pointer hover:bg-gray-200 dark:hover:bg-gray-700"
                    onClick={() => onTopicClick?.(topic.topic)}
                  >
                    {topic.topic}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Summary Stats */}
        <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {data.masteredTopics.length}
              </div>
              <div className="text-xs text-gray-600 dark:text-gray-400">Mastered</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {data.inProgressTopics.length}
              </div>
              <div className="text-xs text-gray-600 dark:text-gray-400">In Progress</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {data.notStartedTopics.length}
              </div>
              <div className="text-xs text-gray-600 dark:text-gray-400">Not Started</div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}