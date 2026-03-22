"use client";

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'
import { useAnalytics } from '@/hooks/useAnalytics'
import { StatsCard } from '@/components/dashboard/StatsCard'
import { ProgressChart } from '@/components/dashboard/ProgressChart'
import { ActivityHeatmap } from '@/components/dashboard/ActivityHeatmap'
import { TopicMastery } from '@/components/dashboard/TopicMastery'
import { StreakCounter } from '@/components/dashboard/StreakCounter'
import { RecommendedTopics } from '@/components/dashboard/RecommendedTopics'
import { RecentActivity } from '@/components/dashboard/RecentActivity'
import { CompanyReadiness } from '@/components/dashboard/CompanyReadiness'
import {
  AcademicCapIcon,
  ChartBarIcon,
  ClockIcon,
  FireIcon,
} from '@heroicons/react/24/outline'

export default function DashboardPage() {
  const router = useRouter()
  const { user, isAuthenticated } = useAuth()
  const {
    summary,
    trends,
    topicMastery,
    streakInfo,
    recommendations,
    recentActivity,
    companyReadiness,
    isLoading,
    fetchDashboardData,
  } = useAnalytics()

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login')
    } else {
      fetchDashboardData()
    }
  }, [isAuthenticated, router, fetchDashboardData])

  if (!user) {
    return null
  }

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Welcome back, {user.displayName || 'User'}!
          </h1>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Here's your progress overview
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <span className="text-sm text-gray-500">
            Last active: {new Date().toLocaleDateString()}
          </span>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard
          title="Overall Accuracy"
          value={`${summary?.overallAccuracy || 0}%`}
          icon={<ChartBarIcon className="h-6 w-6" />}
          trend={{ value: 5, label: 'vs last week', positive: true }}
          color="primary"
          isLoading={isLoading}
        />
        <StatsCard
          title="Questions Solved"
          value={summary?.totalQuestions || 0}
          icon={<AcademicCapIcon className="h-6 w-6" />}
          trend={{ value: 12, label: 'this week', positive: true }}
          color="success"
          isLoading={isLoading}
        />
        <StatsCard
          title="Practice Time"
          value={`${Math.floor((summary?.totalPracticeTime || 0) / 60)}h`}
          icon={<ClockIcon className="h-6 w-6" />}
          description="Total time spent"
          color="warning"
          isLoading={isLoading}
        />
        <StatsCard
          title="Current Streak"
          value={`${streakInfo?.currentStreak || 0} days`}
          icon={<FireIcon className="h-6 w-6" />}
          description={`Best: ${streakInfo?.longestStreak || 0} days`}
          color="error"
          isLoading={isLoading}
        />
      </div>

      {/* Rest of your component remains same */}
    </div>
  )
}
