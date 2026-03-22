'use client'

import { motion } from 'framer-motion'
import { Card } from '@/components/ui/card/Card'
import { DocumentTextIcon } from '@heroicons/react/24/outline'

interface TranscriptViewerProps {
  transcript: string[]
  isLive?: boolean
}

export const TranscriptViewer = ({ transcript, isLive = false }: TranscriptViewerProps) => {
  return (
    <Card className="bg-gray-50 dark:bg-gray-800/50">
      <div className="p-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2">
            <DocumentTextIcon className="h-5 w-5 text-primary-500" />
            <h4 className="font-medium text-gray-900 dark:text-white">Transcript</h4>
          </div>
          {isLive && (
            <div className="flex items-center space-x-1">
              <div className="h-2 w-2 bg-success-500 rounded-full animate-pulse" />
              <span className="text-xs text-gray-500">Live</span>
            </div>
          )}
        </div>

        <div className="space-y-2 max-h-60 overflow-y-auto custom-scrollbar">
          {transcript.map((text, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="p-2 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
            >
              <p className="text-sm text-gray-700 dark:text-gray-300">{text}</p>
              {isLive && index === transcript.length - 1 && (
                <motion.div
                  animate={{ opacity: [1, 0.5, 1] }}
                  transition={{ duration: 1, repeat: Infinity }}
                  className="h-4 w-1 bg-primary-500 inline-block ml-1"
                />
              )}
            </motion.div>
          ))}
        </div>

        {transcript.length === 0 && (
          <div className="text-center py-8">
            <p className="text-sm text-gray-500">
              No transcript available yet. Start speaking to see your words here.
            </p>
          </div>
        )}
      </div>
    </Card>
  )
}