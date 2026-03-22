'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Card } from '@/components/ui/card/Card'
import { Button } from '@/components/ui/button/Button'
import { LightBulbIcon, ChevronDownIcon } from '@heroicons/react/24/outline'

interface HintSystemProps {
  hints: string[]
  onHintUsed?: (hintIndex: number) => void
}

export const HintSystem = ({ hints, onHintUsed }: HintSystemProps) => {
  const [revealedHints, setRevealedHints] = useState<number[]>([])
  const [isExpanded, setIsExpanded] = useState(false)

  const revealHint = (index: number) => {
    if (!revealedHints.includes(index)) {
      setRevealedHints([...revealedHints, index])
      onHintUsed?.(index)
    }
  }

  if (hints.length === 0) {
    return null
  }

  return (
    <Card className="bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800">
      <div className="p-4">
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="w-full flex items-center justify-between text-left"
        >
          <div className="flex items-center space-x-2">
            <LightBulbIcon className="h-5 w-5 text-yellow-600 dark:text-yellow-400" />
            <span className="font-medium text-yellow-800 dark:text-yellow-200">
              Hints ({revealedHints.length}/{hints.length})
            </span>
          </div>
          <ChevronDownIcon
            className={`h-5 w-5 text-yellow-600 dark:text-yellow-400 transition-transform ${
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
              className="mt-4 space-y-3 overflow-hidden"
            >
              {hints.map((hint, index) => (
                <div key={index} className="space-y-2">
                  {revealedHints.includes(index) ? (
                    <div className="p-3 bg-white dark:bg-gray-800 rounded-lg border border-yellow-200 dark:border-yellow-800">
                      <p className="text-sm text-gray-700 dark:text-gray-300">{hint}</p>
                    </div>
                  ) : (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => revealHint(index)}
                      className="w-full justify-center border-yellow-300 dark:border-yellow-700 text-yellow-700 dark:text-yellow-300 hover:bg-yellow-100 dark:hover:bg-yellow-900/50"
                    >
                      Reveal Hint {index + 1}
                    </Button>
                  )}
                </div>
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </Card>
  )
}