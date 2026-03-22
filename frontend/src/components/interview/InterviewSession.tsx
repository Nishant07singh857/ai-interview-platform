'use client'

import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/card/Card'
import { Button } from '@/components/ui/button/Button'
import { Badge } from '@/components/ui/badge/Badge'
import { Progress } from '@/components/ui/progress/Progress'
import { Timer } from '@/components/practice/Timer'
import { VoiceRecorder } from './VoiceRecorder'
import { VideoRecorder } from './VideoRecorder'
import { TranscriptViewer } from './TranscriptViewer'
import { FeedbackPanel } from './FeedbackPanel'
import {
  MicrophoneIcon,
  VideoCameraIcon,
  ChatBubbleLeftRightIcon,
  PauseIcon,
  PlayIcon,
  FlagIcon,
  LightBulbIcon,
  ArrowPathIcon,
} from '@heroicons/react/24/outline'

interface InterviewSessionProps {
  sessionId: string
  interviewType: 'voice' | 'video' | 'text' | 'mixed'
  currentQuestion: {
    questionId: string
    questionText: string
    context?: string
    category: string
    difficulty: string
    hint?: string
  }
  questionNumber: number
  totalQuestions: number
  timeElapsed: number
  timeRemaining: number
  onResponse: (response: { text?: string; audio?: Blob; video?: Blob }) => void
  onNext: () => void
  onPause: () => void
  onResume: () => void
  onEnd: () => void
  onHint: () => void
  isLoading?: boolean
  isPaused?: boolean
}

export const InterviewSession = ({
  sessionId,
  interviewType,
  currentQuestion,
  questionNumber,
  totalQuestions,
  timeElapsed,
  timeRemaining,
  onResponse,
  onNext,
  onPause,
  onResume,
  onEnd,
  onHint,
  isLoading = false,
  isPaused = false,
}: InterviewSessionProps) => {
  const [response, setResponse] = useState('')
  const [isRecording, setIsRecording] = useState(false)
  const [showHint, setShowHint] = useState(false)
  const [showFeedback, setShowFeedback] = useState(false)
  const [transcript, setTranscript] = useState<string[]>([])
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null)
  const [videoBlob, setVideoBlob] = useState<Blob | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  
  const videoRef = useRef<HTMLVideoElement>(null)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<BlobPart[]>([])

  useEffect(() => {
    // Reset state for new question
    setResponse('')
    setShowHint(false)
    setAudioBlob(null)
    setVideoBlob(null)
    setTranscript([])
  }, [currentQuestion])

  const handleSubmitResponse = async () => {
    setIsSubmitting(true)
    
    try {
      await onResponse({
        text: response,
        audio: audioBlob || undefined,
        video: videoBlob || undefined,
      })
      
      setShowFeedback(true)
    } catch (error) {
      console.error('Error submitting response:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleNext = () => {
    setShowFeedback(false)
    onNext()
  }

  const renderInputMethod = () => {
    switch (interviewType) {
      case 'voice':
        return (
          <VoiceRecorder
            onRecordingComplete={(blob, text) => {
              setAudioBlob(blob)
              setTranscript(prev => [...prev, text])
            }}
            isRecording={isRecording}
            setIsRecording={setIsRecording}
          />
        )
      
      case 'video':
        return (
          <VideoRecorder
            onRecordingComplete={(blob) => setVideoBlob(blob)}
            isRecording={isRecording}
            setIsRecording={setIsRecording}
            videoRef={videoRef}
          />
        )
      
      case 'text':
        return (
          <textarea
            value={response}
            onChange={(e) => setResponse(e.target.value)}
            placeholder="Type your answer here..."
            className="w-full h-40 p-4 bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
            disabled={isSubmitting || showFeedback}
          />
        )
      
      case 'mixed':
        return (
          <div className="space-y-4">
            <div className="flex items-center space-x-4">
              <Button
                variant={isRecording ? 'error' : 'outline'}
                onClick={() => setIsRecording(!isRecording)}
                disabled={isSubmitting || showFeedback}
              >
                {isRecording ? (
                  <>
                    <div className="h-2 w-2 bg-error-500 rounded-full animate-pulse mr-2" />
                    Stop Recording
                  </>
                ) : (
                  <>
                    <MicrophoneIcon className="h-4 w-4 mr-2" />
                    Start Recording
                  </>
                )}
              </Button>
              <span className="text-sm text-gray-500">or</span>
              <Button
                variant="outline"
                onClick={() => {/* Switch to text */}}
                disabled={isSubmitting || showFeedback}
              >
                <ChatBubbleLeftRightIcon className="h-4 w-4 mr-2" />
                Type Response
              </Button>
            </div>

            {isRecording ? (
              <div className="space-y-2">
                <div className="flex items-center space-x-2 text-sm text-gray-600">
                  <div className="h-2 w-2 bg-error-500 rounded-full animate-pulse" />
                  <span>Recording in progress...</span>
                </div>
                <VoiceRecorder
                  onRecordingComplete={(blob, text) => {
                    setAudioBlob(blob)
                    setTranscript(prev => [...prev, text])
                  }}
                  isRecording={isRecording}
                  setIsRecording={setIsRecording}
                />
              </div>
            ) : (
              <textarea
                value={response}
                onChange={(e) => setResponse(e.target.value)}
                placeholder="Or type your answer here..."
                className="w-full h-32 p-3 bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
                disabled={isSubmitting || showFeedback}
              />
            )}
          </div>
        )
      
      default:
        return null
    }
  }

  if (isLoading) {
    return (
      <Card className="w-full max-w-3xl mx-auto">
        <CardContent className="p-8">
          <div className="flex items-center justify-center">
            <ArrowPathIcon className="h-8 w-8 animate-spin text-primary-500" />
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="w-full max-w-3xl mx-auto">
      <CardHeader className="border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Badge variant="primary" size="sm">
              Question {questionNumber} of {totalQuestions}
            </Badge>
            <Badge variant={currentQuestion.difficulty === 'hard' ? 'error' : 'warning'} size="sm">
              {currentQuestion.difficulty}
            </Badge>
            <Badge variant="secondary" size="sm">
              {currentQuestion.category}
            </Badge>
          </div>
          <div className="flex items-center space-x-3">
            <Timer
              initialTime={timeRemaining}
              onTimeUp={onNext}
              isPaused={isPaused}
            />
            {!isPaused ? (
              <Button variant="outline" size="sm" onClick={onPause}>
                <PauseIcon className="h-4 w-4" />
              </Button>
            ) : (
              <Button variant="outline" size="sm" onClick={onResume}>
                <PlayIcon className="h-4 w-4" />
              </Button>
            )}
            <Button variant="ghost" size="sm" onClick={onEnd}>
              <FlagIcon className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent className="p-6 space-y-6">
        {/* Question */}
        <div className="space-y-3">
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
            {currentQuestion.questionText}
          </h3>
          {currentQuestion.context && (
            <p className="text-sm text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-800/50 p-3 rounded-lg">
              {currentQuestion.context}
            </p>
          )}
        </div>

        {/* Hint */}
        <AnimatePresence>
          {showHint && currentQuestion.hint && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="bg-yellow-50 dark:bg-yellow-900/20 p-3 rounded-lg border border-yellow-200 dark:border-yellow-800"
            >
              <div className="flex items-start space-x-2">
                <LightBulbIcon className="h-5 w-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-yellow-800 dark:text-yellow-200">
                  {currentQuestion.hint}
                </p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Response Area */}
        {!showFeedback ? (
          <div className="space-y-4">
            {renderInputMethod()}

            {/* Transcript */}
            {transcript.length > 0 && (
              <TranscriptViewer transcript={transcript} />
            )}

            {/* Action Buttons */}
            <div className="flex items-center justify-between pt-4">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowHint(true)}
                disabled={showHint || isSubmitting}
              >
                <LightBulbIcon className="h-4 w-4 mr-2" />
                Get Hint
              </Button>

              <div className="flex items-center space-x-3">
                <Button
                  variant="outline"
                  onClick={() => {/* Skip */}}
                  disabled={isSubmitting}
                >
                  Skip
                </Button>
                <Button
                  onClick={handleSubmitResponse}
                  disabled={
                    (!response && !audioBlob && !videoBlob) ||
                    isSubmitting
                  }
                >
                  {isSubmitting ? 'Submitting...' : 'Submit Response'}
                </Button>
              </div>
            </div>
          </div>
        ) : (
          <FeedbackPanel
            questionId={currentQuestion.questionId}
            sessionId={sessionId}
            onContinue={handleNext}
          />
        )}
      </CardContent>

      <CardFooter className="border-t border-gray-200 dark:border-gray-700 p-4">
        <Progress
          value={(questionNumber / totalQuestions) * 100}
          variant="primary"
          size="sm"
        />
      </CardFooter>
    </Card>
  )
}