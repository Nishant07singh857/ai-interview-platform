'use client'

import { useState, useRef, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Button } from '@/components/ui/button/Button'
import {
  MicrophoneIcon,
  StopIcon,
  SpeakerWaveIcon,
  ArrowPathIcon,
} from '@heroicons/react/24/outline'

interface VoiceRecorderProps {
  onRecordingComplete: (blob: Blob, transcript: string) => void
  isRecording: boolean
  setIsRecording: (isRecording: boolean) => void
  maxDuration?: number // in seconds
}

export const VoiceRecorder = ({
  onRecordingComplete,
  isRecording,
  setIsRecording,
  maxDuration = 300, // 5 minutes default
}: VoiceRecorderProps) => {
  const [recordingTime, setRecordingTime] = useState(0)
  const [audioLevel, setAudioLevel] = useState(0)
  const [isProcessing, setIsProcessing] = useState(false)
  const [permissionDenied, setPermissionDenied] = useState(false)

  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<BlobPart[]>([])
  const analyserRef = useRef<AnalyserNode | null>(null)
  const audioContextRef = useRef<AudioContext | null>(null)
  const sourceRef = useRef<MediaStreamAudioSourceNode | null>(null)
  const animationFrameRef = useRef<number>()

  useEffect(() => {
    if (isRecording) {
      startRecording()
    } else {
      stopRecording()
    }
  }, [isRecording])

  useEffect(() => {
    let interval: NodeJS.Timeout
    if (isRecording) {
      interval = setInterval(() => {
        setRecordingTime(prev => {
          if (prev >= maxDuration) {
            stopRecording()
            return prev
          }
          return prev + 1
        })
      }, 1000)
    }
    return () => clearInterval(interval)
  }, [isRecording, maxDuration])

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      
      // Setup audio analysis
      audioContextRef.current = new AudioContext()
      analyserRef.current = audioContextRef.current.createAnalyser()
      sourceRef.current = audioContextRef.current.createMediaStreamSource(stream)
      sourceRef.current.connect(analyserRef.current)
      analyserRef.current.fftSize = 256

      // Start analyzing audio levels
      const updateAudioLevel = () => {
        if (analyserRef.current && isRecording) {
          const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount)
          analyserRef.current.getByteFrequencyData(dataArray)
          const average = dataArray.reduce((a, b) => a + b, 0) / dataArray.length
          setAudioLevel(average / 255) // Normalize to 0-1
          animationFrameRef.current = requestAnimationFrame(updateAudioLevel)
        }
      }
      updateAudioLevel()

      // Setup media recorder
      mediaRecorderRef.current = new MediaRecorder(stream)
      chunksRef.current = []

      mediaRecorderRef.current.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data)
        }
      }

      mediaRecorderRef.current.onstop = async () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' })
        
        // Simulate speech-to-text (replace with actual API call)
        setIsProcessing(true)
        try {
          // This would be replaced with actual speech-to-text API
          await new Promise(resolve => setTimeout(resolve, 1500))
          const mockTranscript = "This is a simulated transcript of the recorded audio."
          onRecordingComplete(blob, mockTranscript)
        } finally {
          setIsProcessing(false)
        }

        // Cleanup
        stream.getTracks().forEach(track => track.stop())
        if (animationFrameRef.current) {
          cancelAnimationFrame(animationFrameRef.current)
        }
        if (audioContextRef.current) {
          await audioContextRef.current.close()
        }
        setAudioLevel(0)
        setRecordingTime(0)
      }

      mediaRecorderRef.current.start()
      setPermissionDenied(false)
    } catch (error) {
      console.error('Error accessing microphone:', error)
      setPermissionDenied(true)
      setIsRecording(false)
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
    }
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  if (permissionDenied) {
    return (
      <div className="p-4 bg-error-50 dark:bg-error-900/20 rounded-lg text-center">
        <p className="text-sm text-error-600 dark:text-error-400">
          Microphone access denied. Please enable microphone access to record your response.
        </p>
      </div>
    )
  }

  if (isProcessing) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <ArrowPathIcon className="h-8 w-8 animate-spin text-primary-500 mx-auto mb-3" />
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Processing your recording...
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Recording visualization */}
      {isRecording && (
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          className="bg-gray-50 dark:bg-gray-800/50 p-4 rounded-lg"
        >
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-2">
              <div className="h-3 w-3 bg-error-500 rounded-full animate-pulse" />
              <span className="text-sm font-medium">Recording in progress</span>
            </div>
            <span className="text-sm text-gray-600 dark:text-gray-400">
              {formatTime(recordingTime)} / {formatTime(maxDuration)}
            </span>
          </div>

          {/* Audio level visualization */}
          <div className="flex items-center space-x-1 h-8">
            {[...Array(20)].map((_, i) => (
              <motion.div
                key={i}
                className="w-1 bg-primary-500 rounded-full"
                animate={{
                  height: `${Math.max(4, audioLevel * 100 * (0.5 + Math.random() * 0.5))}%`,
                }}
                transition={{ duration: 0.1 }}
              />
            ))}
          </div>

          <div className="flex items-center justify-center mt-3 text-xs text-gray-500">
            <SpeakerWaveIcon className="h-3 w-3 mr-1" />
            Speak clearly into your microphone
          </div>
        </motion.div>
      )}

      {/* Control button */}
      <Button
        variant={isRecording ? 'error' : 'primary'}
        onClick={() => setIsRecording(!isRecording)}
        className="w-full"
      >
        {isRecording ? (
          <>
            <StopIcon className="h-4 w-4 mr-2" />
            Stop Recording
          </>
        ) : (
          <>
            <MicrophoneIcon className="h-4 w-4 mr-2" />
            Start Recording
          </>
        )}
      </Button>
    </div>
  )
}