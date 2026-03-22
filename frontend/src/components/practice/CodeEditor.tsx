'use client'

import { useState, useEffect } from 'react'
import Editor from '@monaco-editor/react'
import { Card } from '@/components/ui/card/Card'
import { Button } from '@/components/ui/button/Button'
import { Select } from '@/components/ui/select/Select'
import { Badge } from '@/components/ui/badge/Badge'
import {
  PlayIcon,
  ArrowPathIcon,
  CheckCircleIcon,
  XCircleIcon,
} from '@heroicons/react/24/outline'

interface CodeEditorProps {
  initialCode?: string
  language?: string
  testCases?: Array<{
    input: string
    output: string
    hidden?: boolean
  }>
  timeLimit?: number
  memoryLimit?: number
  onRun?: (code: string) => void
  onSubmit?: (code: string) => void
  readOnly?: boolean
}

const languageOptions = [
  { value: 'python', label: 'Python' },
  { value: 'javascript', label: 'JavaScript' },
  { value: 'java', label: 'Java' },
  { value: 'cpp', label: 'C++' },
  { value: 'csharp', label: 'C#' },
  { value: 'go', label: 'Go' },
  { value: 'rust', label: 'Rust' },
  { value: 'ruby', label: 'Ruby' },
]

export const CodeEditor = ({
  initialCode = '# Write your code here\n',
  language = 'python',
  testCases = [],
  timeLimit,
  memoryLimit,
  onRun,
  onSubmit,
  readOnly = false,
}: CodeEditorProps) => {
  const [code, setCode] = useState(initialCode)
  const [selectedLanguage, setSelectedLanguage] = useState(language)
  const [isRunning, setIsRunning] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [testResults, setTestResults] = useState<Array<{
    passed: boolean
    input: string
    expected: string
    actual?: string
    error?: string
    time?: number
    hidden?: boolean
  }>>([])
  const [showResults, setShowResults] = useState(false)

  const handleEditorChange = (value: string | undefined) => {
    if (value !== undefined) {
      setCode(value)
    }
  }

  const handleRun = async () => {
    setIsRunning(true)
    setShowResults(true)
    
    try {
      // Simulate code execution
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      const results = testCases.map((testCase, index) => ({
        passed: Math.random() > 0.3,
        input: testCase.input,
        expected: testCase.output,
        actual: testCase.output, // Simulated
        time: Math.floor(Math.random() * 100) + 50,
        hidden: testCase.hidden,
      }))
      
      setTestResults(results)
      onRun?.(code)
    } catch (error) {
      console.error('Error running code:', error)
    } finally {
      setIsRunning(false)
    }
  }

  const handleSubmit = async () => {
    setIsSubmitting(true)
    setShowResults(true)
    
    try {
      // Simulate submission
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      const results = testCases.map((testCase, index) => ({
        passed: Math.random() > 0.2,
        input: testCase.input,
        expected: testCase.output,
        actual: testCase.output, // Simulated
        time: Math.floor(Math.random() * 100) + 50,
        hidden: testCase.hidden,
      }))
      
      setTestResults(results)
      onSubmit?.(code)
    } catch (error) {
      console.error('Error submitting code:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  const passedTests = testResults.filter(r => r.passed).length
  const totalTests = testResults.length

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Select
            value={selectedLanguage}
            onChange={(e) => setSelectedLanguage(e.target.value)}
            options={languageOptions}
            className="w-40"
            disabled={readOnly}
          />
          {(timeLimit || memoryLimit) && (
            <div className="flex items-center space-x-3 text-sm text-gray-600 dark:text-gray-400">
              {timeLimit && (
                <Badge variant="outline" size="sm">
                  Time: {timeLimit}ms
                </Badge>
              )}
              {memoryLimit && (
                <Badge variant="outline" size="sm">
                  Memory: {memoryLimit}MB
                </Badge>
              )}
            </div>
          )}
        </div>
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            onClick={handleRun}
            disabled={isRunning || isSubmitting || readOnly}
          >
            {isRunning ? (
              <ArrowPathIcon className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <PlayIcon className="h-4 w-4 mr-2" />
            )}
            Run
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={isRunning || isSubmitting || readOnly}
          >
            {isSubmitting ? (
              <ArrowPathIcon className="h-4 w-4 mr-2 animate-spin" />
            ) : null}
            Submit
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card className="overflow-hidden">
          <Editor
            height="500px"
            language={selectedLanguage}
            value={code}
            onChange={handleEditorChange}
            theme="vs-dark"
            options={{
              minimap: { enabled: false },
              fontSize: 14,
              readOnly,
              automaticLayout: true,
              scrollBeyondLastLine: false,
              wordWrap: 'on',
              lineNumbers: 'on',
              renderWhitespace: 'selection',
              tabSize: 2,
            }}
          />
        </Card>

        {showResults && (
          <Card className="p-4 overflow-auto" style={{ maxHeight: '500px' }}>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-semibold">Test Results</h3>
                {testResults.length > 0 && (
                  <Badge variant={passedTests === totalTests ? 'success' : 'warning'}>
                    {passedTests}/{totalTests} Passed
                  </Badge>
                )}
              </div>

              {testResults.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  Run your code to see test results
                </div>
              ) : (
                <div className="space-y-3">
                  {testResults.map((result, index) => (
                    <div
                      key={index}
                      className={`p-3 rounded-lg border ${
                        result.passed
                          ? 'border-success-200 bg-success-50 dark:border-success-800 dark:bg-success-900/20'
                          : 'border-error-200 bg-error-50 dark:border-error-800 dark:bg-error-900/20'
                      }`}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center">
                          {result.passed ? (
                            <CheckCircleIcon className="h-5 w-5 text-success-500 mr-2" />
                          ) : (
                            <XCircleIcon className="h-5 w-5 text-error-500 mr-2" />
                          )}
                          <span className="font-medium">
                            Test Case {index + 1}
                            {result.hidden && ' (Hidden)'}
                          </span>
                        </div>
                        {result.time && (
                          <span className="text-xs text-gray-500">{result.time}ms</span>
                        )}
                      </div>

                      <div className="space-y-2 text-sm">
                        <div>
                          <span className="text-gray-600 dark:text-gray-400">Input: </span>
                          <code className="bg-gray-100 dark:bg-gray-800 px-2 py-0.5 rounded">
                            {result.input}
                          </code>
                        </div>
                        <div>
                          <span className="text-gray-600 dark:text-gray-400">Expected: </span>
                          <code className="bg-gray-100 dark:bg-gray-800 px-2 py-0.5 rounded">
                            {result.expected}
                          </code>
                        </div>
                        {result.actual && (
                          <div>
                            <span className="text-gray-600 dark:text-gray-400">Actual: </span>
                            <code className={`px-2 py-0.5 rounded ${
                              result.passed
                                ? 'bg-success-100 dark:bg-success-900'
                                : 'bg-error-100 dark:bg-error-900'
                            }`}>
                              {result.actual}
                            </code>
                          </div>
                        )}
                        {result.error && (
                          <div className="text-error-600 text-xs mt-1">
                            Error: {result.error}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </Card>
        )}
      </div>
    </div>
  )
}
