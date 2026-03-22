import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Providers } from './providers'
import { Toaster } from 'react-hot-toast'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: {
    default: 'AI Interview Platform',
    template: '%s | AI Interview Platform'
  },
  description: 'Master your technical interviews with AI-powered practice platform for ML, DL, DS, and AI roles',
  keywords: ['interview preparation', 'AI interview', 'machine learning', 'deep learning', 'data science', 'practice questions'],
  authors: [{ name: 'AI Interview Platform' }],
  creator: 'AI Interview Platform',
  publisher: 'AI Interview Platform',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  metadataBase: new URL('https://aiinterviewplatform.com'),
  alternates: {
    canonical: '/',
  },
  openGraph: {
    title: 'AI Interview Platform',
    description: 'Master your technical interviews with AI-powered practice',
    url: 'https://aiinterviewplatform.com',
    siteName: 'AI Interview Platform',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'AI Interview Platform',
      },
    ],
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'AI Interview Platform',
    description: 'Master your technical interviews with AI-powered practice',
    images: ['/og-image.png'],
    creator: '@aiinterview',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  icons: {
    icon: '/favicon.ico',
    shortcut: '/favicon-16x16.png',
    apple: '/apple-touch-icon.png',
  },
  manifest: '/manifest.json',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <Providers>
          {children}
          <Toaster 
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#363636',
                color: '#fff',
              },
              success: {
                duration: 3000,
                iconTheme: {
                  primary: '#22c55e',
                  secondary: '#fff',
                },
              },
              error: {
                duration: 4000,
                iconTheme: {
                  primary: '#ef4444',
                  secondary: '#fff',
                },
              },
            }}
          />
        </Providers>
      </body>
    </html>
  )
}