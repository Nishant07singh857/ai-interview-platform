'use client'

import { SessionProvider } from 'next-auth/react'
import { ThemeProvider } from 'next-themes'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Provider as ReduxProvider } from 'react-redux'
import { useEffect, useState } from 'react'
import { store, useAppDispatch, useAppSelector } from '@/store/store'
import { setAuthToken } from '@/services/api/client'
import { hydrateSession } from '@/store/slices/authSlice'

function AuthSessionBootstrap() {
  const dispatch = useAppDispatch()

  useEffect(() => {
    if (typeof window === 'undefined') return

    const token = localStorage.getItem('auth.accessToken')
    if (!token) return

    const refreshToken = localStorage.getItem('auth.refreshToken')
    const sessionExpiresAt = localStorage.getItem('auth.sessionExpiresAt')

    if (sessionExpiresAt && new Date(sessionExpiresAt) <= new Date()) {
      localStorage.removeItem('auth.accessToken')
      localStorage.removeItem('auth.refreshToken')
      localStorage.removeItem('auth.sessionExpiresAt')
      return
    }

    dispatch(
      hydrateSession({
        token,
        refreshToken,
        sessionExpiresAt,
      })
    )
  }, [dispatch])

  return null
}

function AuthTokenSync() {
  const token = useAppSelector((state) => state.auth.token)

  useEffect(() => {
    setAuthToken(token)
  }, [token])

  return null
}

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000,
            gcTime: 5 * 60 * 1000,
            retry: 1,
            refetchOnWindowFocus: false,
          },
        },
      })
  )

  return (
    <SessionProvider refetchInterval={0} refetchOnWindowFocus={false}>
      <ReduxProvider store={store}>
        <AuthSessionBootstrap />
        <AuthTokenSync />
        <QueryClientProvider client={queryClient}>
          <ThemeProvider
            attribute="class"
            defaultTheme="system"
            enableSystem
            disableTransitionOnChange
          >
            {children}
          </ThemeProvider>
        </QueryClientProvider>
      </ReduxProvider>
    </SessionProvider>
  )
}
