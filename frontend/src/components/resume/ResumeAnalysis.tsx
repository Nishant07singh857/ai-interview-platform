'use client'

import { motion } from 'framer-motion'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card/Card'
import { Progress } from '@/components/ui/progress/Progress'
import { Badge } from '@/components/ui/badge/Badge'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs/Tabs'
import {
  ChartBarIcon,
  AcademicCapIcon,
  BriefcaseIcon,
  UserGroupIcon,
  LightBulbIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline'

interface ResumeAnalysisProps {
  analysis: {
    overall_score: number
    ats_score: number
    completeness_score: number
    strengths: string[]
    weaknesses: string[]
    gaps: Array<{
      type: string
      items: string[]
      severity: string
    }>
    immediate_actions: string[]
    short_term_goals: string[]
    target_readiness: Record<string, number>
  }
  isLoading?: boolean
}

export const ResumeAnalysis = ({ analysis, isLoading = false }: ResumeAnalysisProps) => {
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'success'
    if (score >= 60) return 'primary'
    if (score >= 40) return 'warning'
    return 'error'
  }

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <div className="animate-pulse">
            <div className="h-6 w-48 bg-gray-200 dark:bg-gray-700 rounded mb-2"></div>
            <div className="h-4 w-32 bg-gray-200 dark:bg-gray-700 rounded"></div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {[1, 2, 3].map((i) => (
              <div key={i} className="space-y-2">
                <div className="h-4 w-24 bg-gray-200 dark:bg-gray-700 rounded"></div>
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
        <CardTitle>Resume Analysis</CardTitle>
        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
          AI-powered insights and recommendations for your resume
        </p>
      </CardHeader>

      <CardContent>
        <Tabs defaultValue="overview" className="space-y-4">
          <TabsList>
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="gaps">Gap Analysis</TabsTrigger>
            <TabsTrigger value="actions">Actions</TabsTrigger>
            <TabsTrigger value="readiness">Target Readiness</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            {/* Score Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg"
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Overall Score</span>
                  <ChartBarIcon className="h-5 w-5 text-primary-500" />
                </div>
                <div className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                  {analysis.overall_score}%
                </div>
                <Progress value={analysis.overall_score} variant={getScoreColor(analysis.overall_score)} />
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg"
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-600 dark:text-gray-400">ATS Score</span>
                  <AcademicCapIcon className="h-5 w-5 text-primary-500" />
                </div>
                <div className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                  {analysis.ats_score}%
                </div>
                <Progress value={analysis.ats_score} variant={getScoreColor(analysis.ats_score)} />
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg"
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Completeness</span>
                  <BriefcaseIcon className="h-5 w-5 text-primary-500" />
                </div>
                <div className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                  {analysis.completeness_score}%
                </div>
                <Progress value={analysis.completeness_score} variant={getScoreColor(analysis.completeness_score)} />
              </motion.div>
            </div>

            {/* Strengths & Weaknesses */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-3">
                <h4 className="font-medium text-gray-900 dark:text-white flex items-center">
                  <LightBulbIcon className="h-5 w-5 text-success-500 mr-2" />
                  Strengths
                </h4>
                <ul className="space-y-2">
                  {analysis.strengths.map((strength, index) => (
                    <motion.li
                      key={index}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="flex items-start space-x-2 text-sm text-gray-700 dark:text-gray-300"
                    >
                      <span className="text-success-500 mt-0.5">✓</span>
                      <span>{strength}</span>
                    </motion.li>
                  ))}
                </ul>
              </div>

              <div className="space-y-3">
                <h4 className="font-medium text-gray-900 dark:text-white flex items-center">
                  <ExclamationTriangleIcon className="h-5 w-5 text-warning-500 mr-2" />
                  Areas to Improve
                </h4>
                <ul className="space-y-2">
                  {analysis.weaknesses.map((weakness, index) => (
                    <motion.li
                      key={index}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="flex items-start space-x-2 text-sm text-gray-700 dark:text-gray-300"
                    >
                      <span className="text-warning-500 mt-0.5">•</span>
                      <span>{weakness}</span>
                    </motion.li>
                  ))}
                </ul>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="gaps" className="space-y-4">
            {analysis.gaps.map((gap, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className={`p-4 rounded-lg border ${
                  gap.severity === 'high'
                    ? 'border-error-200 bg-error-50 dark:border-error-800 dark:bg-error-900/20'
                    : gap.severity === 'medium'
                    ? 'border-warning-200 bg-warning-50 dark:border-warning-800 dark:bg-warning-900/20'
                    : 'border-primary-200 bg-primary-50 dark:border-primary-800 dark:bg-primary-900/20'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium capitalize">{gap.type} Gap</h4>
                  <Badge
                    variant={
                      gap.severity === 'high'
                        ? 'error'
                        : gap.severity === 'medium'
                        ? 'warning'
                        : 'primary'
                    }
                  >
                    {gap.severity} priority
                  </Badge>
                </div>
                <div className="flex flex-wrap gap-2">
                  {gap.items.map((item, i) => (
                    <Badge key={i} variant="secondary">
                      {item}
                    </Badge>
                  ))}
                </div>
              </motion.div>
            ))}
          </TabsContent>

          <TabsContent value="actions" className="space-y-4">
            <div className="space-y-3">
              <h4 className="font-medium text-gray-900 dark:text-white">Immediate Actions</h4>
              <ul className="space-y-2">
                {analysis.immediate_actions.map((action, index) => (
                  <motion.li
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-start space-x-2 p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg"
                  >
                    <span className="text-primary-500 font-medium">{index + 1}.</span>
                    <span className="text-sm text-gray-700 dark:text-gray-300">{action}</span>
                  </motion.li>
                ))}
              </ul>
            </div>

            <div className="space-y-3">
              <h4 className="font-medium text-gray-900 dark:text-white">Short-term Goals</h4>
              <ul className="space-y-2">
                {analysis.short_term_goals.map((goal, index) => (
                  <motion.li
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-start space-x-2 p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg"
                  >
                    <span className="text-primary-500 font-medium">{index + 1}.</span>
                    <span className="text-sm text-gray-700 dark:text-gray-300">{goal}</span>
                  </motion.li>
                ))}
              </ul>
            </div>
          </TabsContent>

          <TabsContent value="readiness" className="space-y-4">
            {Object.entries(analysis.target_readiness).map(([company, score], index) => (
              <motion.div
                key={company}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="space-y-2"
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium text-gray-900 dark:text-white">{company}</span>
                  <Badge variant={getScoreColor(score)}>{score}% ready</Badge>
                </div>
                <Progress value={score} variant={getScoreColor(score)} />
              </motion.div>
            ))}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}
