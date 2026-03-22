'use client'

import { useEffect, useState } from 'react'
import { useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { useAuth } from '@/hooks/useAuth'
import { Card, CardContent } from '@/components/ui/card/Card'
import { Button } from '@/components/ui/button/Button'
import { Spinner } from '@/components/ui/spinner/Spinner'
import { CheckCircleIcon, XCircleIcon } from '@heroicons/react/24/outline'

export const VerifyEmail = () => {
  const searchParams = useSearchParams()
  const token = searchParams.get('token')
  const { verifyEmail, isLoading } = useAuth()
  
  const [status, setStatus] = useState<'verifying' | 'success' | 'error'>('verifying')
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!token) {
      setStatus('error')
      setError('No verification token provided')
      return
    }

    const verify = async () => {
      try {
        await verifyEmail(token)
        setStatus('success')
      } catch (err: any) {
        setStatus('error')
        setError(err.message || 'Email verification failed')
      }
    }

    verify()
  }, [token, verifyEmail])

  if (status === 'verifying') {
    return (
      <Card className="w-full max-w-md mx-auto">
        <CardContent className="pt-6">
          <div className="text-center">
            <Spinner size="lg" className="mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
              Verifying your email
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Please wait while we verify your email address...
            </p>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (status === 'success') {
    return (
      <Card className="w-full max-w-md mx-auto">
        <CardContent className="pt-6">
          <div className="text-center">
            <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-success-100 dark:bg-success-900/20 mb-4">
              <CheckCircleIcon className="h-6 w-6 text-success-600 dark:text-success-400" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
              Email Verified Successfully!
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-6">
              Your email has been verified. You can now access all features of the platform.
            </p>
            <Link href="/dashboard">
              <Button className="w-full">Go to Dashboard</Button>
            </Link>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="w-full max-w-md mx-auto">
      <CardContent className="pt-6">
        <div className="text-center">
          <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-error-100 dark:bg-error-900/20 mb-4">
            <XCircleIcon className="h-6 w-6 text-error-600 dark:text-error-400" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
            Verification Failed
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
            {error || 'Unable to verify your email. The link may have expired.'}
          </p>
          <div className="space-y-3">
            <Link href="/resend-verification">
              <Button variant="outline" className="w-full">
                Resend Verification Email
              </Button>
            </Link>
            <Link href="/login">
              <Button variant="ghost" className="w-full">
                Back to Login
              </Button>
            </Link>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}