'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { useAuth } from '@/hooks/useAuth'
import { useUser } from '@/hooks/useUser'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card/Card'
import { Button } from '@/components/ui/button/Button'
import { Input } from '@/components/ui/input/Input'
import { Select } from '@/components/ui/select/Select'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs/Tabs'
import { Avatar } from '@/components/ui/avatar/Avatar'
import { Badge } from '@/components/ui/badge/Badge'
import { motion } from 'framer-motion'
import {
  UserIcon,
  EnvelopeIcon,
  BuildingOfficeIcon,
  BriefcaseIcon,
  AcademicCapIcon,
  LockClosedIcon,
  BellIcon,
} from '@heroicons/react/24/outline'

const profileSchema = z.object({
  displayName: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Invalid email address'),
  phone: z.string().optional(),
  location: z.string().optional(),
  bio: z.string().max(500, 'Bio must not exceed 500 characters').optional(),
  currentCompany: z.string().optional(),
  currentRole: z.string().optional(),
  yearsOfExperience: z.number().min(0).max(50).optional(),
  github: z.string().url().optional().or(z.literal('')),
  linkedin: z.string().url().optional().or(z.literal('')),
  twitter: z.string().url().optional().or(z.literal('')),
  website: z.string().url().optional().or(z.literal('')),
})

type ProfileFormData = z.infer<typeof profileSchema>

export default function ProfilePage() {
  const { user } = useAuth()
  const {
    profile,
    preferences,
    isLoading,
    updateProfile,
    updatePreferences,
    uploadProfilePicture,
  } = useUser()

  const [isEditing, setIsEditing] = useState(false)
  const [activeTab, setActiveTab] = useState('profile')

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ProfileFormData>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      displayName: user?.displayName || '',
      email: user?.email || '',
      phone: user?.phone || '',
      location: user?.location || '',
      bio: user?.bio || '',
      currentCompany: user?.currentCompany || '',
      currentRole: user?.currentRole || '',
      yearsOfExperience: user?.yearsOfExperience || 0,
      github: user?.github || '',
      linkedin: user?.linkedin || '',
      twitter: user?.twitter || '',
      website: user?.website || '',
    },
  })

  const onSubmit = async (data: ProfileFormData) => {
    await updateProfile(data)
    setIsEditing(false)
  }

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      await uploadProfilePicture(file)
    }
  }

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(word => word[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Profile Header */}
      <Card>
        <CardContent className="p-6">
          <div className="flex items-start space-x-6">
            <div className="relative group">
              <Avatar
                src={user?.photoURL}
                fallback={user?.displayName ? getInitials(user.displayName) : 'U'}
                size="xl"
              />
              <label
                htmlFor="profile-picture"
                className="absolute inset-0 flex items-center justify-center bg-black/50 rounded-full opacity-0 group-hover:opacity-100 cursor-pointer transition-opacity"
              >
                <span className="text-white text-sm">Change</span>
              </label>
              <input
                type="file"
                id="profile-picture"
                className="hidden"
                accept="image/*"
                onChange={handleFileUpload}
              />
            </div>
            <div className="flex-1">
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                    {user?.displayName || 'User'}
                  </h1>
                  <p className="text-gray-600 dark:text-gray-400">
                    {user?.email}
                  </p>
                </div>
                <Badge variant="primary" size="lg">
                  {user?.role?.toUpperCase() || 'FREE'}
                </Badge>
              </div>
              {user?.bio && (
                <p className="mt-4 text-gray-700 dark:text-gray-300">{user.bio}</p>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Profile Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="w-full justify-start">
          <TabsTrigger value="profile">
            <UserIcon className="h-4 w-4 mr-2" />
            Profile
          </TabsTrigger>
          <TabsTrigger value="skills">
            <AcademicCapIcon className="h-4 w-4 mr-2" />
            Skills
          </TabsTrigger>
          <TabsTrigger value="security">
            <LockClosedIcon className="h-4 w-4 mr-2" />
            Security
          </TabsTrigger>
          <TabsTrigger value="notifications">
            <BellIcon className="h-4 w-4 mr-2" />
            Notifications
          </TabsTrigger>
        </TabsList>

        <TabsContent value="profile">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Profile Information</CardTitle>
                  <CardDescription>
                    Update your personal information
                  </CardDescription>
                </div>
                {!isEditing && (
                  <Button onClick={() => setIsEditing(true)}>Edit Profile</Button>
                )}
              </div>
            </CardHeader>
            <CardContent>
              {isEditing ? (
                <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Full Name</label>
                      <Input
                        {...register('displayName')}
                        error={errors.displayName?.message}
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Email</label>
                      <Input
                        {...register('email')}
                        type="email"
                        error={errors.email?.message}
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Phone</label>
                      <Input
                        {...register('phone')}
                        error={errors.phone?.message}
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Location</label>
                      <Input
                        {...register('location')}
                        error={errors.location?.message}
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium">Bio</label>
                    <textarea
                      {...register('bio')}
                      rows={4}
                      className="input w-full"
                    />
                    {errors.bio && (
                      <p className="text-sm text-error-500">{errors.bio.message}</p>
                    )}
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Current Company</label>
                      <Input
                        {...register('currentCompany')}
                        error={errors.currentCompany?.message}
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Current Role</label>
                      <Input
                        {...register('currentRole')}
                        error={errors.currentRole?.message}
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Years of Experience</label>
                      <Input
                        {...register('yearsOfExperience', { valueAsNumber: true })}
                        type="number"
                        error={errors.yearsOfExperience?.message}
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium">GitHub</label>
                    <Input
                      {...register('github')}
                      placeholder="https://github.com/username"
                      error={errors.github?.message}
                    />
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium">LinkedIn</label>
                    <Input
                      {...register('linkedin')}
                      placeholder="https://linkedin.com/in/username"
                      error={errors.linkedin?.message}
                    />
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium">Twitter</label>
                    <Input
                      {...register('twitter')}
                      placeholder="https://twitter.com/username"
                      error={errors.twitter?.message}
                    />
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium">Personal Website</label>
                    <Input
                      {...register('website')}
                      placeholder="https://yourwebsite.com"
                      error={errors.website?.message}
                    />
                  </div>

                  <div className="flex items-center space-x-3 pt-4">
                    <Button type="submit" disabled={isLoading}>
                      Save Changes
                    </Button>
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => setIsEditing(false)}
                    >
                      Cancel
                    </Button>
                  </div>
                </form>
              ) : (
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-500">Full Name</p>
                      <p className="font-medium">{user?.displayName || 'Not set'}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Email</p>
                      <p className="font-medium">{user?.email}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Phone</p>
                      <p className="font-medium">{user?.phone || 'Not set'}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Location</p>
                      <p className="font-medium">{user?.location || 'Not set'}</p>
                    </div>
                  </div>

                  <div>
                    <p className="text-sm text-gray-500">Bio</p>
                    <p className="font-medium">{user?.bio || 'No bio provided'}</p>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-500">Current Company</p>
                      <p className="font-medium">{user?.currentCompany || 'Not set'}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Current Role</p>
                      <p className="font-medium">{user?.currentRole || 'Not set'}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Experience</p>
                      <p className="font-medium">
                        {user?.yearsOfExperience ? `${user.yearsOfExperience} years` : 'Not set'}
                      </p>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {user?.github && (
                      <div>
                        <p className="text-sm text-gray-500">GitHub</p>
                        <a
                          href={user.github}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="font-medium text-primary-600 hover:text-primary-700"
                        >
                          {user.github}
                        </a>
                      </div>
                    )}
                    {user?.linkedin && (
                      <div>
                        <p className="text-sm text-gray-500">LinkedIn</p>
                        <a
                          href={user.linkedin}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="font-medium text-primary-600 hover:text-primary-700"
                        >
                          {user.linkedin}
                        </a>
                      </div>
                    )}
                    {user?.twitter && (
                      <div>
                        <p className="text-sm text-gray-500">Twitter</p>
                        <a
                          href={user.twitter}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="font-medium text-primary-600 hover:text-primary-700"
                        >
                          {user.twitter}
                        </a>
                      </div>
                    )}
                    {user?.website && (
                      <div>
                        <p className="text-sm text-gray-500">Website</p>
                        <a
                          href={user.website}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="font-medium text-primary-600 hover:text-primary-700"
                        >
                          {user.website}
                        </a>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="skills">
          <Card>
            <CardHeader>
              <CardTitle>Skills & Expertise</CardTitle>
              <CardDescription>
                Manage your technical and professional skills
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {profile?.skills && Object.entries(profile.skills).map(([category, skills]) => (
                  <div key={category}>
                    <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3 capitalize">
                      {category} Skills
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      {(skills as any[]).map((skill, index) => (
                        <Badge key={index} variant="secondary" size="lg">
                          {skill.name}
                          {skill.years && ` • ${skill.years}y`}
                        </Badge>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="security">
          <Card>
            <CardHeader>
              <CardTitle>Security Settings</CardTitle>
              <CardDescription>
                Manage your account security
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
                <div>
                  <h4 className="font-medium">Change Password</h4>
                  <p className="text-sm text-gray-500">
                    Update your password regularly
                  </p>
                </div>
                <Button variant="outline">Change</Button>
              </div>

              <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
                <div>
                  <h4 className="font-medium">Two-Factor Authentication</h4>
                  <p className="text-sm text-gray-500">
                    Add an extra layer of security
                  </p>
                </div>
                <Button variant="outline">Enable</Button>
              </div>

              <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
                <div>
                  <h4 className="font-medium">Active Sessions</h4>
                  <p className="text-sm text-gray-500">
                    Manage your active sessions
                  </p>
                </div>
                <Button variant="outline">View</Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="notifications">
          <Card>
            <CardHeader>
              <CardTitle>Notification Preferences</CardTitle>
              <CardDescription>
                Choose how you want to be notified
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="font-medium">Email Notifications</h4>
                  <p className="text-sm text-gray-500">
                    Receive updates via email
                  </p>
                </div>
                <input
                  type="checkbox"
                  className="toggle"
                  checked={preferences?.notifications?.email}
                  onChange={() => {}}
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <h4 className="font-medium">Push Notifications</h4>
                  <p className="text-sm text-gray-500">
                    Receive browser notifications
                  </p>
                </div>
                <input
                  type="checkbox"
                  className="toggle"
                  checked={preferences?.notifications?.push}
                  onChange={() => {}}
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <h4 className="font-medium">Daily Reminder</h4>
                  <p className="text-sm text-gray-500">
                    Get reminded to practice daily
                  </p>
                </div>
                <input
                  type="checkbox"
                  className="toggle"
                  checked={preferences?.notifications?.dailyReminder}
                  onChange={() => {}}
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <h4 className="font-medium">Weekly Report</h4>
                  <p className="text-sm text-gray-500">
                    Receive weekly progress report
                  </p>
                </div>
                <input
                  type="checkbox"
                  className="toggle"
                  checked={preferences?.notifications?.weeklyReport}
                  onChange={() => {}}
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}