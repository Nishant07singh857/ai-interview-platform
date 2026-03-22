'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Card } from '@/components/ui/card/Card'
import { Button } from '@/components/ui/button/Button'
import { AcademicCapIcon, ChevronDownIcon, LinkIcon } from '@heroicons/react/24/outline'

interface ExplanationBoxProps {
  explanation: string
  detailedExplanation?: string
  references?: Array<{
    title: string
    url: string
  }>
  commonMistakes?: string[]
}

export const ExplanationBox = ({
  explanation,
  detailedExplanation,
  references = [],
  commonMistakes = [],
}: ExplanationBoxProps) => {
  const [isExpanded, setIsExpanded] = useState(false)

  return (
    <Card className="bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800">
      <div className="p-4">
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="w-full flex items-center justify-between text-left"
        >
          <div className="flex items-center space-x-2">
            <AcademicCapIcon className="h-5 w-5 text-blue-600 dark:text-blue-400" />
            <span className="font-medium text-blue-800 dark:text-blue-200">
              Explanation
            </span>
          </div>
          <ChevronDownIcon
            className={`h-5 w-5 text-blue-600 dark:text-blue-400 transition-transform ${
              isExpanded ? 'rotate-180' : ''
            }`}
          />
        </button>

        <AnimatePresence>
          {isExpanded && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mt-4 space-y-4 overflow-hidden"
            >
              <div className="p-3 bg-white dark:bg-gray-800 rounded-lg">
                <p className="text-sm text-gray-700 dark:text-gray-300">{explanation}</p>
              </div>

              {detailedExplanation && (
                <div className="space-y-2">
                  <h4 className="text-sm font-medium text-blue-800 dark:text-blue-200">
                    Detailed Explanation
                  </h4>
                  <div className="p-3 bg-white dark:bg-gray-800 rounded-lg">
                    <p className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                      {detailedExplanation}
                    </p>
                  </div>
                </div>
              )}

              {commonMistakes.length > 0 && (
                <div className="space-y-2">
                  <h4 className="text-sm font-medium text-blue-800 dark:text-blue-200">
                    Common Mistakes
                  </h4>
                  <ul className="list-disc list-inside space-y-1">
                    {commonMistakes.map((mistake, index) => (
                      <li key={index} className="text-sm text-gray-700 dark:text-gray-300">
                        {mistake}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {references.length > 0 && (
                <div className="space-y-2">
                  <h4 className="text-sm font-medium text-blue-800 dark:text-blue-200">
                    References
                  </h4>
                  <div className="space-y-2">
                    {references.map((ref, index) => (
                      <a
                        key={index}
                        href={ref.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center space-x-2 p-2 bg-white dark:bg-gray-800 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                      >
                        <LinkIcon className="h-4 w-4 text-blue-600 dark:text-blue-400" />
                        <span className="text-sm text-gray-700 dark:text-gray-300">
                          {ref.title}
                        </span>
                      </a>
                    ))}
                  </div>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </Card>
  )
}