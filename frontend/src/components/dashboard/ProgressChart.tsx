'use client'

import { useEffect, useRef, useState } from 'react'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js'
import { Line } from 'react-chartjs-2'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card/Card'
import { Select } from '@/components/ui/select/Select'
import { Button } from '@/components/ui/button/Button'
import { ArrowPathIcon } from '@heroicons/react/24/outline'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

interface ProgressChartProps {
  data: {
    dates: string[]
    accuracy: number[]
    volume: number[]
    timeSpent: number[]
  }
  isLoading?: boolean
  onRefresh?: () => void
  timeframe?: string
  onTimeframeChange?: (timeframe: string) => void
}

export const ProgressChart = ({
  data,
  isLoading = false,
  onRefresh,
  timeframe = '30',
  onTimeframeChange,
}: ProgressChartProps) => {
  const chartRef = useRef<ChartJS<'line'> | null>(null)
  const [selectedMetric, setSelectedMetric] = useState<'accuracy' | 'volume' | 'time'>('accuracy')

  const timeframeOptions = [
    { value: '7', label: 'Last 7 days' },
    { value: '14', label: 'Last 14 days' },
    { value: '30', label: 'Last 30 days' },
    { value: '90', label: 'Last 90 days' },
  ]

  const getChartData = () => {
    let chartData: number[] = []
    let label = ''
    let color = ''

    switch (selectedMetric) {
      case 'accuracy':
        chartData = data.accuracy
        label = 'Accuracy (%)'
        color = 'rgb(59, 130, 246)'
        break
      case 'volume':
        chartData = data.volume
        label = 'Questions Attempted'
        color = 'rgb(34, 197, 94)'
        break
      case 'time':
        chartData = data.timeSpent
        label = 'Time Spent (minutes)'
        color = 'rgb(234, 179, 8)'
        break
    }

    return {
      labels: data.dates.map(date => new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })),
      datasets: [
        {
          label,
          data: chartData,
          borderColor: color,
          backgroundColor: `${color}20`,
          fill: true,
          tension: 0.4,
          pointRadius: 4,
          pointHoverRadius: 6,
          pointBackgroundColor: color,
          pointBorderColor: 'white',
          pointBorderWidth: 2,
        },
      ],
    }
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        mode: 'index' as const,
        intersect: false,
        backgroundColor: 'rgba(17, 24, 39, 0.9)',
        titleColor: 'rgb(243, 244, 246)',
        bodyColor: 'rgb(209, 213, 219)',
        borderColor: 'rgb(75, 85, 99)',
        borderWidth: 1,
        padding: 12,
        bodySpacing: 8,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(156, 163, 175, 0.1)',
        },
        ticks: {
          color: 'rgb(107, 114, 128)',
        },
      },
      x: {
        grid: {
          display: false,
        },
        ticks: {
          color: 'rgb(107, 114, 128)',
          maxRotation: 45,
          minRotation: 45,
        },
      },
    },
    interaction: {
      mode: 'nearest' as const,
      axis: 'x' as const,
      intersect: false,
    },
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
          <div className="h-[400px] animate-pulse bg-gray-100 dark:bg-gray-800 rounded-lg"></div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle>Performance Trends</CardTitle>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Track your progress over time
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2 bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
            {['accuracy', 'volume', 'time'].map((metric) => (
              <button
                key={metric}
                onClick={() => setSelectedMetric(metric as any)}
                className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
                  selectedMetric === metric
                    ? 'bg-white dark:bg-gray-900 text-primary-600 dark:text-primary-400 shadow-sm'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
                }`}
              >
                {metric.charAt(0).toUpperCase() + metric.slice(1)}
              </button>
            ))}
          </div>
          <Select
            value={timeframe}
            onChange={(e) => onTimeframeChange?.(e.target.value)}
            options={timeframeOptions}
            className="w-40"
          />
          {onRefresh && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onRefresh}
              className="p-2"
            >
              <ArrowPathIcon className="h-4 w-4" />
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <div className="h-[400px]">
          <Line ref={chartRef} data={getChartData()} options={options} />
        </div>
      </CardContent>
    </Card>
  )
}
