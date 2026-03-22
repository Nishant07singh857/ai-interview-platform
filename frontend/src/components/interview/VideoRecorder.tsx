'use client'

import { useState, useRef, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Button } from '@/components/ui/button/Button'
import {
  VideoCameraIcon,
  StopIcon,
  ArrowPathIcon,
} from '@heroicons/react/24/outline'

interface VideoRecorderProps {
  onRecordingComplete: (blob: Blob) => void
  isRecording: boolean
  setIsRecording: (isRecording: boolean) => void
  videoRef: React.RefObject<HTMLVideoElement>
  maxDuration?: number // in seconds
}

export const VideoRecorder = ({
  onRecordingComplete,
  isRecording,
  setIsRecording,
  videoRef,
  maxDuration = 300,
}: VideoRecorderProps) => {
  const [recordingTime, setRecordingTime] = useState(0)
  const [isProcessing, setIsProcessing] = useState(false)
  const [permissionDenied, setPermissionDenied] = useState(false)
  const [hasCamera, setHasCamera] = useState(false)

  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const chunksRef = useRef<BlobPart[]>([])

  useEffect(() => {
    checkCameraAvailability()
  }, [])

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

  const checkCameraAvailability = async () => {
    try {
      const devices = await navigator.mediaDevices.enumerateDevices()
      setHasCamera(devices.some(device => device.kind === 'videoinput'))
    } catch (error) {
      console.error('Error checking camera:', error)
      setHasCamera(false)
    }
  }

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: true,
      })
      
      streamRef.current = stream
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream
        await videoRef.current.play()
      }

      mediaRecorderRef.current = new MediaRecorder(stream)
      chunksRef.current = []

      mediaRecorderRef.current.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data)
        }
      }

      mediaRecorderRef.current.onstop = async () => {
        const blob = new Blob(chunksRef.current, { type: 'video/webm' })
        
        setIsProcessing(true)
        try {
          await new Promise(resolve => setTimeout(resolve, 1000))
          onRecordingComplete(blob)
        } finally {
          setIsProcessing(false)
        }

        // Cleanup
        stream.getTracks().forEach(track => track.stop())
        if (videoRef.current) {
          videoRef.current.srcObject = null
        }
        setRecordingTime(0)
      }

      mediaRecorderRef.current.start()
      setPermissionDenied(false)
    } catch (error) {
      console.error('Error accessing camera:', error)
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

  if (!hasCamera) {
    return (
      <div className="p-4 bg-warning-50 dark:bg-warning-900/20 rounded-lg text-center">
        <p className="text-sm text-warning-600 dark:text-warning-400">
          No camera detected. You can still participate with audio only.
        </p>
      </div>
    )
  }

  if (permissionDenied) {
    return (
      <div className="p-4 bg-error-50 dark:bg-error-900/20 rounded-lg text-center">
        <p className="text-sm text-error-600 dark:text-error-400">
          Camera access denied. Please enable camera access to record video.
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
            Processing your video...
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Video preview */}
      {isRecording && (
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          className="relative rounded-lg overflow-hidden bg-black"
        >
          <video
            ref={videoRef}
            autoPlay
            muted
            playsInline
            className="w-full aspect-video object-cover"
          />
          
          {/* Recording indicator */}
          <div className="absolute top-4 left-4 flex items-center space-x-2 bg-black/50 backdrop-blur-sm px-3 py-1.5 rounded-full">
            <div className="h-2 w-2 bg-error-500 rounded-full animate-pulse" />
            <span className="text-xs text-white">REC</span>
          </div>

          {/* Timer */}
          <div className="absolute top-4 right-4 bg-black/50 backdrop-blur-sm px-3 py-1.5 rounded-full">
            <span className="text-xs text-white">{formatTime(recordingTime)}</span>
          </div>

          {/* Recording tips */}
          <div className="absolute bottom-4 left-4 right-4 text-center">
            <div className="inline-block bg-black/50 backdrop-blur-sm px-4 py-2 rounded-lg">
              <p className="text-xs text-white">
                Look at the camera and speak clearly
              </p>
            </div>
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
            <VideoCameraIcon className="h-4 w-4 mr-2" />
            Start Recording
          </>
        )}
      </Button>
    </div>
  )
}