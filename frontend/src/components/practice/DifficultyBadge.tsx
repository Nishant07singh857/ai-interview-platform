'use client'

import { Badge } from '@/components/ui/badge/Badge'

interface DifficultyBadgeProps {
  difficulty: 'easy' | 'medium' | 'hard' | 'expert'
  size?: 'sm' | 'md' | 'lg'
  showLabel?: boolean
}

const difficultyConfig = {
  easy: {
    label: 'Easy',
    variant: 'success' as const,
    icon: '🌱',
  },
  medium: {
    label: 'Medium',
    variant: 'warning' as const,
    icon: '📊',
  },
  hard: {
    label: 'Hard',
    variant: 'error' as const,
    icon: '⚡',
  },
  expert: {
    label: 'Expert',
    variant: 'primary' as const,
    icon: '🎯',
  },
}

export const DifficultyBadge = ({
  difficulty,
  size = 'md',
  showLabel = true,
}: DifficultyBadgeProps) => {
  const config = difficultyConfig[difficulty]

  return (
    <Badge variant={config.variant} size={size} className="inline-flex items-center">
      <span className="mr-1">{config.icon}</span>
      {showLabel && config.label}
    </Badge>
  )
}