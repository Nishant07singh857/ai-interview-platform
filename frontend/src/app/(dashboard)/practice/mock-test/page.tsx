'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card/Card'
import { Button } from '@/components/ui/button/Button'
import { Select } from '@/components/ui/select/Select'
import { Input } from '@/components/ui/input/Input'
import { Badge } from '@/components/ui/badge/Badge'
import { usePractice } from '@/hooks/usePractice'
import { useAuth } from '@/hooks/useAuth'
import {
  ClockIcon,
  DocumentTextIcon,
  ChartBarIcon,
  LockClosedIcon,
} from '@heroicons/react/24/outline'

const mockTests = [
  {
    id: 'ml-fundamentals',
    title: 'ML Fundamentals',
    description: 'Test your knowledge of core machine learning concepts',
    subject: 'Machine Learning',
    duration: 30,
    questions: 30,
    difficulty: 'Medium',
    popularity: 1240,
  },
  {
    id: 'deep-learning',
    title: 'Deep Learning Specialization',
    description: 'Comprehensive test on neural networks and deep learning',
    subject: 'Deep Learning',
    duration: 45,
    questions: 40,
    difficulty: 'Hard',
    popularity: 890,
    pro: true,
  },
  {
    id: 'data-science',
    title: 'Data Science Complete',
    description: 'Full-stack data science assessment',
    subject: 'Data Science',
    duration: 60,
    questions: 50,
    difficulty: 'Hard',
    popularity: 1560,
    pro: true,
  },
  {
    id: 'sql-mastery',
    title: 'SQL Mastery',
    description: 'Advanced SQL queries and optimization',
    subject: 'Data Analysis',
    duration: 25,
    questions: 25,
    difficulty: 'Medium',
    popularity: 2100,
  },
  {
    id: 'system-design',
    title: 'System Design Interview',
    description: 'Practice system design questions for tech interviews',
    subject: 'System Design',
    duration: 60,
    questions: 5,
    difficulty: 'Expert',
    popularity: 750,
    pro: true,
  },
  {
    id: 'python-coding',
    title: 'Python Coding Challenge',
    description: 'Test your Python programming skills',
    subject: 'Programming',
    duration: 40,
    questions: 20,
    difficulty: 'Medium',
    popularity: 1800,
  },
]

export default function MockTestPage() {
  const router = useRouter()
  const { user } = useAuth()
  const { startMockTest, isLoading } = usePractice()
  const [selectedTest, setSelectedTest] = useState<any>(null)
  const [customConfig, setCustomConfig] = useState({
    subject: 'Machine Learning',
    totalQuestions: 30,
    timeLimit: 30,
  })

  const handleStartTest = async () => {
    if (!selectedTest) return

    try {
      const session = await startMockTest({
        subject: selectedTest.subject,
        title: selectedTest.title,
        totalQuestions: selectedTest.questions,
        timeLimit: selectedTest.duration,
      })
      if (session?.sessionId) {
        router.push(`/practice/session/${session.sessionId}`)
      }
    } catch (error) {
      console.error('Failed to start test:', error)
    }
  }

  const handleStartCustom = async () => {
    try {
      const session = await startMockTest(customConfig)
      if (session?.sessionId) {
        router.push(`/practice/session/${session.sessionId}`)
      }
    } catch (error) {
      console.error('Failed to start custom test:', error)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Mock Tests</h1>
        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
          Full-length tests simulating real interview conditions
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Predefined Tests */}
        <div className="lg:col-span-2 space-y-4">
          <h2 className="text-lg font-semibold">Recommended Tests</h2>
          <div className="grid grid-cols-1 gap-4">
            {mockTests.map((test, index) => (
              <motion.div
                key={test.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <Card
                  className={`cursor-pointer transition-all ${
                    selectedTest?.id === test.id
                      ? 'ring-2 ring-primary-500'
                      : 'hover:shadow-md'
                  }`}
                  onClick={() => setSelectedTest(test)}
                >
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                            {test.title}
                          </h3>
                          {test.pro && !user?.subscriptionPlan && (
                            <Badge variant="primary" size="sm">PRO</Badge>
                          )}
                          <Badge
                            variant={
                              test.difficulty === 'Easy' ? 'success' :
                              test.difficulty === 'Medium' ? 'warning' :
                              test.difficulty === 'Hard' ? 'error' : 'primary'
                            }
                            size="sm"
                          >
                            {test.difficulty}
                          </Badge>
                        </div>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                          {test.description}
                        </p>
                        <div className="flex items-center space-x-6 text-sm text-gray-500">
                          <span className="flex items-center">
                            <DocumentTextIcon className="h-4 w-4 mr-1" />
                            {test.questions} questions
                          </span>
                          <span className="flex items-center">
                            <ClockIcon className="h-4 w-4 mr-1" />
                            {test.duration} minutes
                          </span>
                          <span className="flex items-center">
                            <ChartBarIcon className="h-4 w-4 mr-1" />
                            {test.popularity.toLocaleString()} taken
                          </span>
                        </div>
                      </div>
                      {test.pro && !user?.subscriptionPlan && (
                        <LockClosedIcon className="h-5 w-5 text-gray-400 ml-4" />
                      )}
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Selected Test */}
          {selectedTest && (
            <Card>
              <CardHeader>
                <CardTitle>Start Test</CardTitle>
                <CardDescription>
                  {selectedTest.title}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Questions</span>
                    <span className="font-medium">{selectedTest.questions}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Time Limit</span>
                    <span className="font-medium">{selectedTest.duration} minutes</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Difficulty</span>
                    <Badge
                      variant={
                        selectedTest.difficulty === 'Easy' ? 'success' :
                        selectedTest.difficulty === 'Medium' ? 'warning' :
                        selectedTest.difficulty === 'Hard' ? 'error' : 'primary'
                      }
                      size="sm"
                    >
                      {selectedTest.difficulty}
                    </Badge>
                  </div>
                </div>

                {selectedTest.pro && !user?.subscriptionPlan ? (
                  <Button
                    variant="primary"
                    className="w-full"
                    onClick={() => router.push('/pricing')}
                  >
                    Upgrade to Pro
                  </Button>
                ) : (
                  <Button
                    onClick={handleStartTest}
                    disabled={isLoading}
                    className="w-full"
                  >
                    Start Test
                  </Button>
                )}
              </CardContent>
            </Card>
          )}

          {/* Custom Test */}
          <Card>
            <CardHeader>
              <CardTitle>Custom Test</CardTitle>
              <CardDescription>
                Create your own mock test
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Subject</label>
                <Select
                  value={customConfig.subject}
                  onChange={(e) => setCustomConfig({ ...customConfig, subject: e.target.value })}
                >
                  <option value="Machine Learning">Machine Learning</option>
                  <option value="Deep Learning">Deep Learning</option>
                  <option value="Data Science">Data Science</option>
                  <option value="Data Analysis">Data Analysis</option>
                  <option value="Artificial Intelligence">Artificial Intelligence</option>
                </Select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Number of Questions</label>
                <Input
                  type="number"
                  min="10"
                  max="100"
                  value={customConfig.totalQuestions}
                  onChange={(e) => setCustomConfig({
                    ...customConfig,
                    totalQuestions: parseInt(e.target.value)
                  })}
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Time Limit (minutes)</label>
                <Input
                  type="number"
                  min="15"
                  max="180"
                  value={customConfig.timeLimit}
                  onChange={(e) => setCustomConfig({
                    ...customConfig,
                    timeLimit: parseInt(e.target.value)
                  })}
                />
              </div>

              <Button
                onClick={handleStartCustom}
                disabled={isLoading}
                variant="outline"
                className="w-full"
              >
                Create Custom Test
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
