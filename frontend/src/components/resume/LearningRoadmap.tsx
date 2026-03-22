'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card/Card'
import { Button } from '@/components/ui/button/Button'
import { Badge } from '@/components/ui/badge/Badge'
import { Progress } from '@/components/ui/progress/Progress'
import {
  CalendarIcon,
  CheckCircleIcon,
  ClockIcon,
  BookOpenIcon,
  PlayCircleIcon,
  DocumentTextIcon,
  ChevronDownIcon,
  ChevronUpIcon,
} from '@heroicons/react/24/outline'

interface LearningRoadmapProps {
  roadmap: {
    roadmap_id: string
    target_company: string
    target_role: string
    created_at: string
    target_interview_date: string
    total_days: number
    overall_progress: number
    milestones: Array<{
      milestone_id: string
      title: string
      description: string
      category: string
      target_date: string
      completed: boolean
      completed_at?: string
      progress: number
      tasks: Array<{
        name: string
        completed: boolean
      }>
      resources: Array<{
        type: string
        name: string
        url?: string
      }>
    }>
    weekly_plan: Array<{
      week: number
      start_date: string
      end_date: string
      focus_areas: Array<{
        topic: string
        hours: number
        focus: string
      }>
      total_hours: number
    }>
    recommended_courses: Array<{
      name: string
      platform: string
      url: string
      duration_hours: number
    }>
    recommended_practice: Array<{
      name: string
      platform: string
      count: number
      type: string
    }>
  }
  onUpdateMilestone?: (milestoneId: string, completed: boolean) => void
  isLoading?: boolean
}

export const LearningRoadmap = ({
  roadmap,
  onUpdateMilestone,
  isLoading = false,
}: LearningRoadmapProps) => {
  const [expandedMilestones, setExpandedMilestones] = useState<string[]>([])
  const [showAllCourses, setShowAllCourses] = useState(false)
  const [showAllPractice, setShowAllPractice] = useState(false)

  const toggleMilestone = (milestoneId: string) => {
    setExpandedMilestones(prev =>
      prev.includes(milestoneId)
        ? prev.filter(id => id !== milestoneId)
        : [...prev, milestoneId]
    )
  }

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'skill': return <BookOpenIcon className="h-5 w-5" />
      case 'project': return <DocumentTextIcon className="h-5 w-5" />
      case 'interview': return <PlayCircleIcon className="h-5 w-5" />
      default: return <CheckCircleIcon className="h-5 w-5" />
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
            {[1, 2, 3].map((i) => (
              <div key={i} className="space-y-3">
                <div className="h-5 w-32 bg-gray-200 dark:bg-gray-700 rounded"></div>
                <div className="h-20 bg-gray-200 dark:bg-gray-700 rounded"></div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  const completedMilestones = roadmap.milestones.filter(m => m.completed).length
  const totalMilestones = roadmap.milestones.length

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Learning Roadmap: {roadmap.target_company}</CardTitle>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              {roadmap.target_role} - Created on{' '}
              {new Date(roadmap.created_at).toLocaleDateString()}
            </p>
          </div>
          <Badge variant="primary" size="lg">
            {roadmap.overall_progress}% Complete
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-8">
        {/* Progress Overview */}
        <div className="bg-gradient-to-r from-primary-50 to-primary-100 dark:from-primary-900/20 dark:to-primary-800/20 p-6 rounded-lg">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Your Journey to {roadmap.target_company}
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                Target interview date:{' '}
                {new Date(roadmap.target_interview_date).toLocaleDateString('en-US', {
                  weekday: 'long',
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                })}
              </p>
            </div>
            <div className="text-right">
              <div className="text-3xl font-bold text-primary-600 dark:text-primary-400">
                {roadmap.total_days}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">days total</div>
            </div>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Progress</span>
              <span>{completedMilestones}/{totalMilestones} milestones</span>
            </div>
            <Progress value={roadmap.overall_progress} variant="primary" size="lg" />
          </div>
        </div>

        {/* Milestones */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Milestones</h3>
          <div className="space-y-3">
            {roadmap.milestones.map((milestone, index) => (
              <motion.div
                key={milestone.milestone_id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden"
              >
                <div
                  className={`p-4 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors ${
                    milestone.completed ? 'bg-success-50 dark:bg-success-900/20' : ''
                  }`}
                  onClick={() => toggleMilestone(milestone.milestone_id)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3 flex-1">
                      <div className={`p-2 rounded-lg ${
                        milestone.completed
                          ? 'bg-success-100 dark:bg-success-900'
                          : 'bg-gray-100 dark:bg-gray-800'
                      }`}>
                        {getCategoryIcon(milestone.category)}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <h4 className="font-medium text-gray-900 dark:text-white">
                            {milestone.title}
                          </h4>
                          {milestone.completed && (
                            <Badge variant="success" size="sm">Completed</Badge>
                          )}
                        </div>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {milestone.description}
                        </p>
                        <div className="flex items-center space-x-4 mt-2 text-xs">
                          <span className="flex items-center text-gray-500">
                            <CalendarIcon className="h-3 w-3 mr-1" />
                            Due: {new Date(milestone.target_date).toLocaleDateString()}
                          </span>
                          <span className="flex items-center text-gray-500">
                            <ClockIcon className="h-3 w-3 mr-1" />
                            {milestone.progress}% complete
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-3">
                      <Button
                        size="sm"
                        variant={milestone.completed ? 'outline' : 'primary'}
                        onClick={(e) => {
                          e.stopPropagation()
                          onUpdateMilestone?.(milestone.milestone_id, !milestone.completed)
                        }}
                      >
                        {milestone.completed ? 'Undo' : 'Mark Complete'}
                      </Button>
                      {expandedMilestones.includes(milestone.milestone_id) ? (
                        <ChevronUpIcon className="h-5 w-5 text-gray-400" />
                      ) : (
                        <ChevronDownIcon className="h-5 w-5 text-gray-400" />
                      )}
                    </div>
                  </div>
                </div>

                <AnimatePresence>
                  {expandedMilestones.includes(milestone.milestone_id) && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                      className="border-t border-gray-200 dark:border-gray-700"
                    >
                      <div className="p-4 bg-gray-50 dark:bg-gray-800/50 space-y-4">
                        {/* Tasks */}
                        <div className="space-y-2">
                          <h5 className="text-sm font-medium text-gray-700 dark:text-gray-300">
                            Tasks
                          </h5>
                          <ul className="space-y-2">
                            {milestone.tasks.map((task, i) => (
                              <li key={i} className="flex items-center space-x-2">
                                <input
                                  type="checkbox"
                                  checked={task.completed}
                                  onChange={() => {}}
                                  className="rounded border-gray-300 text-primary focus:ring-primary"
                                />
                                <span className={`text-sm ${
                                  task.completed
                                    ? 'text-gray-500 line-through'
                                    : 'text-gray-700 dark:text-gray-300'
                                }`}>
                                  {task.name}
                                </span>
                              </li>
                            ))}
                          </ul>
                        </div>

                        {/* Resources */}
                        {milestone.resources.length > 0 && (
                          <div className="space-y-2">
                            <h5 className="text-sm font-medium text-gray-700 dark:text-gray-300">
                              Resources
                            </h5>
                            <div className="flex flex-wrap gap-2">
                              {milestone.resources.map((resource, i) => (
                                <a
                                  key={i}
                                  href={resource.url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="inline-flex items-center space-x-1 px-3 py-1 bg-white dark:bg-gray-800 rounded-full text-xs border border-gray-200 dark:border-gray-700 hover:border-primary-300 transition-colors"
                                >
                                  <span className="capitalize">{resource.type}:</span>
                                  <span className="font-medium">{resource.name}</span>
                                </a>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Weekly Plan */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Weekly Focus</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {roadmap.weekly_plan.map((week) => (
              <motion.div
                key={week.week}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: week.week * 0.05 }}
                className="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg"
              >
                <div className="flex items-center justify-between mb-3">
                  <Badge variant="outline">Week {week.week}</Badge>
                  <span className="text-xs text-gray-500">
                    {new Date(week.start_date).toLocaleDateString()} - {new Date(week.end_date).toLocaleDateString()}
                  </span>
                </div>
                <div className="space-y-2">
                  {week.focus_areas.map((area, i) => (
                    <div key={i} className="flex items-center justify-between text-sm">
                      <span className="text-gray-700 dark:text-gray-300">{area.topic}</span>
                      <span className="text-gray-500">{area.hours}h</span>
                    </div>
                  ))}
                </div>
                <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
                  <div className="flex items-center justify-between text-sm">
                    <span className="font-medium text-gray-700 dark:text-gray-300">Total hours</span>
                    <span className="text-primary-600 font-medium">{week.total_hours}h</span>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Recommended Resources */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Courses */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Recommended Courses</h3>
            <div className="space-y-2">
              {(showAllCourses ? roadmap.recommended_courses : roadmap.recommended_courses.slice(0, 3)).map((course, index) => (
                <a
                  key={index}
                  href={course.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-medium text-gray-900 dark:text-white">{course.name}</span>
                    <Badge variant="secondary" size="sm">{course.platform}</Badge>
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {course.duration_hours} hours
                  </p>
                </a>
              ))}
            </div>
            {roadmap.recommended_courses.length > 3 && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowAllCourses(!showAllCourses)}
                className="w-full"
              >
                {showAllCourses ? 'Show less' : `Show all (${roadmap.recommended_courses.length})`}
              </Button>
            )}
          </div>

          {/* Practice */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Practice Resources</h3>
            <div className="space-y-2">
              {(showAllPractice ? roadmap.recommended_practice : roadmap.recommended_practice.slice(0, 3)).map((practice, index) => (
                <div
                  key={index}
                  className="p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg"
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-medium text-gray-900 dark:text-white">{practice.name}</span>
                    <Badge variant="secondary" size="sm">{practice.platform}</Badge>
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {practice.count} {practice.type}
                  </p>
                </div>
              ))}
            </div>
            {roadmap.recommended_practice.length > 3 && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowAllPractice(!showAllPractice)}
                className="w-full"
              >
                {showAllPractice ? 'Show less' : `Show all (${roadmap.recommended_practice.length})`}
              </Button>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}