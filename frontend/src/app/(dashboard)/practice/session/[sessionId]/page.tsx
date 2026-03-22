'use client'

import { useEffect, useRef, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { usePractice } from '@/hooks/usePractice'
import { PracticeSession } from '@/components/practice/PracticeSession'
import { Spinner } from '@/components/ui/spinner/Spinner'

export default function PracticeSessionPage() {
  const params = useParams()
  const router = useRouter()
  const { loadSession, currentSession, isLoading } = usePractice()
  const [loading, setLoading] = useState(true)
  const hasLoadedRef = useRef(false)

  useEffect(() => {
    const pathSegments = window.location.pathname.split('/')
    const urlSessionId = pathSegments[pathSegments.length - 1]
    
    const sessionId = params?.sessionId as string || urlSessionId
    
    if (!sessionId || sessionId === 'undefined' || sessionId === 'null') {
      return
    }

    if (hasLoadedRef.current) {
      return
    }
    hasLoadedRef.current = true

    const loadData = async () => {
      try {
        await loadSession(sessionId)
        setLoading(false)
      } catch (error) {
        router.push('/practice')
      }
    }

    loadData()
  }, [params, loadSession, router])

  if (loading || isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Spinner size="lg" />
      </div>
    )
  }

  if (!currentSession) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-4">Session not found</h2>
          <button
            onClick={() => router.push('/practice')}
            className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
          >
            Go to Practice
          </button>
        </div>
      </div>
    )
  }

  return <PracticeSession sessionId={currentSession.sessionId} />
}
