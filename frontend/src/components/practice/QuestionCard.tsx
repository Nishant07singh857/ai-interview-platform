'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/card/Card'
import { Button } from '@/components/ui/button/Button'
import { Badge } from '@/components/ui/badge/Badge'
import { Timer } from './Timer'
import { DifficultyBadge } from './DifficultyBadge'
import { BookmarkButton } from './BookmarkButton'
import { HintSystem } from './HintSystem'
import {
  LightBulbIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  FlagIcon,
} from '@heroicons/react/24/outline'
import type { Question } from '@/types'

interface QuestionCardProps {
  question: Question
  totalQuestions: number
  currentIndex: number
  timeLimit?: number
  onAnswer: (answer: any) => Promise<any> | any
  onNext: () => void
  onPrevious: () => void
  onSkip: () => void
  onBookmark?: () => void
  isBookmarked?: boolean
  showExplanation?: boolean
  isLoading?: boolean
}

export const QuestionCard = ({
  question,
  totalQuestions,
  currentIndex,
  timeLimit,
  onAnswer,
  onNext,
  onPrevious,
  onSkip,
  onBookmark,
  isBookmarked = false,
  showExplanation = false,
  isLoading = false,
}: QuestionCardProps) => {
  const [selectedAnswer, setSelectedAnswer] = useState<any>(null)
  const [showHint, setShowHint] = useState(false)
  const [isSubmitted, setIsSubmitted] = useState(false)
  const [isCorrect, setIsCorrect] = useState<boolean | null>(null)
  const [showResult, setShowResult] = useState(false)

  const handleAnswerSelect = (answer: any) => {
    if (!isSubmitted) {
      setSelectedAnswer(answer)
    }
  }

  const handleSubmit = async () => {
    if (!selectedAnswer) return

    setIsSubmitted(true)

    try {
      const result = await onAnswer(selectedAnswer)
      const correct =
        typeof result?.isCorrect === 'boolean'
          ? result.isCorrect
          : typeof result?.is_correct === 'boolean'
          ? result.is_correct
          : null
      setIsCorrect(correct)
      setShowResult(true)
    } catch (error) {
      setIsCorrect(null)
      setIsSubmitted(false)
      setShowResult(false)
    }
  }

  const handleNext = () => {
    setSelectedAnswer(null)
    setIsSubmitted(false)
    setIsCorrect(null)
    setShowResult(false)
    setShowHint(false)
    onNext()
  }

  const renderQuestionContent = () => {
    switch (question.type) {
      case 'mcq':
        return (
          <div className="space-y-3">
            {question.options?.map((option) => (
              <button
                key={option.id}
                onClick={() => handleAnswerSelect(option.id)}
                className={`w-full p-4 text-left rounded-lg border-2 transition-all ${
                  selectedAnswer === option.id
                    ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                    : 'border-gray-200 dark:border-gray-700 hover:border-primary-300 dark:hover:border-primary-600'
                } ${
                  isSubmitted && option.isCorrect
                    ? 'border-success-500 bg-success-50 dark:bg-success-900/20'
                    : isSubmitted && selectedAnswer === option.id && !option.isCorrect
                    ? 'border-error-500 bg-error-50 dark:bg-error-900/20'
                    : ''
                }`}
                disabled={isSubmitted}
              >
                <div className="flex items-center">
                  <span className="w-8 h-8 flex items-center justify-center rounded-full bg-gray-100 dark:bg-gray-800 font-medium mr-3">
                    {option.id}
                  </span>
                  <span className="flex-1">{option.text}</span>
                  {isSubmitted && option.isCorrect && (
                    <span className="ml-3 text-success-600">✓</span>
                  )}
                </div>
              </button>
            ))}
          </div>
        )

      case 'code':
        return (
          <div className="space-y-4">
            <div className="bg-gray-900 rounded-lg p-4">
              <pre className="text-gray-100 font-mono text-sm overflow-x-auto">
                <code>{question.codeSnippet}</code>
              </pre>
            </div>
            <textarea
              className="w-full h-40 p-3 font-mono text-sm bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="Write your code here..."
              value={selectedAnswer || ''}
              onChange={(e) => setSelectedAnswer(e.target.value)}
              disabled={isSubmitted}
            />
          </div>
        )

      case 'theory':
        return (
          <textarea
            className="w-full h-40 p-3 bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            placeholder="Type your answer here..."
            value={selectedAnswer || ''}
            onChange={(e) => setSelectedAnswer(e.target.value)}
            disabled={isSubmitted}
          />
        )

      case 'system_design':
        return (
          <div className="space-y-4">
            <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
              <h4 className="font-medium mb-2">Requirements:</h4>
              <ul className="list-disc list-inside space-y-1 text-sm">
                {question.requirements?.map((req, i) => (
                  <li key={i}>{req}</li>
                ))}
              </ul>
            </div>
            <div className="bg-yellow-50 dark:bg-yellow-900/20 p-4 rounded-lg">
              <h4 className="font-medium mb-2">Constraints:</h4>
              <ul className="list-disc list-inside space-y-1 text-sm">
                {question.constraints?.map((constraint, i) => (
                  <li key={i}>{constraint}</li>
                ))}
              </ul>
            </div>
            <textarea
              className="w-full h-60 p-3 font-mono text-sm bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="Describe your system design..."
              value={selectedAnswer || ''}
              onChange={(e) => setSelectedAnswer(e.target.value)}
              disabled={isSubmitted}
            />
          </div>
        )

      default:
        return null
    }
  }

  if (isLoading) {
    return (
      <Card className="w-full">
        <CardContent className="p-6">
          <div className="animate-pulse space-y-4">
            <div className="h-8 w-3/4 bg-gray-200 dark:bg-gray-700 rounded"></div>
            <div className="h-4 w-full bg-gray-200 dark:bg-gray-700 rounded"></div>
            <div className="h-4 w-5/6 bg-gray-200 dark:bg-gray-700 rounded"></div>
            <div className="space-y-2">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="h-12 bg-gray-200 dark:bg-gray-700 rounded"></div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="w-full">
      <CardHeader className="border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Badge variant="secondary" size="sm">
              Question {currentIndex + 1} of {totalQuestions}
            </Badge>
            <DifficultyBadge difficulty={question.difficulty} />
            <Badge variant="outline" size="sm">
              {question.subject}
            </Badge>
            <Badge variant="outline" size="sm">
              {question.topic}
            </Badge>
          </div>
          <div className="flex items-center space-x-2">
            {timeLimit && <Timer initialTime={timeLimit} onTimeUp={() => onSkip()} />}
            <BookmarkButton isBookmarked={isBookmarked} onClick={onBookmark} />
            <button
              onClick={() => setShowHint(!showHint)}
              className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            >
              <LightBulbIcon className="h-5 w-5" />
            </button>
          </div>
        </div>
      </CardHeader>

      <CardContent className="p-6 space-y-6">
        <div>
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">
            {question.title}
          </h3>
          <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
            {question.description}
          </p>
        </div>

        <AnimatePresence>
          {showHint && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
            >
              <HintSystem hints={question.hints} />
            </motion.div>
          )}
        </AnimatePresence>

        <div className="space-y-4">
          {renderQuestionContent()}
        </div>

        <AnimatePresence>
          {showResult && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className={`p-4 rounded-lg ${
                isCorrect
                  ? 'bg-success-50 dark:bg-success-900/20 border border-success-200 dark:border-success-800'
                  : 'bg-error-50 dark:bg-error-900/20 border border-error-200 dark:border-error-800'
              }`}
            >
              <div className="flex items-start space-x-3">
                <div className={`flex-shrink-0 ${
                  isCorrect ? 'text-success-600' : 'text-error-600'
                }`}>
                  {isCorrect ? '✓' : '✗'}
                </div>
                <div className="flex-1">
                  <h4 className={`font-medium mb-1 ${
                    isCorrect ? 'text-success-800' : 'text-error-800'
                  }`}>
                    {isCorrect ? 'Correct!' : 'Incorrect'}
                  </h4>
                  {showExplanation && (
                    <p className="text-sm text-gray-700 dark:text-gray-300">
                      {question.explanation}
                    </p>
                  )}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </CardContent>

      <CardFooter className="border-t border-gray-200 dark:border-gray-700 p-4">
        <div className="flex items-center justify-between w-full">
          <Button
            variant="outline"
            onClick={onPrevious}
            disabled={currentIndex === 0}
          >
            <ChevronLeftIcon className="h-4 w-4 mr-2" />
            Previous
          </Button>

          <div className="flex items-center space-x-2">
            <Button
              variant="ghost"
              onClick={onSkip}
              disabled={isSubmitted}
            >
              <FlagIcon className="h-4 w-4 mr-2" />
              Skip
            </Button>

            {!isSubmitted ? (
              <Button
                onClick={handleSubmit}
                disabled={!selectedAnswer}
              >
                Submit Answer
              </Button>
            ) : (
              <Button onClick={handleNext}>
                {currentIndex === totalQuestions - 1 ? 'Finish' : 'Next'}
                <ChevronRightIcon className="h-4 w-4 ml-2" />
              </Button>
            )}
          </div>

          <Button
            variant="outline"
            onClick={onNext}
            disabled={currentIndex === totalQuestions - 1}
          >
            Next
            <ChevronRightIcon className="h-4 w-4 ml-2" />
          </Button>
        </div>
      </CardFooter>
    </Card>
  )
}
