'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/hooks/useAuth'
import { useRouter } from 'next/navigation'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card/Card'
import { Button } from '@/components/ui/button/Button'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs/Tabs'
import { StatsCard } from '@/components/dashboard/StatsCard'
import {
  UsersIcon,
  DocumentTextIcon,
  QuestionMarkCircleIcon,
  CurrencyDollarIcon,
  ChartBarIcon,
  Cog6ToothIcon,
} from '@heroicons/react/24/outline'

export default function AdminPage() {
  const router = useRouter()
  const { user, isAuthenticated } = useAuth()
  const [isLoading, setIsLoading] = useState(true)
  const [stats, setStats] = useState<any>(null)

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login')
    } else if (user?.role !== 'admin') {
      router.push('/dashboard')
    } else {
      fetchAdminStats()
    }
  }, [isAuthenticated, user, router])

  const fetchAdminStats = async () => {
    setIsLoading(true)
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000))
      setStats({
        totalUsers: 15420,
        activeUsers: 8234,
        totalQuestions: 3240,
        totalAttempts: 456789,
        revenue: 125000,
        growth: 23.5,
      })
    } finally {
      setIsLoading(false)
    }
  }

  if (!user || user.role !== 'admin') {
    return null
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Admin Dashboard</h1>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Platform management and analytics
          </p>
        </div>
        <Button variant="outline" onClick={fetchAdminStats}>
          <ChartBarIcon className="h-4 w-4 mr-2" />
          Refresh Data
        </Button>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <StatsCard
          title="Total Users"
          value={stats?.totalUsers || 0}
          icon={<UsersIcon className="h-6 w-6" />}
          trend={{ value: 12, label: 'vs last month', positive: true }}
          color="primary"
          isLoading={isLoading}
        />
        <StatsCard
          title="Active Users"
          value={stats?.activeUsers || 0}
          icon={<UsersIcon className="h-6 w-6" />}
          trend={{ value: 8, label: 'vs last month', positive: true }}
          color="success"
          isLoading={isLoading}
        />
        <StatsCard
          title="Total Questions"
          value={stats?.totalQuestions || 0}
          icon={<QuestionMarkCircleIcon className="h-6 w-6" />}
          trend={{ value: 15, label: 'new this month', positive: true }}
          color="warning"
          isLoading={isLoading}
        />
        <StatsCard
          title="Total Attempts"
          value={stats?.totalAttempts?.toLocaleString() || 0}
          icon={<DocumentTextIcon className="h-6 w-6" />}
          trend={{ value: 23, label: 'vs last month', positive: true }}
          color="info"
          isLoading={isLoading}
        />
        <StatsCard
          title="Revenue"
          value={`$${(stats?.revenue || 0).toLocaleString()}`}
          icon={<CurrencyDollarIcon className="h-6 w-6" />}
          trend={{ value: 18, label: 'vs last month', positive: true }}
          color="success"
          isLoading={isLoading}
        />
        <StatsCard
          title="Growth Rate"
          value={`${stats?.growth || 0}%`}
          icon={<ChartBarIcon className="h-6 w-6" />}
          trend={{ value: 5, label: 'acceleration', positive: true }}
          color="primary"
          isLoading={isLoading}
        />
      </div>

      {/* Management Tabs */}
      <Tabs defaultValue="users">
        <TabsList>
          <TabsTrigger value="users">Users</TabsTrigger>
          <TabsTrigger value="questions">Questions</TabsTrigger>
          <TabsTrigger value="content">Content</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </TabsList>

        <TabsContent value="users" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>User Management</CardTitle>
              <CardDescription>
                Manage platform users and their roles
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600 dark:text-gray-400">
                User management interface would go here
              </p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="questions" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Question Management</CardTitle>
              <CardDescription>
                Add, edit, and manage interview questions
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600 dark:text-gray-400">
                Question management interface would go here
              </p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="content" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Content Management</CardTitle>
              <CardDescription>
                Manage platform content and resources
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600 dark:text-gray-400">
                Content management interface would go here
              </p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="analytics" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Platform Analytics</CardTitle>
              <CardDescription>
                Detailed platform usage analytics
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600 dark:text-gray-400">
                Analytics dashboard would go here
              </p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="settings" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Platform Settings</CardTitle>
              <CardDescription>
                Configure platform-wide settings
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600 dark:text-gray-400">
                Platform settings interface would go here
              </p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}