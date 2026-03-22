'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { motion } from 'framer-motion'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card/Card'
import { Button } from '@/components/ui/button/Button'
import { Input } from '@/components/ui/input/Input'
import { Select } from '@/components/ui/select/Select'
import { Badge } from '@/components/ui/badge/Badge'
import {
  MicrophoneIcon,
  VideoCameraIcon,
  ChatBubbleLeftRightIcon,
  BuildingOfficeIcon,
  UserGroupIcon,
  ClockIcon,
} from '@heroicons/react/24/outline'

const interviewSchema = z.object({
  interviewType: z.enum(['voice', 'video', 'text', 'mixed']),
  interviewMode: z.enum(['practice', 'mock', 'assessment', 'company_specific']),
  difficulty: z.enum(['beginner', 'intermediate', 'advanced', 'expert']),
  durationMinutes: z.number().min(15).max(120),
  companyFocus: z.string().optional(),
  roleFocus: z.string().optional(),
  categories: z.array(z.string()).optional(),
  topics: z.array(z.string()).optional(),
})

type InterviewFormData = z.infer<typeof interviewSchema>

interface InterviewSetupProps {
  onSubmit: (data: InterviewFormData) => void
  isLoading?: boolean
  companies?: Array<{ name: string; roles: string[] }>
  availableTopics?: string[]
}

const interviewTypes = [
  { value: 'voice', label: 'Voice Only', icon: MicrophoneIcon, description: 'Practice with voice responses' },
  { value: 'video', label: 'Video', icon: VideoCameraIcon, description: 'Full video interview experience' },
  { value: 'text', label: 'Text Based', icon: ChatBubbleLeftRightIcon, description: 'Type your responses' },
  { value: 'mixed', label: 'Mixed', icon: UserGroupIcon, description: 'Combine all formats' },
]

const interviewModes = [
  { value: 'practice', label: 'Practice Mode', description: 'Learn and improve at your own pace' },
  { value: 'mock', label: 'Mock Interview', description: 'Simulate real interview conditions' },
  { value: 'assessment', label: 'Skill Assessment', description: 'Evaluate your current level' },
  { value: 'company_specific', label: 'Company Specific', description: 'Practice for specific companies' },
]

const difficultyLevels = [
  { value: 'beginner', label: 'Beginner', color: 'success' },
  { value: 'intermediate', label: 'Intermediate', color: 'primary' },
  { value: 'advanced', label: 'Advanced', color: 'warning' },
  { value: 'expert', label: 'Expert', color: 'error' },
]

const durationOptions = [
  { value: 15, label: '15 minutes' },
  { value: 30, label: '30 minutes' },
  { value: 45, label: '45 minutes' },
  { value: 60, label: '1 hour' },
  { value: 90, label: '1.5 hours' },
  { value: 120, label: '2 hours' },
]

export const InterviewSetup = ({
  onSubmit,
  isLoading = false,
  companies = [],
  availableTopics = [],
}: InterviewSetupProps) => {
  const [selectedCategories, setSelectedCategories] = useState<string[]>([])
  const [selectedTopics, setSelectedTopics] = useState<string[]>([])

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<InterviewFormData>({
    resolver: zodResolver(interviewSchema),
    defaultValues: {
      interviewType: 'mixed',
      interviewMode: 'practice',
      difficulty: 'intermediate',
      durationMinutes: 30,
    },
  })

  const selectedMode = watch('interviewMode')
  const selectedCompany = watch('companyFocus')

  const categoryOptions = [
    { value: 'technical', label: 'Technical' },
    { value: 'behavioral', label: 'Behavioral' },
    { value: 'system_design', label: 'System Design' },
    { value: 'coding', label: 'Coding' },
    { value: 'ml_design', label: 'ML Design' },
  ]

  const toggleCategory = (category: string) => {
    setSelectedCategories(prev =>
      prev.includes(category)
        ? prev.filter(c => c !== category)
        : [...prev, category]
    )
    setValue('categories', selectedCategories)
  }

  const toggleTopic = (topic: string) => {
    setSelectedTopics(prev =>
      prev.includes(topic)
        ? prev.filter(t => t !== topic)
        : [...prev, topic]
    )
    setValue('topics', selectedTopics)
  }

  return (
    <Card className="w-full max-w-3xl mx-auto">
      <CardHeader>
        <CardTitle className="text-2xl">Interview Setup</CardTitle>
        <CardDescription>
          Configure your AI interview experience
        </CardDescription>
      </CardHeader>

      <CardContent>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
          {/* Interview Type */}
          <div className="space-y-4">
            <label className="text-sm font-medium">Interview Type</label>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {interviewTypes.map((type) => {
                const Icon = type.icon
                const isSelected = watch('interviewType') === type.value
                return (
                  <motion.div
                    key={type.value}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <button
                      type="button"
                      onClick={() => setValue('interviewType', type.value as any)}
                      className={`w-full p-4 rounded-lg border-2 transition-all ${
                        isSelected
                          ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                          : 'border-gray-200 dark:border-gray-700 hover:border-primary-300'
                      }`}
                    >
                      <Icon className={`h-6 w-6 mb-2 ${
                        isSelected ? 'text-primary-500' : 'text-gray-400'
                      }`} />
                      <div className={`font-medium ${
                        isSelected ? 'text-primary-700' : 'text-gray-700'
                      }`}>
                        {type.label}
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        {type.description}
                      </div>
                    </button>
                  </motion.div>
                )
              })}
            </div>
          </div>

          {/* Interview Mode */}
          <div className="space-y-4">
            <label className="text-sm font-medium">Interview Mode</label>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {interviewModes.map((mode) => {
                const isSelected = watch('interviewMode') === mode.value
                return (
                  <motion.div
                    key={mode.value}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <button
                      type="button"
                      onClick={() => setValue('interviewMode', mode.value as any)}
                      className={`w-full p-4 rounded-lg border-2 text-left transition-all ${
                        isSelected
                          ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                          : 'border-gray-200 dark:border-gray-700 hover:border-primary-300'
                      }`}
                    >
                      <div className={`font-medium ${
                        isSelected ? 'text-primary-700' : 'text-gray-700'
                      }`}>
                        {mode.label}
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        {mode.description}
                      </div>
                    </button>
                  </motion.div>
                )
              })}
            </div>
          </div>

          {/* Difficulty & Duration */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <label className="text-sm font-medium">Difficulty Level</label>
              <Select {...register('difficulty')}>
                {difficultyLevels.map((level) => (
                  <option key={level.value} value={level.value}>
                    {level.label}
                  </option>
                ))}
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Duration</label>
              <Select {...register('durationMinutes', { valueAsNumber: true })}>
                {durationOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </Select>
            </div>
          </div>

          {/* Company Specific (conditional) */}
          {selectedMode === 'company_specific' && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="space-y-4 overflow-hidden"
            >
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Target Company</label>
                  <Select {...register('companyFocus')}>
                    <option value="">Select company</option>
                    {companies.map((company) => (
                      <option key={company.name} value={company.name}>
                        {company.name}
                      </option>
                    ))}
                  </Select>
                </div>

                {selectedCompany && (
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Target Role</label>
                    <Select {...register('roleFocus')}>
                      <option value="">Select role</option>
                      {companies
                        .find(c => c.name === selectedCompany)
                        ?.roles.map((role) => (
                          <option key={role} value={role}>
                            {role}
                          </option>
                        ))}
                    </Select>
                  </div>
                )}
              </div>
            </motion.div>
          )}

          {/* Categories */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Question Categories</label>
            <div className="flex flex-wrap gap-2">
              {categoryOptions.map((category) => (
                <Badge
                  key={category.value}
                  variant={selectedCategories.includes(category.value) ? 'primary' : 'secondary'}
                  className="cursor-pointer"
                  onClick={() => toggleCategory(category.value)}
                >
                  {category.label}
                </Badge>
              ))}
            </div>
          </div>

          {/* Topics */}
          {availableTopics.length > 0 && (
            <div className="space-y-2">
              <label className="text-sm font-medium">Specific Topics</label>
              <div className="flex flex-wrap gap-2 max-h-32 overflow-y-auto p-2 border border-gray-200 dark:border-gray-700 rounded-lg">
                {availableTopics.map((topic) => (
                  <Badge
                    key={topic}
                    variant={selectedTopics.includes(topic) ? 'primary' : 'secondary'}
                    className="cursor-pointer"
                    onClick={() => toggleTopic(topic)}
                  >
                    {topic}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          <Button type="submit" className="w-full" size="lg" disabled={isLoading}>
            {isLoading ? 'Starting Interview...' : 'Start Interview'}
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}