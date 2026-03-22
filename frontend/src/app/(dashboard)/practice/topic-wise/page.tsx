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
import { MagnifyingGlassIcon } from '@heroicons/react/24/outline'

const subjects = [
  {
    name: 'Machine Learning',
    suggestedTopics: [
      'Linear Regression',
      'Logistic Regression',
      'Decision Trees',
      'Random Forest',
      'SVM',
      'Neural Networks',
    ],
  },
  {
    name: 'Deep Learning',
    suggestedTopics: [
      'CNNs',
      'RNNs',
      'LSTMs',
      'Transformers',
      'BERT',
      'GANs',
    ],
  },
  {
    name: 'Data Science',
    suggestedTopics: [
      'Data Cleaning',
      'Feature Engineering',
      'EDA',
      'Statistics',
      'Data Visualization',
    ],
  },
  {
    name: 'Python',
    suggestedTopics: [
      'Functions',
      'Classes',
      'Decorators',
      'Generators',
      'File I/O',
    ],
  },
  {
    name: 'SQL',
    suggestedTopics: [
      'SELECT',
      'JOINs',
      'GROUP BY',
      'Subqueries',
      'Indexes',
    ],
  },
]

export default function TopicWisePage() {
  const router = useRouter()
  const { startTopicPractice, isLoading } = usePractice()
  const [selectedSubject, setSelectedSubject] = useState<string>('Machine Learning')
  const [customTopic, setCustomTopic] = useState('')
  const [questionCount, setQuestionCount] = useState(10)
  const [error, setError] = useState('')

  const currentSubject = subjects.find(s => s.name === selectedSubject)

  const handleStartPractice = async () => {
    setError('')

    if (!customTopic.trim()) {
      setError('Please enter a topic name')
      return
    }

    try {
      const session = await startTopicPractice({
        subject: selectedSubject,
        topic: customTopic.trim(),
        totalQuestions: questionCount,
      })
      router.push(`/practice/session/${session.sessionId}`)
    } catch (error: any) {
      setError(error.message || 'Failed to start practice')
    }
  }

  const handleSuggestedTopic = (topic: string) => {
    setCustomTopic(topic)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Topic Wise Practice</h1>
        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
          Enter any topic and start practicing
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Filters */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle>Practice Configuration</CardTitle>
              <CardDescription>
                Set your practice parameters
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {error && (
                <div className="p-3 bg-red-100 text-red-700 rounded text-sm">
                  {error}
                </div>
              )}

              <div className="space-y-2">
                <label className="text-sm font-medium">Subject</label>
                <Select
                  value={selectedSubject}
                  onChange={(e) => {
                    setSelectedSubject(e.target.value)
                    setCustomTopic('')
                    setError('')
                  }}
                >
                  {subjects.map((subject) => (
                    <option key={subject.name} value={subject.name}>
                      {subject.name}
                    </option>
                  ))}
                </Select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">
                  Topic <span className="text-red-500">*</span>
                </label>
                <Input
                  type="text"
                  value={customTopic}
                  onChange={(e) => setCustomTopic(e.target.value)}
                  placeholder="e.g., Linear Regression, Python Functions..."
                  className="w-full"
                />
                <p className="text-xs text-gray-500">
                  You can enter any topic name - questions will be generated automatically
                </p>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Number of Questions</label>
                <Select
                  value={questionCount}
                  onChange={(e) => setQuestionCount(Number(e.target.value))}
                >
                  {[5, 10, 15, 20, 25, 30].map((num) => (
                    <option key={num} value={num}>
                      {num} questions
                    </option>
                  ))}
                </Select>
              </div>

              <div className="pt-4">
                <Button
                  onClick={handleStartPractice}
                  disabled={isLoading || !customTopic.trim()}
                  className="w-full"
                >
                  {isLoading ? 'Starting...' : 'Start Practice'}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Suggested Topics */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Suggested Topics</CardTitle>
                  <CardDescription>
                    Click any topic to auto-fill or type your own
                  </CardDescription>
                </div>
                <div className="relative">
                  <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    type="text"
                    placeholder="Search topics..."
                    value={customTopic}
                    onChange={(e) => setCustomTopic(e.target.value)}
                    className="pl-9 w-64"
                  />
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {currentSubject?.suggestedTopics.map((topic) => (
                  <motion.button
                    key={topic}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => handleSuggestedTopic(topic)}
                    className={`p-4 rounded-lg border-2 text-left transition-all ${
                      customTopic === topic
                        ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                        : 'border-gray-200 dark:border-gray-700 hover:border-primary-300'
                    }`}
                  >
                    <h3 className={`font-medium ${
                      customTopic === topic
                        ? 'text-primary-700 dark:text-primary-300'
                        : 'text-gray-900 dark:text-white'
                    }`}>
                      {topic}
                    </h3>
                    <p className="text-xs text-gray-500 mt-1">
                      Click to use this topic
                    </p>
                  </motion.button>
                ))}
              </div>

              <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <h3 className="text-sm font-medium text-blue-800 dark:text-blue-300 mb-2">
                  ✨ Manual Topic Entry
                </h3>
                <p className="text-xs text-blue-600 dark:text-blue-400">
                  You can type ANY topic in the field above. Questions will be generated on-the-fly.
                  <br />
                  <span className="font-medium">Examples:</span> Linear Regression, Python Functions, 
                  SQL JOINs, CNN Architecture, etc.
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}