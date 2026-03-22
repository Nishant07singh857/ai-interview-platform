'use client'

import { motion } from 'framer-motion'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card/Card'
import { Progress } from '@/components/ui/progress/Progress'
import { Badge } from '@/components/ui/badge/Badge'
import { Button } from '@/components/ui/button/Button'
import {
  ArrowTrendingUpIcon,
  ClockIcon,
  AcademicCapIcon,
  BriefcaseIcon,
  CodeBracketIcon,
  UserGroupIcon,
  DocumentTextIcon,
} from '@heroicons/react/24/outline'

interface GapAnalysisProps {
  analysis: {
    overall_readiness: number
    technical_readiness: number
    behavioral_readiness: number
    system_design_readiness: number
    skill_gaps: Array<{
      skill: string
      current_level: string
      required_level: string
      severity: string
      estimated_time: number
    }>
    experience_gap: {
      current: number
      required: number
      gap: number
    }
    education_gap: {
      current: string
      required: string
      gap: number
    }
    project_gap: {
      current: number
      required: number
      gap: number
    }
    high_priority_gaps: any[]
    estimated_preparation_time: number
    recommended_interview_date: string
  }
  targetCompany: string
  targetRole: string
  isLoading?: boolean
  onGenerateRoadmap?: () => void
}

export const GapAnalysis = ({
  analysis,
  targetCompany,
  targetRole,
  isLoading = false,
  onGenerateRoadmap,
}: GapAnalysisProps) => {
  const getReadinessColor = (score: number) => {
    if (score >= 80) return 'success'
    if (score >= 60) return 'primary'
    if (score >= 40) return 'warning'
    return 'error'
  }

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'expert': return 'success'
      case 'advanced': return 'primary'
      case 'intermediate': return 'warning'
      default: return 'error'
    }
  }

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <div className="animate-pulse">
            <div className="h-6 w-64 bg-gray-200 dark:bg-gray-700 rounded mb-2"></div>
            <div className="h-4 w-48 bg-gray-200 dark:bg-gray-700 rounded"></div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="space-y-2">
                <div className="h-4 w-32 bg-gray-200 dark:bg-gray-700 rounded"></div>
                <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded"></div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Gap Analysis: {targetCompany}</CardTitle>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              {targetRole} - Readiness Assessment
            </p>
          </div>
          <Badge variant={getReadinessColor(analysis.overall_readiness)} size="lg">
            {analysis.overall_readiness}% Ready
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Readiness Scores */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600 dark:text-gray-400">Technical</span>
              <CodeBracketIcon className="h-5 w-5 text-primary-500" />
            </div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              {analysis.technical_readiness}%
            </div>
            <Progress value={analysis.technical_readiness} variant={getReadinessColor(analysis.technical_readiness)} />
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600 dark:text-gray-400">Behavioral</span>
              <UserGroupIcon className="h-5 w-5 text-primary-500" />
            </div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              {analysis.behavioral_readiness}%
            </div>
            <Progress value={analysis.behavioral_readiness} variant={getReadinessColor(analysis.behavioral_readiness)} />
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600 dark:text-gray-400">System Design</span>
              <DocumentTextIcon className="h-5 w-5 text-primary-500" />
            </div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              {analysis.system_design_readiness}%
            </div>
            <Progress value={analysis.system_design_readiness} variant={getReadinessColor(analysis.system_design_readiness)} />
          </motion.div>
        </div>

        {/* Skill Gaps */}
        <div className="space-y-4">
          <h4 className="font-medium text-gray-900 dark:text-white">Skill Gaps</h4>
          <div className="space-y-3">
            {analysis.skill_gaps.map((gap, index) => (
              <motion.div
                key={gap.skill}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg"
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <span className="font-medium text-gray-900 dark:text-white">{gap.skill}</span>
                    <Badge variant={getLevelColor(gap.severity)} size="sm">
                      {gap.severity} priority
                    </Badge>
                  </div>
                  <span className="text-sm text-gray-600 dark:text-gray-400">
                    Est. {gap.estimated_time} days
                  </span>
                </div>
                <div className="flex items-center space-x-4 text-sm">
                  <div>
                    <span className="text-gray-600 dark:text-gray-400">Current: </span>
                    <Badge variant={getLevelColor(gap.current_level)} size="sm">
                      {gap.current_level}
                    </Badge>
                  </div>
                  <ArrowTrendingUpIcon className="h-4 w-4 text-gray-400" />
                  <div>
                    <span className="text-gray-600 dark:text-gray-400">Required: </span>
                    <Badge variant={getLevelColor(gap.required_level)} size="sm">
                      {gap.required_level}
                    </Badge>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Experience, Education, Project Gaps */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg"
          >
            <div className="flex items-center space-x-2 mb-3">
              <BriefcaseIcon className="h-5 w-5 text-primary-500" />
              <h5 className="font-medium text-gray-900 dark:text-white">Experience</h5>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600 dark:text-gray-400">Current</span>
                <span className="font-medium">{analysis.experience_gap.current} years</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600 dark:text-gray-400">Required</span>
                <span className="font-medium">{analysis.experience_gap.required} years</span>
              </div>
              {analysis.experience_gap.gap > 0 && (
                <div className="mt-2 text-xs text-warning-600">
                  Gap: {analysis.experience_gap.gap} years
                </div>
              )}
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg"
          >
            <div className="flex items-center space-x-2 mb-3">
              <AcademicCapIcon className="h-5 w-5 text-primary-500" />
              <h5 className="font-medium text-gray-900 dark:text-white">Education</h5>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600 dark:text-gray-400">Current</span>
                <span className="font-medium capitalize">{analysis.education_gap.current}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600 dark:text-gray-400">Required</span>
                <span className="font-medium capitalize">{analysis.education_gap.required}</span>
              </div>
              {analysis.education_gap.gap > 0 && (
                <div className="mt-2 text-xs text-warning-600">
                  Education gap detected
                </div>
              )}
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg"
          >
            <div className="flex items-center space-x-2 mb-3">
              <CodeBracketIcon className="h-5 w-5 text-primary-500" />
              <h5 className="font-medium text-gray-900 dark:text-white">Projects</h5>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600 dark:text-gray-400">Current</span>
                <span className="font-medium">{analysis.project_gap.current} projects</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600 dark:text-gray-400">Required</span>
                <span className="font-medium">{analysis.project_gap.required} projects</span>
              </div>
              {analysis.project_gap.gap > 0 && (
                <div className="mt-2 text-xs text-warning-600">
                  Need {analysis.project_gap.gap} more projects
                </div>
              )}
            </div>
          </motion.div>
        </div>

        {/* Timeline & Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="bg-primary-50 dark:bg-primary-900/20 p-4 rounded-lg"
        >
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-2">
              <ClockIcon className="h-5 w-5 text-primary-600" />
              <h4 className="font-medium text-primary-900 dark:text-primary-100">
                Preparation Timeline
              </h4>
            </div>
            <Badge variant="primary">
              {analysis.estimated_preparation_time} days
            </Badge>
          </div>
          <p className="text-sm text-primary-700 dark:text-primary-300 mb-4">
            Recommended interview date:{' '}
            <span className="font-medium">
              {new Date(analysis.recommended_interview_date).toLocaleDateString('en-US', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric',
              })}
            </span>
          </p>
          <Button onClick={onGenerateRoadmap} className="w-full">
            Generate Learning Roadmap
          </Button>
        </motion.div>
      </CardContent>
    </Card>
  )
}