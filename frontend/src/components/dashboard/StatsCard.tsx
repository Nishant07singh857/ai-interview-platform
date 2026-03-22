'use client'

import { motion } from 'framer-motion'
import { Card } from '@/components/ui/card/Card'
import { ArrowTrendingUpIcon, ArrowTrendingDownIcon } from '@heroicons/react/24/outline'

interface StatsCardProps {
  title: string
  value: string | number
  description?: string
  icon: React.ReactNode
  trend?: {
    value: number
    label: string
    positive?: boolean
  }
  color?: 'primary' | 'success' | 'warning' | 'error' | 'info'
  isLoading?: boolean
}

const colorClasses = {
  primary: {
    bg: 'bg-primary-50 dark:bg-primary-900/20',
    text: 'text-primary-600 dark:text-primary-400',
    border: 'border-primary-200 dark:border-primary-800',
  },
  success: {
    bg: 'bg-success-50 dark:bg-success-900/20',
    text: 'text-success-600 dark:text-success-400',
    border: 'border-success-200 dark:border-success-800',
  },
  warning: {
    bg: 'bg-warning-50 dark:bg-warning-900/20',
    text: 'text-warning-600 dark:text-warning-400',
    border: 'border-warning-200 dark:border-warning-800',
  },
  error: {
    bg: 'bg-error-50 dark:bg-error-900/20',
    text: 'text-error-600 dark:text-error-400',
    border: 'border-error-200 dark:border-error-800',
  },
  info: {
    bg: 'bg-info-50 dark:bg-info-900/20',
    text: 'text-info-600 dark:text-info-400',
    border: 'border-info-200 dark:border-info-800',
  },
}

export const StatsCard = ({
  title,
  value,
  description,
  icon,
  trend,
  color = 'primary',
  isLoading = false,
}: StatsCardProps) => {
  const colors = colorClasses[color]

  if (isLoading) {
    return (
      <Card className="relative overflow-hidden">
        <div className="p-6">
          <div className="animate-pulse">
            <div className="flex items-center justify-between mb-4">
              <div className="h-10 w-10 rounded-lg bg-gray-200 dark:bg-gray-700"></div>
              <div className="h-4 w-16 bg-gray-200 dark:bg-gray-700 rounded"></div>
            </div>
            <div className="h-8 w-24 bg-gray-200 dark:bg-gray-700 rounded mb-2"></div>
            <div className="h-4 w-32 bg-gray-200 dark:bg-gray-700 rounded"></div>
          </div>
        </div>
      </Card>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card className="relative overflow-hidden group hover:shadow-lg transition-shadow duration-300">
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div className={`p-3 rounded-xl ${colors.bg} ${colors.text}`}>
              {icon}
            </div>
            {trend && (
              <div className={`flex items-center space-x-1 text-sm ${
                trend.positive ? 'text-success-600' : 'text-error-600'
              }`}>
                {trend.positive ? (
                  <ArrowTrendingUpIcon className="h-4 w-4" />
                ) : (
                  <ArrowTrendingDownIcon className="h-4 w-4" />
                )}
                <span className="font-medium">{trend.value}%</span>
                <span className="text-gray-500 dark:text-gray-400 text-xs">
                  {trend.label}
                </span>
              </div>
            )}
          </div>

          <div className="space-y-1">
            <h3 className="text-3xl font-bold text-gray-900 dark:text-white">
              {typeof value === 'number' ? value.toLocaleString() : value}
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">{title}</p>
            {description && (
              <p className="text-xs text-gray-500 dark:text-gray-500 mt-2">
                {description}
              </p>
            )}
          </div>
        </div>

        {/* Decorative gradient */}
        <div className={`absolute bottom-0 left-0 right-0 h-1 ${colors.bg}`} />
      </Card>
    </motion.div>
  )
}