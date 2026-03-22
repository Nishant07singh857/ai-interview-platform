'use client'

import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card/Card'
import { Button } from '@/components/ui/button/Button'
import { Badge } from '@/components/ui/badge/Badge'
import {
  BoltIcon,
  AcademicCapIcon,
  ClipboardDocumentListIcon,
  BuildingOfficeIcon,
  ArrowRightIcon,
} from '@heroicons/react/24/outline'

const practiceModes = [
  {
    id: 'quick-quiz',
    title: 'Quick Quiz',
    description: '5 random questions to test your knowledge',
    icon: BoltIcon,
    color: 'yellow',
    time: '5 min',
    questions: 5,
    href: '/practice/quick-quiz',
  },
  {
    id: 'topic-wise',
    title: 'Topic Wise',
    description: 'Practice specific topics in depth',
    icon: AcademicCapIcon,
    color: 'blue',
    time: '10-30 min',
    questions: '10-30',
    href: '/practice/topic-wise',
  },
  {
    id: 'mock-test',
    title: 'Mock Tests',
    description: 'Full-length tests simulating real interviews',
    icon: ClipboardDocumentListIcon,
    color: 'purple',
    time: '30-90 min',
    questions: '30-60',
    href: '/practice/mock-test',
    pro: true,
  },
  {
    id: 'company-grid',
    title: 'Company Grid',
    description: 'Questions asked at top tech companies',
    icon: BuildingOfficeIcon,
    color: 'green',
    time: '20-45 min',
    questions: '15-30',
    href: '/practice/company-grid',
    pro: true,
  },
]

const subjects = [
  { name: 'Machine Learning', count: 1200, color: 'blue' },
  { name: 'Deep Learning', count: 800, color: 'purple' },
  { name: 'Data Science', count: 950, color: 'green' },
  { name: 'Data Analysis', count: 700, color: 'yellow' },
  { name: 'Artificial Intelligence', count: 600, color: 'red' },
]

export default function PracticePage() {
  const router = useRouter()

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Practice</h1>
        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
          Choose your practice mode and start preparing
        </p>
      </div>

      {/* Practice Modes */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {practiceModes.map((mode, index) => {
          const Icon = mode.icon
          return (
            <motion.div
              key={mode.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <Card className="group cursor-pointer hover:shadow-lg transition-all" onClick={() => router.push(mode.href)}>
                <CardContent className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className={`p-3 rounded-xl bg-${mode.color}-100 dark:bg-${mode.color}-900/20`}>
                      <Icon className={`h-6 w-6 text-${mode.color}-600 dark:text-${mode.color}-400`} />
                    </div>
                    {mode.pro && (
                      <Badge variant="primary">PRO</Badge>
                    )}
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                    {mode.title}
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                    {mode.description}
                  </p>
                  <div className="flex items-center justify-between text-sm">
                    <div className="flex items-center space-x-4">
                      <span className="text-gray-500">⏱️ {mode.time}</span>
                      <span className="text-gray-500">📝 {mode.questions} questions</span>
                    </div>
                    <ArrowRightIcon className="h-5 w-5 text-gray-400 group-hover:text-primary-500 transition-colors" />
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )
        })}
      </div>

      {/* Subjects Overview */}
      <div className="pt-8">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
          Available Subjects
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {subjects.map((subject) => (
            <Card key={subject.name} className="cursor-pointer hover:shadow-md transition-all">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-medium text-gray-900 dark:text-white">{subject.name}</h3>
                    <p className="text-sm text-gray-500">{subject.count} questions</p>
                  </div>
                  <Badge variant={subject.color as any}>{subject.count}+</Badge>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  )
}