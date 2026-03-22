'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card/Card'
import { Button } from '@/components/ui/button/Button'
import { Badge } from '@/components/ui/badge/Badge'
import { usePractice } from '@/hooks/usePractice'
import {
  BuildingOfficeIcon,
  BriefcaseIcon,
  ChartBarIcon,
  ArrowRightIcon,
} from '@heroicons/react/24/outline'

const companies = [
  {
    name: 'Google',
    description: 'Practice questions commonly asked at Google interviews',
    roles: ['ML Engineer', 'Data Scientist', 'Software Engineer', 'Research Scientist'],
    difficulty: 'Hard',
    questions: 250,
    topics: ['Algorithms', 'System Design', 'Machine Learning', 'Python'],
    icon: '🔍',
  },
  {
    name: 'Amazon',
    description: 'Amazon interview questions focusing on leadership principles',
    roles: ['Applied Scientist', 'Data Scientist', 'ML Engineer', 'SDE'],
    difficulty: 'Hard',
    questions: 320,
    topics: ['Leadership', 'System Design', 'AWS', 'Scalability'],
    icon: '📦',
  },
  {
    name: 'Microsoft',
    description: 'Microsoft interview preparation with Azure focus',
    roles: ['Data Scientist', 'ML Engineer', 'Software Engineer', 'Researcher'],
    difficulty: 'Hard',
    questions: 280,
    topics: ['Algorithms', 'C#', 'Azure', 'System Design'],
    icon: '🪟',
  },
  {
    name: 'Meta',
    description: 'Meta (Facebook) interview questions for ML and engineering roles',
    roles: ['Data Scientist', 'ML Engineer', 'Research Scientist', 'Software Engineer'],
    difficulty: 'Hard',
    questions: 230,
    topics: ['Product Sense', 'System Design', 'Python', 'Hack'],
    icon: '📱',
  },
  {
    name: 'Apple',
    description: 'Apple interview preparation with hardware/software integration',
    roles: ['ML Engineer', 'Data Scientist', 'AI Researcher', 'Software Engineer'],
    difficulty: 'Hard',
    questions: 180,
    topics: ['Swift', 'Privacy', 'System Design', 'Computer Vision'],
    icon: '🍎',
  },
  {
    name: 'Netflix',
    description: 'Netflix interview questions focusing on streaming and recommendations',
    roles: ['Data Scientist', 'ML Engineer', 'Research Scientist', 'Software Engineer'],
    difficulty: 'Expert',
    questions: 150,
    topics: ['Recommendation Systems', 'Microservices', 'Chaos Engineering', 'AWS'],
    icon: '🎬',
  },
  {
    name: 'Uber',
    description: 'Uber interview preparation for engineering roles',
    roles: ['Data Scientist', 'ML Engineer', 'Software Engineer', 'Research Scientist'],
    difficulty: 'Hard',
    questions: 160,
    topics: ['Real-time Systems', 'Maps', 'Distributed Systems', 'Python'],
    icon: '🚗',
  },
  {
    name: 'Airbnb',
    description: 'Airbnb interview questions for data and engineering roles',
    roles: ['Data Scientist', 'ML Engineer', 'Software Engineer', 'Product Analyst'],
    difficulty: 'Medium',
    questions: 140,
    topics: ['Product Analytics', 'Search', 'Recommendations', 'Python'],
    icon: '🏠',
  },
]

export default function CompanyGridPage() {
  const router = useRouter()
  const { startCompanyPractice, isLoading } = usePractice()
  const [selectedCompany, setSelectedCompany] = useState<string | null>(null)

  const handleStartPractice = async (company: string) => {
    try {
      const session = await startCompanyPractice({
        company,
        totalQuestions: 20,
      })
      if (session?.sessionId) {
        router.push(`/practice/session/${session.sessionId}`)
      }
    } catch (error) {
      console.error('Failed to start practice:', error)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Company Grid</h1>
        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
          Practice questions tailored to specific companies
        </p>
      </div>

      {/* Company Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {companies.map((company, index) => (
          <motion.div
            key={company.name}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <Card className="group cursor-pointer hover:shadow-lg transition-all h-full flex flex-col">
              <CardContent className="p-6 flex-1">
                <div className="flex items-start justify-between mb-4">
                  <div className="text-4xl">{company.icon}</div>
                  <Badge variant={company.difficulty === 'Expert' ? 'error' : 'warning'}>
                    {company.difficulty}
                  </Badge>
                </div>

                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                  {company.name}
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                  {company.description}
                </p>

                <div className="space-y-3 mb-4">
                  <div>
                    <span className="text-xs font-medium text-gray-500 uppercase">Roles</span>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {company.roles.slice(0, 3).map((role) => (
                        <Badge key={role} variant="secondary" size="sm">
                          {role}
                        </Badge>
                      ))}
                      {company.roles.length > 3 && (
                        <Badge variant="secondary" size="sm">
                          +{company.roles.length - 3}
                        </Badge>
                      )}
                    </div>
                  </div>

                  <div>
                    <span className="text-xs font-medium text-gray-500 uppercase">Topics</span>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {company.topics.slice(0, 3).map((topic) => (
                        <Badge key={topic} variant="outline" size="sm">
                          {topic}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
                  <span>{company.questions} questions</span>
                </div>

                <Button
                  onClick={() => handleStartPractice(company.name)}
                  disabled={isLoading}
                  className="w-full"
                >
                  Start Practice
                  <ArrowRightIcon className="h-4 w-4 ml-2" />
                </Button>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>
    </div>
  )
}
