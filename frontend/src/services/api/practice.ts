import { apiClient } from './client'
import { PracticeSession, PracticeResult, PracticeType, Question } from '@/types'

const normalizeQuestion = (data: any): Question | undefined => {
  if (!data) return undefined

  return {
    questionId: data?.questionId ?? data?.question_id ?? data?.id ?? '',
    subject: data?.subject,
    topic: data?.topic,
    subtopic: data?.subtopic ?? data?.sub_topic ?? undefined,
    type: data?.type,
    difficulty: data?.difficulty,
    status: data?.status ?? 'approved',
    title: data?.title ?? '',
    description: data?.description ?? '',
    instructions: data?.instructions ?? undefined,
    options: data?.options?.map((opt: any) => ({
      id: opt?.id,
      text: opt?.text,
      isCorrect: opt?.isCorrect ?? opt?.is_correct ?? false,
    })),
    correctAnswers: data?.correctAnswers ?? data?.correct_answers ?? undefined,
    codeSnippet: data?.codeSnippet ?? data?.code_snippet ?? undefined,
    programmingLanguage: data?.programmingLanguage ?? data?.programming_language ?? undefined,
    testCases: data?.testCases ?? data?.test_cases ?? undefined,
    timeLimit: data?.timeLimit ?? data?.time_limit ?? undefined,
    memoryLimit: data?.memoryLimit ?? data?.memory_limit ?? undefined,
    expectedAnswer: data?.expectedAnswer ?? data?.expected_answer ?? undefined,
    keyPoints: data?.keyPoints ?? data?.key_points ?? undefined,
    wordLimit: data?.wordLimit ?? data?.word_limit ?? undefined,
    requirements: data?.requirements ?? undefined,
    constraints: data?.constraints ?? undefined,
    expectedComponents: data?.expectedComponents ?? data?.expected_components ?? undefined,
    diagramsRequired: data?.diagramsRequired ?? data?.diagrams_required ?? false,
    caseData: data?.caseData ?? data?.case_data ?? undefined,
    datasets: data?.datasets ?? undefined,
    analysisRequired: data?.analysisRequired ?? data?.analysis_required ?? undefined,
    explanation: data?.explanation ?? '',
    detailedExplanation: data?.detailedExplanation ?? data?.detailed_explanation ?? undefined,
    hints: data?.hints ?? [],
    commonMistakes: data?.commonMistakes ?? data?.common_mistakes ?? undefined,
    references: data?.references ?? [],
  }
}

const normalizePracticeSession = (data: any): PracticeSession => {
  return {
    sessionId: data?.sessionId ?? data?.session_id ?? data?.id ?? '',
    type: data?.type,
    status: data?.status,
    title: data?.title ?? undefined,
    description: data?.description ?? undefined,
    totalQuestions: data?.totalQuestions ?? data?.total_questions ?? 0,
    timeLimit: data?.timeLimit ?? data?.time_limit ?? data?.time_limit_minutes ?? undefined,
    passingScore: data?.passingScore ?? data?.passing_score ?? undefined,
    subject: data?.subject ?? undefined,
    topic: data?.topic ?? undefined,
    company: data?.company ?? undefined,
    role: data?.role ?? undefined,
    questionIds: data?.questionIds ?? data?.question_ids ?? [],
    currentQuestionIndex: data?.currentQuestionIndex ?? data?.current_question_index ?? 0,
    currentQuestion: normalizeQuestion(data?.currentQuestion ?? data?.current_question),
    questionsAnswered: data?.questionsAnswered ?? data?.questions_answered ?? 0,
    questionsSkipped: data?.questionsSkipped ?? data?.questions_skipped ?? 0,
    correctAnswers: data?.correctAnswers ?? data?.correct_answers ?? 0,
    incorrectAnswers: data?.incorrectAnswers ?? data?.incorrect_answers ?? 0,
    score: data?.score ?? undefined,
    accuracy: data?.accuracy ?? undefined,
    totalTimeSpent: data?.totalTimeSpent ?? data?.total_time_spent ?? undefined,
    timeElapsed: data?.timeElapsed ?? data?.time_elapsed ?? 0,
    timeRemaining: data?.timeRemaining ?? data?.time_remaining ?? undefined,
    createdAt: data?.createdAt ?? data?.created_at ?? new Date().toISOString(),
    startedAt: data?.startedAt ?? data?.started_at ?? undefined,
    completedAt: data?.completedAt ?? data?.completed_at ?? undefined,
    lastActivityAt: data?.lastActivityAt ?? data?.last_activity_at ?? undefined,
  }
}

const normalizeProgress = (data: any) => {
  return {
    current: data?.current ?? 0,
    total: data?.total ?? 0,
    correct: data?.correct ?? 0,
    incorrect: data?.incorrect ?? 0,
  }
}

const normalizeSubmitResponse = (data: any) => {
  return {
    isCorrect: data?.isCorrect ?? data?.is_correct ?? false,
    correctAnswer: data?.correctAnswer ?? data?.correct_answer ?? [],
    explanation: data?.explanation ?? '',
    nextQuestion: normalizeQuestion(data?.nextQuestion ?? data?.next_question),
    sessionCompleted: data?.sessionCompleted ?? data?.session_completed ?? false,
    progress: normalizeProgress(data?.progress),
  }
}

const normalizeSkipResponse = (data: any) => {
  return {
    nextQuestion: normalizeQuestion(data?.nextQuestion ?? data?.next_question),
    sessionCompleted: data?.sessionCompleted ?? data?.session_completed ?? false,
    progress: normalizeProgress(data?.progress),
  }
}

export const practiceService = {
  // Quick Quiz
  startQuickQuiz: async (config: {
    totalQuestions?: number
    timeLimit?: number
    subjects?: string[]
    difficulties?: string[]
    shuffle?: boolean
  }) => {
    const response = await apiClient.post<PracticeSession>('/practice/quick-quiz/start', config)
    return { ...response, data: normalizePracticeSession(response.data) }
  },

  // Topic Practice
  startTopicPractice: async (config: {
    subject: string
    topic: string
    subtopics?: string[]
    totalQuestions?: number
    timeLimit?: number
    difficulty?: string
    includeExplanations?: boolean
    shuffle?: boolean
  }) => {
    const response = await apiClient.post<PracticeSession>('/practice/topic/start', config)
    return { ...response, data: normalizePracticeSession(response.data) }
  },

  getAvailableTopics: async (subject: string) => {
    return apiClient.get(`/practice/topics/${subject}`)
  },

  // Mock Test
  startMockTest: async (config: {
    subject: string
    title?: string
    totalQuestions?: number
    timeLimit?: number
    passingScore?: number
    difficultyDistribution?: Record<string, number>
    topics?: string[]
  }) => {
    const response = await apiClient.post<PracticeSession>('/practice/mock-test/start', config)
    return { ...response, data: normalizePracticeSession(response.data) }
  },

  // Company Grid
  startCompanyPractice: async (config: {
    company: string
    role?: string
    totalQuestions?: number
    timeLimit?: number
    difficultyFocus?: string
  }) => {
    const response = await apiClient.post<PracticeSession>('/practice/company/start', config)
    return { ...response, data: normalizePracticeSession(response.data) }
  },

  getCompanyGrids: async () => {
    return apiClient.get('/practice/companies')
  },

  // Session Management
  getSession: async (sessionId: string) => {
    const response = await apiClient.get<PracticeSession>(`/practice/session/${sessionId}`)
    return { ...response, data: normalizePracticeSession(response.data) }
  },

  submitAnswer: async (sessionId: string, questionId: string, answer: any, timeTaken: number) => {
    const response = await apiClient.post(`/practice/session/${sessionId}/answer`, {
      session_id: sessionId,
      question_id: questionId,
      answer,
      time_taken_seconds: timeTaken,
    })
    return { ...response, data: normalizeSubmitResponse(response.data) }
  },

  skipQuestion: async (sessionId: string) => {
    const response = await apiClient.post(`/practice/session/${sessionId}/skip`)
    return { ...response, data: normalizeSkipResponse(response.data) }
  },

  pauseSession: async (sessionId: string) => {
    return apiClient.post(`/practice/session/${sessionId}/pause`)
  },

  resumeSession: async (sessionId: string) => {
    const response = await apiClient.post<PracticeSession>(`/practice/session/${sessionId}/resume`)
    return { ...response, data: normalizePracticeSession(response.data) }
  },

  endSession: async (sessionId: string) => {
    return apiClient.post(`/practice/session/${sessionId}/end`)
  },

  submitFeedback: async (sessionId: string, rating: number, feedback?: string) => {
    return apiClient.post(`/practice/session/${sessionId}/feedback`, {
      session_id: sessionId,
      rating,
      feedback,
    })
  },

  getSessionResults: async (sessionId: string) => {
    return apiClient.get<PracticeResult>(`/practice/session/${sessionId}/results`)
  },

  // History
  getHistory: async (days: number = 30, type?: PracticeType) => {
    let url = `/practice/history?days=${days}`
    if (type) url += `&type=${type}`
    return apiClient.get(url)
  },

  getStats: async () => {
    return apiClient.get('/practice/stats')
  },

  // Leaderboard
  getLeaderboard: async (subject: string, period: string = 'all', limit: number = 10) => {
    return apiClient.get(`/practice/leaderboard/${subject}?period=${period}&limit=${limit}`)
  },
}
