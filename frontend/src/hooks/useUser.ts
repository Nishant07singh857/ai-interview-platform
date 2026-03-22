import { useCallback } from 'react'
import { useAppDispatch, useAppSelector } from '@/store/store'
import {
  fetchUserProfile,
  updateUserProfile,
  fetchUserPreferences,
  updateUserPreferences,
  fetchUserSkills,
  updateUserSkills,
  fetchRecentActivity,
  uploadProfilePicture,
} from '@/store/slices/userSlice'
import { Skill, UserPreferences, User } from '@/types'

export const useUser = () => {
  const dispatch = useAppDispatch()
  const { profile, preferences, skills, recentActivity, stats, isLoading, error } = useAppSelector(
    (state) => state.user
  )

  const loadProfile = useCallback(() => {
    return dispatch(fetchUserProfile()).unwrap()
  }, [dispatch])

  const updateProfile = useCallback((data: Partial<User>) => {
    return dispatch(updateUserProfile(data)).unwrap()
  }, [dispatch])

  const loadPreferences = useCallback(() => {
    return dispatch(fetchUserPreferences()).unwrap()
  }, [dispatch])

  const updatePreferences = useCallback((data: Partial<UserPreferences>) => {
    return dispatch(updateUserPreferences(data)).unwrap()
  }, [dispatch])

  const loadSkills = useCallback(() => {
    return dispatch(fetchUserSkills()).unwrap()
  }, [dispatch])

  const updateSkills = useCallback((data: Record<string, Skill[]>) => {
    return dispatch(updateUserSkills(data)).unwrap()
  }, [dispatch])

  const loadRecentActivity = useCallback((limit?: number) => {
    return dispatch(fetchRecentActivity(limit ?? 10)).unwrap()
  }, [dispatch])

  const uploadAvatar = useCallback((file: File) => {
    return dispatch(uploadProfilePicture(file)).unwrap()
  }, [dispatch])

  return {
    profile,
    preferences,
    skills,
    recentActivity,
    stats,
    isLoading,
    error,
    fetchProfile: loadProfile,
    updateProfile,
    fetchPreferences: loadPreferences,
    updatePreferences,
    fetchSkills: loadSkills,
    updateSkills,
    fetchRecentActivity: loadRecentActivity,
    uploadProfilePicture: uploadAvatar,
  }
}
