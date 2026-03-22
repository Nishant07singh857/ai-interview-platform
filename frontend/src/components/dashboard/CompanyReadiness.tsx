'use client'

import { motion } from 'framer-motion'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card/Card'
import { Progress } from '@/components/ui/progress/Progress'
import { Badge } from '@/components/ui/badge/Badge'
import { CompanyReadiness as CompanyReadinessType } from '@/types'
import { 
  BuildingOfficeIcon,
  ArrowTrendingUpIcon,
  ExclamationTriangleIcon 
} from '@heroicons/react/24/outline'

interface CompanyReadinessProps {
  companies: CompanyReadinessType[]
  isLoading?: boolean
  onCompanyClick?: (company: string) => void
}

const readinessColors = {
  not_ready: 'error',
  almost_ready: 'warning',
  ready: 'primary',
  highly_ready: 'success',
} as const

const readinessLabels = {
  not_ready: 'Not Ready',
  almost_ready: 'Almost Ready',
  ready: 'Ready',
  highly_ready: 'Highly Ready',
} as const

export const CompanyReadiness = ({
  companies,
  isLoading = false,
  onCompanyClick,
}: CompanyReadinessProps) => {
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
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="animate-pulse">
                <div className="flex justify-between mb-2">
                  <div className="h-5 w-32 bg-gray-200 dark:bg-gray-700 rounded"></div>
                  <div className="h-5 w-16 bg-gray-200 dark:bg-gray-700 rounded"></div>
                </div>
                <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded mb-2"></div>
                <div className="grid grid-cols-3 gap-2">
                  {[1, 2, 3].map((j) => (
                    <div key={j} className="h-4 bg-gray-200 dark:bg-gray-700 rounded"></div>
                  ))}
                </div>
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
        <CardTitle>Company Readiness</CardTitle>
        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
          Your preparedness for top tech companies
        </p>
      </CardHeader>

      <CardContent>
        <div className="space-y-6">
          {companies.map((company, index) => {
            const readinessLevel = company.readinessLevel
            const displayName = company.company
            const overallScore = company.overallScore
            const gaps = company.criticalGaps || []

            return (
              <motion.div
              key={displayName}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="group cursor-pointer"
              onClick={() => onCompanyClick?.(displayName)}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-3">
                  {company.logo ? (
                    <img
                      src={company.logo}
                      alt={displayName}
                      className="w-8 h-8 rounded-full object-contain bg-white p-1"
                    />
                  ) : (
                    <div className="w-8 h-8 rounded-full bg-primary-100 dark:bg-primary-900/20 flex items-center justify-center">
                      <BuildingOfficeIcon className="h-4 w-4 text-primary-600 dark:text-primary-400" />
                    </div>
                  )}
                  <div>
                    <h4 className="text-base font-semibold text-gray-900 dark:text-white">
                      {displayName}
                    </h4>
                    <p className="text-xs text-gray-500 dark:text-gray-500">
                      Target company
                    </p>
                  </div>
                </div>
                <Badge variant={readinessColors[readinessLevel]}>
                  {readinessLabels[readinessLevel]}
                </Badge>
              </div>

              <div className="space-y-2 mb-3">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600 dark:text-gray-400">Overall</span>
                  <span className="font-medium text-gray-900 dark:text-white">
                    {overallScore}%
                  </span>
                </div>
                <Progress value={overallScore} variant={readinessColors[readinessLevel]} />
              </div>

              <div className="grid grid-cols-3 gap-2 mb-3">
                <div>
                  <div className="text-xs text-gray-500 dark:text-gray-500 mb-1">Technical</div>
                  <div className="flex items-center">
                    <div className="flex-1 h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-primary-500"
                        style={{ width: `${company.technicalScore}%` }}
                      />
                    </div>
                    <span className="ml-2 text-xs font-medium text-gray-700 dark:text-gray-300">
                      {company.technicalScore}%
                    </span>
                  </div>
                </div>
                <div>
                  <div className="text-xs text-gray-500 dark:text-gray-500 mb-1">Behavioral</div>
                  <div className="flex items-center">
                    <div className="flex-1 h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-success-500"
                        style={{ width: `${company.behavioralScore}%` }}
                      />
                    </div>
                    <span className="ml-2 text-xs font-medium text-gray-700 dark:text-gray-300">
                      {company.behavioralScore}%
                    </span>
                  </div>
                </div>
                <div>
                  <div className="text-xs text-gray-500 dark:text-gray-500 mb-1">System Design</div>
                  <div className="flex items-center">
                    <div className="flex-1 h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-warning-500"
                        style={{ width: `${company.systemDesignScore}%` }}
                      />
                    </div>
                    <span className="ml-2 text-xs font-medium text-gray-700 dark:text-gray-300">
                      {company.systemDesignScore}%
                    </span>
                  </div>
                </div>
              </div>

              {gaps.length > 0 && (
                <div className="flex items-start space-x-2 text-xs text-warning-600 dark:text-warning-400 bg-warning-50 dark:bg-warning-900/20 p-2 rounded">
                  <ExclamationTriangleIcon className="h-4 w-4 flex-shrink-0 mt-0.5" />
                  <div>
                    <span className="font-medium">Critical gaps: </span>
                    {gaps.join(', ')}
                  </div>
                </div>
              )}

              <div className="mt-3 flex items-center text-sm text-primary-600 dark:text-primary-400 opacity-0 group-hover:opacity-100 transition-opacity">
                <span>View preparation plan</span>
                <ArrowTrendingUpIcon className="h-4 w-4 ml-1" />
              </div>

              {index < companies.length - 1 && (
                <div className="mt-4 border-t border-gray-200 dark:border-gray-700" />
              )}
            </motion.div>
            )
          })}
        </div>
      </CardContent>
    </Card>
  )
}
