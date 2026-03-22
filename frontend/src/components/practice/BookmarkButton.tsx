'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { BookmarkIcon as BookmarkOutline } from '@heroicons/react/24/outline'
import { BookmarkIcon as BookmarkSolid } from '@heroicons/react/24/solid'

interface BookmarkButtonProps {
  isBookmarked?: boolean
  onClick?: () => void
  size?: 'sm' | 'md' | 'lg'
}

const sizeClasses = {
  sm: 'h-4 w-4',
  md: 'h-5 w-5',
  lg: 'h-6 w-6',
}

export const BookmarkButton = ({
  isBookmarked = false,
  onClick,
  size = 'md',
}: BookmarkButtonProps) => {
  const [isHovered, setIsHovered] = useState(false)

  return (
    <motion.button
      whileHover={{ scale: 1.1 }}
      whileTap={{ scale: 0.95 }}
      onHoverStart={() => setIsHovered(true)}
      onHoverEnd={() => setIsHovered(false)}
      onClick={onClick}
      className={`p-2 rounded-lg transition-colors ${
        isBookmarked
          ? 'text-yellow-500 hover:text-yellow-600'
          : 'text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300'
      }`}
      aria-label={isBookmarked ? 'Remove bookmark' : 'Add bookmark'}
    >
      {isBookmarked ? (
        <BookmarkSolid className={sizeClasses[size]} />
      ) : (
        <BookmarkOutline className={sizeClasses[size]} />
      )}
    </motion.button>
  )
}