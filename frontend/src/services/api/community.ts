import { apiClient } from './client'

export const communityService = {
  // Forums
  getForums: async () => {
    return apiClient.get('/community/forums')
  },

  getForum: async (forumId: string) => {
    return apiClient.get(`/community/forums/${forumId}`)
  },

  getThreads: async (forumId: string, params?: {
    page?: number
    limit?: number
    sort?: 'latest' | 'popular' | 'unanswered'
  }) => {
    const queryParams = new URLSearchParams()
    if (params?.page) queryParams.append('page', params.page.toString())
    if (params?.limit) queryParams.append('limit', params.limit.toString())
    if (params?.sort) queryParams.append('sort', params.sort)

    return apiClient.get(`/community/forums/${forumId}/threads?${queryParams.toString()}`)
  },

  getThread: async (threadId: string) => {
    return apiClient.get(`/community/threads/${threadId}`)
  },

  createThread: async (data: {
    forumId: string
    title: string
    content: string
    tags?: string[]
  }) => {
    return apiClient.post('/community/threads', data)
  },

  updateThread: async (threadId: string, data: { title?: string; content?: string }) => {
    return apiClient.put(`/community/threads/${threadId}`, data)
  },

  deleteThread: async (threadId: string) => {
    return apiClient.delete(`/community/threads/${threadId}`)
  },

  // Posts/Comments
  getPosts: async (threadId: string, page: number = 1, limit: number = 20) => {
    return apiClient.get(`/community/threads/${threadId}/posts?page=${page}&limit=${limit}`)
  },

  createPost: async (threadId: string, content: string, parentId?: string) => {
    return apiClient.post(`/community/threads/${threadId}/posts`, {
      content,
      parent_id: parentId,
    })
  },

  updatePost: async (postId: string, content: string) => {
    return apiClient.put(`/community/posts/${postId}`, { content })
  },

  deletePost: async (postId: string) => {
    return apiClient.delete(`/community/posts/${postId}`)
  },

  likePost: async (postId: string) => {
    return apiClient.post(`/community/posts/${postId}/like`)
  },

  unlikePost: async (postId: string) => {
    return apiClient.delete(`/community/posts/${postId}/like`)
  },

  // Study Groups
  getStudyGroups: async () => {
    return apiClient.get('/community/study-groups')
  },

  getStudyGroup: async (groupId: string) => {
    return apiClient.get(`/community/study-groups/${groupId}`)
  },

  createStudyGroup: async (data: {
    name: string
    description: string
    topics: string[]
    maxMembers?: number
    isPrivate?: boolean
  }) => {
    return apiClient.post('/community/study-groups', data)
  },

  joinStudyGroup: async (groupId: string) => {
    return apiClient.post(`/community/study-groups/${groupId}/join`)
  },

  leaveStudyGroup: async (groupId: string) => {
    return apiClient.post(`/community/study-groups/${groupId}/leave`)
  },

  // Leaderboard
  getLeaderboard: async (params?: {
    period?: 'daily' | 'weekly' | 'monthly' | 'all'
    subject?: string
    limit?: number
  }) => {
    const queryParams = new URLSearchParams()
    if (params?.period) queryParams.append('period', params.period)
    if (params?.subject) queryParams.append('subject', params.subject)
    if (params?.limit) queryParams.append('limit', params.limit.toString())

    return apiClient.get(`/community/leaderboard?${queryParams.toString()}`)
  },

  // Badges
  getBadges: async () => {
    return apiClient.get('/community/badges')
  },

  getUserBadges: async (userId: string) => {
    return apiClient.get(`/community/users/${userId}/badges`)
  },
}