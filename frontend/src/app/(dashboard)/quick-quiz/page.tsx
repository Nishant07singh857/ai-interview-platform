'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card/Card'
import { Button } from '@/components/ui/button/Button'
import { Select } from '@/components/ui/select/Select'
import { usePractice } from '@/hooks/usePractice'
import { motion } from 'framer-motion'

const subjects = [
  { value: 'all', label: 'All Subjects' },
  { value: 'ml', label: 'Machine Learning' },
  { value: 'dl', label: 'Deep Learning' },
  { value: 'ds', label: 'Data Science' },
  { value: 'da', label: 'Data Analysis' },
  { value: 'ai', label: 'Artificial Intelligence' },
]

const difficulties = [
  { value: 'all', label: 'All Difficulties' },
  { value: 'easy', label: 'Easy' },
  { value: 'medium', label: 'Medium' },
  { value: 'hard', label: 'Hard' },
]

export default function QuickQuizSetupPage() {
  const router = useRouter()
  const { startQuickQuiz, isLoading } = usePractice()
  const [config, setConfig] = useState({
    totalQuestions: 5,
    timeLimit: 5,
    subjects: [] as string[],
    difficulties: [] as string[],
  })

  const handleStart = async () => {
    try {
      const session = await startQuickQuiz(config)
      router.push(`/practice/session/${session.sessionId}`)
    } catch (error) {
      console.error('Failed to start quiz:', error)
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="max-w-2xl mx-auto"
    >
      <Card>
        <CardHeader>
          <CardTitle>Quick Quiz Setup</CardTitle>
          <CardDescription>
            Configure your quick quiz session
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-6">
          {/* Question Count */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Number of Questions</label>
            <div className="flex items-center space-x-4">
              {[5, 10, 15, 20].map((num) => (
                <button
                  key={num}
                  onClick={() => setConfig({ ...config, totalQuestions: num })}
                  className={`flex-1 py-2 px-4 rounded-lg border-2 transition-all ${
                    config.totalQuestions === num
                      ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                      : 'border-gray-200 dark:border-gray-700 hover:border-primary-300'
                  }`}
                >
                  <span className="font-medium">{num}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Time Limit */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Time Limit (minutes)</label>
            <div className="flex items-center space-x-4">
              {[5, 10, 15, 30].map((time) => (
                <button
                  key={time}
                  onClick={() => setConfig({ ...config, timeLimit: time })}
                  className={`flex-1 py-2 px-4 rounded-lg border-2 transition-all ${
                    config.timeLimit === time
                      ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                      : 'border-gray-200 dark:border-gray-700 hover:border-primary-300'
                  }`}
                >
                  <span className="font-medium">{time}m</span>
                </button>
              ))}
            </div>
          </div>

          {/* Subjects */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Subjects (optional)</label>
            <Select
              multiple
              value={config.subjects}
              onChange={(e) => setConfig({
                ...config,
                subjects: Array.from(e.target.selectedOptions, opt => opt.value)
              })}
              className="h-32"
            >
              {subjects.map(subject => (
                <option key={subject.value} value={subject.value}>
                  {subject.label}
                </option>
              ))}
            </Select>
          </div>

          {/* Difficulties */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Difficulties (optional)</label>
            <Select
              multiple
              value={config.difficulties}
              onChange={(e) => setConfig({
                ...config,
                difficulties: Array.from(e.target.selectedOptions, opt => opt.value)
              })}
              className="h-24"
            >
              {difficulties.map(diff => (
                <option key={diff.value} value={diff.value}>
                  {diff.label}
                </option>
              ))}
            </Select>
          </div>
        </CardContent>

        <CardFooter>
          <Button
            onClick={handleStart}
            disabled={isLoading}
            className="w-full"
            size="lg"
          >
            {isLoading ? 'Starting...' : 'Start Quick Quiz'}
          </Button>
        </CardFooter>
      </Card>
    </motion.div>
  )
}