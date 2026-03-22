'use client'

import { motion } from 'framer-motion'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card/Card'
import { Badge } from '@/components/ui/badge/Badge'
import { 
  CheckCircleIcon, 
  XCircleIcon,
  ClockIcon,
  ArrowPathIcon,
  DocumentTextIcon,
  MicrophoneIcon 
} from '@heroicons/react/24/outline'

interface RecentActivityProps {
  activities: Array<{
    id: string
    type: 'practice' | 'mock_test' | 'resume' | 'interview'
    title: string
    description?: string
    result?: 'passed' | 'failed' | 'completed'
    score?: number
    timeAgo: string
    icon?: React.ReactNode
  }>
  isLoading?: boolean
  onViewAll?: () => void
}

const activityIcons = {
  practice: <ArrowPathIcon className="h-5 w-5" />,
  mock_test: <DocumentTextIcon className="h-5 w-5" />,
  resume: <DocumentTextIcon className="h-5 w-5" />,
  interview: <MicrophoneIcon className="h-5 w-5" />,
}

const activityColors = {
  practice: 'bg-blue-100 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400',
  mock_test: 'bg-purple-100 text-purple-600 dark:bg-purple-900/20 dark:text-purple-400',
  resume: 'bg-green-100 text-green-600 dark:bg-green-900/20 dark:text-green-400',
  interview: 'bg-orange-100 text-orange-600 dark:bg-orange-900/20 dark:text-orange-400',
}

export const RecentActivity = ({
  activities,
  isLoading = false,
  onViewAll,
}: RecentActivityProps) => {
  const getResultIcon = (result?: string) => {
    if (result === 'passed' || result === 'completed') {
      return <CheckCircleIcon className="h-4 w-4 text-success-500" />
    }
    if (result === 'failed') {
      return <XCircleIcon className="h-4 w-4 text-error-500" />
    }
    return null
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
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="flex items-start space-x-3 animate-pulse">
                <div className="w-10 h-10 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
                <div className="flex-1">
                  <div className="h-5 w-32 bg-gray-200 dark:bg-gray-700 rounded mb-2"></div>
                  <div className="h-4 w-48 bg-gray-200 dark:bg-gray-700 rounded"></div>
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
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle>Recent Activity</CardTitle>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Your latest practice sessions and achievements
          </p>
        </div>
        {onViewAll && (
          <button
            onClick={onViewAll}
            className="text-sm text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300 font-medium"
          >
            View all
          </button>
        )}
      </CardHeader>

      <CardContent>
        <div className="space-y-4">
          {activities.length === 0 ? (
            <div className="text-center py-8">
              <div className="mx-auto w-12 h-12 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center mb-4">
                <ClockIcon className="h-6 w-6 text-gray-400" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                No Activity Yet
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Start practicing to see your activity here
              </p>
            </div>
          ) : (
            activities.map((activity, index) => (
              <motion.div
                key={activity.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="flex items-start space-x-3 p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors group cursor-pointer"
              >
                <div className={`flex-shrink-0 w-10 h-10 rounded-lg flex items-center justify-center ${activityColors[activity.type]}`}>
                  {activity.icon || activityIcons[activity.type]}
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-1">
                    <h4 className="text-sm font-medium text-gray-900 dark:text-white truncate">
                      {activity.title}
                    </h4>
                    <div className="flex items-center space-x-2">
                      {getResultIcon(activity.result)}
                      {activity.score !== undefined && (
                        <Badge variant={activity.score >= 70 ? 'success' : 'warning'} size="sm">
                          {activity.score}%
                        </Badge>
                      )}
                    </div>
                  </div>
                  
                  {activity.description && (
                    <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">
                      {activity.description}
                    </p>
                  )}

                  <div className="flex items-center text-xs text-gray-500 dark:text-gray-500">
                    <ClockIcon className="h-3 w-3 mr-1" />
                    {activity.timeAgo}
                  </div>
                </div>
              </motion.div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  )
}