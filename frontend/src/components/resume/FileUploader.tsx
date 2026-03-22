'use client'

import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { motion, AnimatePresence } from 'framer-motion'
import { Card } from '@/components/ui/card/Card'
import { Button } from '@/components/ui/button/Button'
import { Progress } from '@/components/ui/progress/Progress'
import {
  DocumentArrowUpIcon,
  DocumentTextIcon,
  XMarkIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
} from '@heroicons/react/24/outline'

interface FileUploaderProps {
  onUpload: (file: File) => void
  onCancel?: () => void
  accept?: Record<string, string[]>
  maxSize?: number // in MB
  isUploading?: boolean
  uploadProgress?: number
  error?: string | null
}

const defaultAccept = {
  'application/pdf': ['.pdf'],
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
  'text/plain': ['.txt'],
}

export const FileUploader = ({
  onUpload,
  onCancel,
  accept = defaultAccept,
  maxSize = 10, // 10MB default
  isUploading = false,
  uploadProgress = 0,
  error = null,
}: FileUploaderProps) => {
  const [file, setFile] = useState<File | null>(null)
  const [fileError, setFileError] = useState<string | null>(null)

  const onDrop = useCallback((acceptedFiles: File[], rejectedFiles: any[]) => {
    if (rejectedFiles.length > 0) {
      const error = rejectedFiles[0].errors[0]
      if (error.code === 'file-too-large') {
        setFileError(`File is too large. Max size is ${maxSize}MB`)
      } else if (error.code === 'file-invalid-type') {
        setFileError('Invalid file type. Please upload PDF, DOCX, or TXT')
      } else {
        setFileError('Error uploading file')
      }
      return
    }

    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0])
      setFileError(null)
    }
  }, [maxSize])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept,
    maxSize: maxSize * 1024 * 1024,
    multiple: false,
  })

  const handleUpload = () => {
    if (file) {
      onUpload(file)
    }
  }

  const handleCancel = () => {
    setFile(null)
    setFileError(null)
    onCancel?.()
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  return (
    <Card className="p-6">
      <div className="space-y-4">
        {/* Dropzone */}
        {!file && !isUploading && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                isDragActive
                  ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                  : 'border-gray-300 dark:border-gray-700 hover:border-primary-400 dark:hover:border-primary-600'
              }`}
            >
              <input {...getInputProps()} />
              <DocumentArrowUpIcon className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <p className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                {isDragActive ? 'Drop your resume here' : 'Drag & drop your resume'}
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                or click to browse
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-500">
                Supports PDF, DOCX, TXT (Max {maxSize}MB)
              </p>
            </div>
          </motion.div>
        )}

        {/* File Preview */}
        <AnimatePresence>
          {file && !isUploading && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="overflow-hidden"
            >
              <div className="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <DocumentTextIcon className="h-8 w-8 text-primary-500" />
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white">
                        {file.name}
                      </p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {formatFileSize(file.size)}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={handleCancel}
                    className="p-1 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-full transition-colors"
                  >
                    <XMarkIcon className="h-5 w-5 text-gray-500" />
                  </button>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Upload Progress */}
        <AnimatePresence>
          {isUploading && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-3"
            >
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-700 dark:text-gray-300">Uploading...</span>
                <span className="text-gray-600 dark:text-gray-400">{uploadProgress}%</span>
              </div>
              <Progress value={uploadProgress} variant="primary" size="md" />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Error Message */}
        <AnimatePresence>
          {(fileError || error) && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="flex items-center space-x-2 text-error-600 bg-error-50 dark:bg-error-900/20 p-3 rounded-lg"
            >
              <ExclamationCircleIcon className="h-5 w-5 flex-shrink-0" />
              <span className="text-sm">{fileError || error}</span>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Action Buttons */}
        {file && !isUploading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex space-x-3"
          >
            <Button
              onClick={handleUpload}
              className="flex-1"
            >
              Upload Resume
            </Button>
            <Button
              variant="outline"
              onClick={handleCancel}
            >
              Cancel
            </Button>
          </motion.div>
        )}

        {/* Success Message */}
        {!file && !isUploading && !error && uploadProgress === 100 && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex items-center justify-center space-x-2 text-success-600 bg-success-50 dark:bg-success-900/20 p-4 rounded-lg"
          >
            <CheckCircleIcon className="h-5 w-5" />
            <span>Resume uploaded successfully!</span>
          </motion.div>
        )}
      </div>
    </Card>
  )
}