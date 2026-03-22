'use client'

import { useEffect, useState } from 'react'
import { useAuth } from '@/hooks/useAuth'
import { useAnalytics } from '@/hooks/useAnalytics'
import { useRouter } from 'next/navigation'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card/Card'
import { ProgressChart } from '@/components/dashboard/ProgressChart'
import { TopicMastery } from '@/components/dashboard/TopicMastery'
import { CompanyReadiness } from '@/components/dashboard/CompanyReadiness'
import { Button } from '@/components/ui/button/Button'
import { Select } from '@/components/ui/select/Select'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs/Tabs'
import {
  ArrowDownTrayIcon,
  ChartBarIcon,
  ClockIcon,
  AcademicCapIcon,
} from '@heroicons/react/24/outline'

export default function AnalyticsPage() {
  const router = useRouter()
  const { isAuthenticated, user } = useAuth()
  const {
    summary,
    trends,
    subjectPerformance,
    topicMastery,
    companyReadiness,
    difficultyPerformance,
    questionTypePerformance,
    timeAnalysis,
    isLoading,
    fetchAnalyticsSummary,
    fetchPerformanceTrends,
    fetchSubjectPerformance,
    fetchTopicMastery,
    fetchCompanyReadiness,
    fetchDifficultyPerformance,
    fetchQuestionTypePerformance,
    fetchTimeAnalysis,
    exportAnalytics,
  } = useAnalytics()

  const [timeframe, setTimeframe] = useState('30')
  const [selectedSubject, setSelectedSubject] = useState<string>('all')

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login')
    } else {
      loadAnalytics()
    }
  }, [isAuthenticated, router, timeframe])

  const loadAnalytics = async () => {
    const isPro = user?.role === 'pro' || user?.role === 'premium' || user?.role === 'admin'
    await Promise.allSettled([
      fetchAnalyticsSummary(),
      fetchPerformanceTrends(parseInt(timeframe)),
      fetchSubjectPerformance(),
      fetchTopicMastery(),
      isPro ? fetchCompanyReadiness() : Promise.resolve(),
      fetchDifficultyPerformance(),
      fetchQuestionTypePerformance(),
      fetchTimeAnalysis(),
    ])
  }

  const handleExport = async (format: string) => {
    await exportAnalytics(format, timeframe)
  }

  const subjectOptions = [
    { value: 'all', label: 'All Subjects' },
    { value: 'ml', label: 'Machine Learning' },
    { value: 'dl', label: 'Deep Learning' },
    { value: 'ds', label: 'Data Science' },
    { value: 'da', label: 'Data Analysis' },
    { value: 'ai', label: 'Artificial Intelligence' },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Analytics</h1>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Track your performance and progress over time
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <Select
            value={timeframe}
            onChange={(e) => setTimeframe(e.target.value)}
            className="w-40"
          >
            <option value="7">Last 7 days</option>
            <option value="14">Last 14 days</option>
            <option value="30">Last 30 days</option>
            <option value="90">Last 90 days</option>
          </Select>
          <Button variant="outline" onClick={() => handleExport('pdf')}>
            <ArrowDownTrayIcon className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600 dark:text-gray-400">Overall Accuracy</span>
              <ChartBarIcon className="h-5 w-5 text-primary-500" />
            </div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white">
              {summary?.overallAccuracy || 0}%
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600 dark:text-gray-400">Total Questions</span>
              <AcademicCapIcon className="h-5 w-5 text-success-500" />
            </div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white">
              {summary?.totalQuestions || 0}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600 dark:text-gray-400">Current Streak</span>
              <ClockIcon className="h-5 w-5 text-warning-500" />
            </div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white">
              {summary?.currentStreak || 0} days
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600 dark:text-gray-400">Practice Time</span>
              <ClockIcon className="h-5 w-5 text-info-500" />
            </div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white">
              {Math.floor((summary?.totalPracticeTime || 0) / 60)}h
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Progress Chart */}
      <ProgressChart
        data={trends || { dates: [], accuracy: [], volume: [], timeSpent: [] }}
        isLoading={isLoading}
        onTimeframeChange={setTimeframe}
        timeframe={timeframe}
      />

      {/* Performance Tabs */}
      <Tabs defaultValue="subjects">
        <TabsList>
          <TabsTrigger value="subjects">Subject Performance</TabsTrigger>
          <TabsTrigger value="topics">Topic Mastery</TabsTrigger>
          <TabsTrigger value="difficulty">By Difficulty</TabsTrigger>
          <TabsTrigger value="types">Question Types</TabsTrigger>
          <TabsTrigger value="time">Time Analysis</TabsTrigger>
        </TabsList>

        <TabsContent value="subjects">
          <Card>
            <CardHeader>
              <CardTitle>Performance by Subject</CardTitle>
              <CardDescription>
                Your accuracy across different subjects
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {subjectPerformance && Object.entries(subjectPerformance).map(([subject, data]: [string, any]) => (
                  <div key={subject} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-medium capitalize">{subject}</span>
                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        {data.accuracy}% • {data.total} questions
                      </span>
                    </div>
                    <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-primary-500"
                        style={{ width: `${data.accuracy}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="topics">
          <TopicMastery
            data={topicMastery || { masteredTopics: [], inProgressTopics: [], notStartedTopics: [] }}
            isLoading={isLoading}
          />
        </TabsContent>

        <TabsContent value="difficulty">
          <Card>
            <CardHeader>
              <CardTitle>Performance by Difficulty</CardTitle>
              <CardDescription>
                How you perform on different difficulty levels
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {difficultyPerformance && Object.entries(difficultyPerformance).map(([difficulty, data]: [string, any]) => (
                  <div key={difficulty} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-medium capitalize">{difficulty}</span>
                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        {data.accuracy}% • {data.total} questions
                      </span>
                    </div>
                    <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                      <div
                        className={`h-full ${
                          difficulty === 'easy' ? 'bg-success-500' :
                          difficulty === 'medium' ? 'bg-primary-500' :
                          difficulty === 'hard' ? 'bg-warning-500' : 'bg-error-500'
                        }`}
                        style={{ width: `${data.accuracy}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="types">
          <Card>
            <CardHeader>
              <CardTitle>Performance by Question Type</CardTitle>
              <CardDescription>
                Your accuracy on different question formats
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {questionTypePerformance && Object.entries(questionTypePerformance).map(([type, data]: [string, any]) => (
                  <div key={type} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-medium capitalize">{type.replace('_', ' ')}</span>
                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        {data.accuracy}% • {data.total} questions
                      </span>
                    </div>
                    <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-primary-500"
                        style={{ width: `${data.accuracy}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="time">
          <Card>
            <CardHeader>
              <CardTitle>Time Analysis</CardTitle>
              <CardDescription>
                How you spend your practice time
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <h3 className="font-medium">Average Time per Question</h3>
                  <div className="text-3xl font-bold text-gray-900 dark:text-white">
                    {timeAnalysis?.averageTime || 0}s
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Fastest</span>
                      <span>{timeAnalysis?.fastestTime || 0}s</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Slowest</span>
                      <span>{timeAnalysis?.slowestTime || 0}s</span>
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <h3 className="font-medium">Time by Difficulty</h3>
                  {timeAnalysis?.byDifficulty && Object.entries(timeAnalysis.byDifficulty).map(([difficulty, data]: [string, any]) => (
                    <div key={difficulty} className="flex justify-between text-sm">
                      <span className="capitalize">{difficulty}</span>
                      <span>{data.averageTime}s avg</span>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Company Readiness */}
      {companyReadiness && companyReadiness.length > 0 && (
        <CompanyReadiness
          companies={companyReadiness}
          isLoading={isLoading}
          onCompanyClick={(company) => router.push(`/practice/company-grid/${company}`)}
        />
      )}
    </div>
  )
}
