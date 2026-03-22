'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card/Card'
import { Button } from '@/components/ui/button/Button'
import { Badge } from '@/components/ui/badge/Badge'
import { Progress } from '@/components/ui/progress/Progress'
import { usePractice } from '@/hooks/usePractice'
import { motion } from 'framer-motion'
import {
  CheckCircleIcon,
  XCircleIcon,
  ChartBarIcon,
  ArrowPathIcon,
  ShareIcon,
} from '@heroicons/react/24/outline'

export default function PracticeResultsPage() {
  const params = useParams()
  const router = useRouter()
  const sessionId = params.sessionId as string
  const { loadResults, isLoading } = usePractice()
  const [results, setResults] = useState<any>(null)

  useEffect(() => {
    loadResults(sessionId).then(setResults)
  }, [sessionId, loadResults])

  if (isLoading || !results) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <ArrowPathIcon className="h-8 w-8 animate-spin text-primary-500" />
      </div>
    )
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'success'
    if (score >= 60) return 'primary'
    if (score >= 40) return 'warning'
    return 'error'
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="max-w-4xl mx-auto space-y-6"
    >
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Practice Session Complete!
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Here's how you performed
        </p>
      </div>

      {/* Score Card */}
      <Card className="bg-gradient-to-r from-primary-500 to-primary-600 text-white">
        <CardContent className="p-8">
          <div className="text-center">
            <div className="text-6xl font-bold mb-2">{results.score}%</div>
            <p className="text-primary-100">Overall Score</p>
            <Progress
              value={results.score}
              variant="default"
              className="mt-6 bg-white/20"
            />
          </div>
        </CardContent>
      </Card>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-gray-900 dark:text-white">
              {results.correctAnswers}
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400">Correct</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-gray-900 dark:text-white">
              {results.incorrectAnswers}
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400">Incorrect</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-gray-900 dark:text-white">
              {results.skippedQuestions}
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400">Skipped</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-gray-900 dark:text-white">
              {Math.floor(results.totalTimeSpent / 60)}m
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400">Time Spent</p>
          </CardContent>
        </Card>
      </div>

      {/* Subject Performance */}
      <Card>
        <CardHeader>
          <CardTitle>Performance by Subject</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {Object.entries(results.subjectWise || {}).map(([subject, data]: [string, any]) => (
            <div key={subject} className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-medium capitalize">{subject}</span>
                <Badge variant={getScoreColor(data.accuracy)}>
                  {data.accuracy}%
                </Badge>
              </div>
              <Progress value={data.accuracy} variant={getScoreColor(data.accuracy)} />
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Strengths & Weaknesses */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <CheckCircleIcon className="h-5 w-5 text-success-500 mr-2" />
              Strengths
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {results.strengths.map((strength: string, index: number) => (
                <li key={index} className="flex items-start space-x-2">
                  <span className="text-success-500 mt-0.5">✓</span>
                  <span className="text-sm text-gray-700 dark:text-gray-300">{strength}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <XCircleIcon className="h-5 w-5 text-warning-500 mr-2" />
              Areas to Improve
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {results.weaknesses.map((weakness: string, index: number) => (
                <li key={index} className="flex items-start space-x-2">
                  <span className="text-warning-500 mt-0.5">•</span>
                  <span className="text-sm text-gray-700 dark:text-gray-300">{weakness}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      </div>

      {/* Recommendations */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <ChartBarIcon className="h-5 w-5 text-primary-500 mr-2" />
            Recommendations
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-3">
            {results.recommendations.map((rec: string, index: number) => (
              <li key={index} className="flex items-start space-x-3">
                <span className="text-primary-500 font-medium">{index + 1}.</span>
                <span className="text-sm text-gray-700 dark:text-gray-300">{rec}</span>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>

      {/* Action Buttons */}
      <div className="flex items-center justify-center space-x-4 pt-6">
        <Button
          variant="outline"
          onClick={() => router.push('/practice')}
        >
          Practice More
        </Button>
        <Button
          onClick={() => {/* Share results */}}
        >
          <ShareIcon className="h-4 w-4 mr-2" />
          Share Results
        </Button>
      </div>
    </motion.div>
  )
}
