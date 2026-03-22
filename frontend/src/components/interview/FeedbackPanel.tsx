'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Card } from '@/components/ui/card/Card'
import { Button } from '@/components/ui/button/Button'
import { Badge } from '@/components/ui/badge/Badge'
import { Progress } from '@/components/ui/progress/Progress'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs/Tabs'
import {
  CheckCircleIcon,
  XCircleIcon,
  ChartBarIcon,
  LightBulbIcon,
  AcademicCapIcon,
  ArrowPathIcon,
} from '@heroicons/react/24/outline'

interface FeedbackPanelProps {
  questionId: string
  sessionId: string
  onContinue: () => void
}

export const FeedbackPanel = ({ questionId, sessionId, onContinue }: FeedbackPanelProps) => {
  const [isLoading, setIsLoading] = useState(true)
  const [feedback, setFeedback] = useState<any>(null)

  useEffect(() => {
    // Simulate fetching feedback
    setTimeout(() => {
      setFeedback({
        score: 85,
        technical_score: 90,
        communication_score: 80,
        clarity_score: 85,
        confidence_score: 85,
        strengths: [
          "Clear explanation of core concepts",
          "Good use of technical terminology",
          "Structured response with examples",
        ],
        improvements: [
          "Could provide more specific examples",
          "Consider discussing edge cases",
          "Work on reducing filler words",
        ],
        key_points_covered: [
          "Understanding of neural networks",
          "Backpropagation explanation",
          "Activation functions discussion",
        ],
        missing_points: [
          "Gradient vanishing problem",
          "Comparison with other architectures",
        ],
        voice_analysis: {
          speaking_rate: "Good (120 wpm)",
          clarity: "Excellent",
          filler_words: 3,
          confidence: "High",
        },
      })
      setIsLoading(false)
    }, 2000)
  }, [questionId, sessionId])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <ArrowPathIcon className="h-8 w-8 animate-spin text-primary-500 mx-auto mb-3" />
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Analyzing your response...
          </p>
        </div>
      </div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-4"
    >
      {/* Overall Score */}
      <Card className="bg-gradient-to-r from-primary-500 to-primary-600 text-white">
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Response Analysis</h3>
            <Badge variant="secondary" className="bg-white/20 text-white border-white/30">
              Overall Score
            </Badge>
          </div>
          <div className="flex items-end space-x-4">
            <div className="text-5xl font-bold">{feedback.score}</div>
            <div className="text-xl opacity-90">/100</div>
          </div>
          <Progress value={feedback.score} variant="default" className="mt-4 bg-white/20" />
        </div>
      </Card>

      {/* Detailed Scores */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <div className="p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600 dark:text-gray-400">Technical</span>
              <AcademicCapIcon className="h-4 w-4 text-primary-500" />
            </div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white">
              {feedback.technical_score}%
            </div>
          </div>
        </Card>
        <Card>
          <div className="p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600 dark:text-gray-400">Communication</span>
              <ChartBarIcon className="h-4 w-4 text-primary-500" />
            </div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white">
              {feedback.communication_score}%
            </div>
          </div>
        </Card>
        <Card>
          <div className="p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600 dark:text-gray-400">Clarity</span>
              <LightBulbIcon className="h-4 w-4 text-primary-500" />
            </div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white">
              {feedback.clarity_score}%
            </div>
          </div>
        </Card>
      </div>

      {/* Detailed Feedback Tabs */}
      <Tabs defaultValue="strengths">
        <TabsList>
          <TabsTrigger value="strengths">Strengths</TabsTrigger>
          <TabsTrigger value="improvements">Improvements</TabsTrigger>
          <TabsTrigger value="coverage">Coverage</TabsTrigger>
          <TabsTrigger value="voice">Voice Analysis</TabsTrigger>
        </TabsList>

        <TabsContent value="strengths" className="space-y-2">
          {feedback.strengths.map((strength: string, index: number) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="flex items-start space-x-2 p-3 bg-success-50 dark:bg-success-900/20 rounded-lg"
            >
              <CheckCircleIcon className="h-5 w-5 text-success-500 flex-shrink-0 mt-0.5" />
              <span className="text-sm text-gray-700 dark:text-gray-300">{strength}</span>
            </motion.div>
          ))}
        </TabsContent>

        <TabsContent value="improvements" className="space-y-2">
          {feedback.improvements.map((improvement: string, index: number) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="flex items-start space-x-2 p-3 bg-warning-50 dark:bg-warning-900/20 rounded-lg"
            >
              <XCircleIcon className="h-5 w-5 text-warning-500 flex-shrink-0 mt-0.5" />
              <span className="text-sm text-gray-700 dark:text-gray-300">{improvement}</span>
            </motion.div>
          ))}
        </TabsContent>

        <TabsContent value="coverage" className="space-y-4">
          <div>
            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Key Points Covered
            </h4>
            <ul className="space-y-1">
              {feedback.key_points_covered.map((point: string, index: number) => (
                <li key={index} className="flex items-center space-x-2 text-sm text-gray-600">
                  <CheckCircleIcon className="h-4 w-4 text-success-500" />
                  <span>{point}</span>
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Missing Points
            </h4>
            <ul className="space-y-1">
              {feedback.missing_points.map((point: string, index: number) => (
                <li key={index} className="flex items-center space-x-2 text-sm text-gray-600">
                  <XCircleIcon className="h-4 w-4 text-warning-500" />
                  <span>{point}</span>
                </li>
              ))}
            </ul>
          </div>
        </TabsContent>

        <TabsContent value="voice" className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <div className="p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
              <p className="text-xs text-gray-500 mb-1">Speaking Rate</p>
              <p className="text-sm font-medium">{feedback.voice_analysis.speaking_rate}</p>
            </div>
            <div className="p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
              <p className="text-xs text-gray-500 mb-1">Clarity</p>
              <p className="text-sm font-medium">{feedback.voice_analysis.clarity}</p>
            </div>
            <div className="p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
              <p className="text-xs text-gray-500 mb-1">Filler Words</p>
              <p className="text-sm font-medium">{feedback.voice_analysis.filler_words}</p>
            </div>
            <div className="p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
              <p className="text-xs text-gray-500 mb-1">Confidence</p>
              <p className="text-sm font-medium">{feedback.voice_analysis.confidence}</p>
            </div>
          </div>
        </TabsContent>
      </Tabs>

      {/* Continue Button */}
      <Button onClick={onContinue} className="w-full">
        Continue to Next Question
      </Button>
    </motion.div>
  )
}
