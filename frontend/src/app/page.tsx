import Link from 'next/link'
import { Button } from '@/components/ui/button/Button'
import { ArrowRightIcon, CheckCircleIcon } from '@heroicons/react/24/outline'

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-gray-50 dark:from-gray-900 dark:to-gray-800">
      {/* Navigation */}
      <nav className="border-b border-gray-200 dark:border-gray-800 bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container-responsive py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold">AI</span>
              </div>
              <span className="text-xl font-bold text-gray-900 dark:text-white">Interview Platform</span>
            </div>
            <div className="flex items-center space-x-4">
              <Link href="/login">
                <Button variant="ghost">Sign In</Button>
              </Link>
              <Link href="/register">
                <Button>Get Started</Button>
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="py-20 md:py-28">
        <div className="container-responsive">
          <div className="text-center max-w-4xl mx-auto">
            <h1 className="text-5xl md:text-6xl font-bold text-gray-900 dark:text-white mb-6">
              Master Your{' '}
              <span className="gradient-text-primary">Technical Interviews</span>
            </h1>
            <p className="text-xl text-gray-600 dark:text-gray-400 mb-8 max-w-2xl mx-auto">
              Practice with AI-powered interviews, get real-time feedback, and land your dream job at top tech companies.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link href="/register">
                <Button size="lg" className="w-full sm:w-auto">
                  Start Free Trial
                  <ArrowRightIcon className="h-5 w-5 ml-2" />
                </Button>
              </Link>
              <Link href="#features">
                <Button variant="outline" size="lg" className="w-full sm:w-auto">
                  Learn More
                </Button>
              </Link>
            </div>
            <p className="text-sm text-gray-500 mt-4">
              No credit card required • 7-day free trial
            </p>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-white dark:bg-gray-900">
        <div className="container-responsive">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
              Everything you need to succeed
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
              Comprehensive tools and features to prepare for your dream job
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="p-6 bg-gray-50 dark:bg-gray-800 rounded-xl">
                <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900/20 rounded-lg flex items-center justify-center mb-4">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-600 dark:text-gray-400">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20 bg-primary-50 dark:bg-primary-900/20">
        <div className="container-responsive">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
            {stats.map((stat, index) => (
              <div key={index}>
                <div className="text-4xl font-bold text-primary-600 dark:text-primary-400 mb-2">
                  {stat.value}
                </div>
                <div className="text-gray-600 dark:text-gray-400">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20">
        <div className="container-responsive">
          <div className="bg-gradient-to-r from-primary-600 to-primary-800 rounded-2xl p-12 text-center">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Ready to ace your interview?
            </h2>
            <p className="text-xl text-primary-100 mb-8 max-w-2xl mx-auto">
              Join thousands of developers who have landed jobs at top companies
            </p>
            <Link href="/register">
              <Button variant="secondary" size="lg" className="bg-white text-primary-600 hover:bg-gray-100">
                Start Your Journey
                <ArrowRightIcon className="h-5 w-5 ml-2" />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-200 dark:border-gray-800 py-12">
        <div className="container-responsive">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold">AI</span>
                </div>
                <span className="font-bold text-gray-900 dark:text-white">Interview Platform</span>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Master your technical interviews with AI-powered practice.
              </p>
            </div>
            {footerLinks.map((section, index) => (
              <div key={index}>
                <h4 className="font-semibold text-gray-900 dark:text-white mb-4">{section.title}</h4>
                <ul className="space-y-2">
                  {section.links.map((link, i) => (
                    <li key={i}>
                      <Link href={link.href} className="text-sm text-gray-600 dark:text-gray-400 hover:text-primary-600">
                        {link.label}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
          <div className="mt-12 pt-8 border-t border-gray-200 dark:border-gray-800 text-center text-sm text-gray-600 dark:text-gray-400">
            © 2024 AI Interview Platform. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  )
}

const features = [
  {
    icon: <CheckCircleIcon className="h-6 w-6 text-primary-600" />,
    title: 'AI-Powered Interviews',
    description: 'Practice with realistic AI interviews that adapt to your skill level.',
  },
  {
    icon: <CheckCircleIcon className="h-6 w-6 text-primary-600" />,
    title: 'Company-Specific Prep',
    description: 'Targeted practice for Google, Amazon, Microsoft, and more.',
  },
  {
    icon: <CheckCircleIcon className="h-6 w-6 text-primary-600" />,
    title: 'Real-time Feedback',
    description: 'Get instant feedback on your responses with detailed analysis.',
  },
  {
    icon: <CheckCircleIcon className="h-6 w-6 text-primary-600" />,
    title: 'Resume Analysis',
    description: 'Upload your resume for AI-powered gap analysis and improvement suggestions.',
  },
  {
    icon: <CheckCircleIcon className="h-6 w-6 text-primary-600" />,
    title: 'Progress Tracking',
    description: 'Track your improvement with detailed analytics and insights.',
  },
  {
    icon: <CheckCircleIcon className="h-6 w-6 text-primary-600" />,
    title: 'Community Support',
    description: 'Learn with peers, share experiences, and grow together.',
  },
]

const stats = [
  { value: '50K+', label: 'Active Users' },
  { value: '10K+', label: 'Practice Questions' },
  { value: '85%', label: 'Success Rate' },
]

const footerLinks = [
  {
    title: 'Product',
    links: [
      { label: 'Features', href: '/features' },
      { label: 'Pricing', href: '/pricing' },
      { label: 'FAQ', href: '/faq' },
    ],
  },
  {
    title: 'Company',
    links: [
      { label: 'About', href: '/about' },
      { label: 'Blog', href: '/blog' },
      { label: 'Contact', href: '/contact' },
    ],
  },
  {
    title: 'Legal',
    links: [
      { label: 'Privacy', href: '/privacy' },
      { label: 'Terms', href: '/terms' },
      { label: 'Security', href: '/security' },
    ],
  },
]