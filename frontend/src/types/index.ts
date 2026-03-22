// User Types
export interface User {
    uid: string
    email: string
    displayName?: string
    photoURL?: string
    role: 'free' | 'pro' | 'premium' | 'admin'
    status: 'active' | 'inactive' | 'suspended'
    createdAt: string
    lastLogin?: string
    
    // Profile
    bio?: string
    location?: string
    phone?: string
    website?: string
    github?: string
    linkedin?: string
    twitter?: string
    
    // Professional
    currentCompany?: string
    currentRole?: string
    yearsOfExperience?: number
    experienceLevel?: 'entry' | 'junior' | 'mid' | 'senior' | 'lead' | 'principal'
    
    // Skills
    skills: {
      technical: Skill[]
      soft: Skill[]
      domain: Skill[]
      tools: Skill[]
      languages: Skill[]
    }
    
    // Stats
    stats: UserStats
    
    // Targets
    targetCompanies: string[]
    targetRoles: string[]
    targetInterviewDate?: string
    
    // Preferences
    preferences: UserPreferences
    
    // Subscription
    subscriptionId?: string
    subscriptionPlan?: string
    subscriptionExpires?: string
    
    // Security
    emailVerified: boolean
    mfaEnabled: boolean
  }
  
  export interface Skill {
    name: string
    years?: number
    level?: 'beginner' | 'intermediate' | 'advanced' | 'expert'
    lastUsed?: string
  }
  
  export interface UserStats {
    totalQuestions: number
    correctAnswers: number
    accuracy: number
    currentStreak: number
    longestStreak: number
    totalPracticeTime: number // minutes
    totalTestsTaken: number
    averageScore: number
  }
  
  export interface UserPreferences {
    theme: 'light' | 'dark' | 'system'
    language: string
    notifications: {
      email: boolean
      push: boolean
      dailyReminder: boolean
      weeklyReport: boolean
    }
    dailyGoal: number
    difficultyPreference: 'easy' | 'medium' | 'hard' | 'expert'
    subjectsInterest: string[]
  }
  
  // Question Types
  export interface Question {
    questionId: string
    subject: 'ml' | 'dl' | 'ds' | 'da' | 'ai'
    topic: string
    subtopic?: string
    type: 'mcq' | 'code' | 'theory' | 'system_design' | 'case_study' | 'multiple_select' | 'true_false' | 'fill_blank' | 'matching'
    difficulty: 'easy' | 'medium' | 'hard' | 'expert'
    status: 'draft' | 'review' | 'approved' | 'rejected' | 'archived'
    
    // Content
    title: string
    description: string
    instructions?: string
    
    // For MCQ
    options?: QuestionOption[]
    
    // For multiple correct
    correctAnswers?: string[]
    
    // For code questions
    codeSnippet?: string
    programmingLanguage?: string
    testCases?: TestCase[]
    timeLimit?: number // milliseconds
    memoryLimit?: number // MB
    
    // For theory
    expectedAnswer?: string
    keyPoints?: string[]
    wordLimit?: number
    
    // For system design
    requirements?: string[]
    constraints?: string[]
    expectedComponents?: string[]
    diagramsRequired?: boolean
    
    // For case study
    caseData?: Record<string, any>
    datasets?: string[]
    analysisRequired?: string[]
    
    // Explanation
    explanation: string
    detailedExplanation?: string
    hints: string[]
    commonMistakes?: string[]
    
    // Resources
    references: Resource[]
    videos: Resource[]
    images: string[]
    
    // Metadata
    tags: string[]
    companies: string[]
    roles: string[]
    
    // Statistics
    timesUsed: number
    correctRate: number
    avgTimeSeconds: number
    difficultyRating: number
    
    createdAt: string
    updatedAt?: string
  }
  
  export interface QuestionOption {
    id: string
    text: string
    isCorrect?: boolean // Only included when fetching with answers
  }
  
  export interface TestCase {
    input: string
    output: string
    hidden: boolean
  }
  
  export interface Resource {
    title: string
    url: string
    type?: 'article' | 'video' | 'book' | 'course'
  }
  
  // Practice Types
  export type PracticeType = 'quick_quiz' | 'topic_wise' | 'mock_test' | 'company_grid' | 'custom'
  
  export interface PracticeSession {
    sessionId: string
    type: PracticeType
    status: 'not_started' | 'in_progress' | 'completed' | 'timed_out' | 'abandoned'
    
    // Configuration
    title?: string
    description?: string
    totalQuestions: number
    timeLimit?: number // minutes
    passingScore?: number // percentage
    
    // Content
    subject?: string
    topic?: string
    company?: string
    role?: string
    questionIds: string[]
    
    // Progress
    currentQuestionIndex: number
    currentQuestion?: Question
    questionsAnswered: number
    questionsSkipped: number
    correctAnswers: number
    incorrectAnswers: number
    
    // Results
    score?: number
    accuracy?: number
    totalTimeSpent?: number // seconds
    timeElapsed?: number // seconds
    timeRemaining?: number // seconds
    
    // Timestamps
    createdAt: string
    startedAt?: string
    completedAt?: string
    lastActivityAt?: string
  }
  
  export interface PracticeResult {
    sessionId: string
    score: number
    accuracy: number
    totalTimeSpent: number
    correctAnswers: number
    incorrectAnswers: number
    skippedQuestions: number
    subjectWise: Record<string, SubjectPerformance>
    topicWise: Record<string, TopicPerformance>
    difficultyWise: Record<string, DifficultyPerformance>
    strengths: string[]
    weaknesses: string[]
    recommendations: string[]
    percentile?: number
    averageScore?: number
    completedAt: string
  }

  export interface QuestionAttempt {
    attemptId?: string
    questionId: string
    sessionId?: string
    answer?: any
    isCorrect?: boolean
    score?: number
    timeTaken?: number
    timeTakenSeconds?: number
    attemptedAt?: string
    feedback?: string
  }
  
  export interface SubjectPerformance {
    total: number
    correct: number
    accuracy: number
  }
  
  export interface TopicPerformance {
    total: number
    correct: number
    accuracy: number
    masteryLevel: 'not_started' | 'beginner' | 'intermediate' | 'advanced' | 'mastered'
  }
  
  export interface DifficultyPerformance {
    total: number
    correct: number
    accuracy: number
    averageTime: number
  }
  
  // Resume Types
  export interface Resume {
    resumeId: string
    filename: string
    fileUrl: string
    fileSize: number
    status: 'uploaded' | 'parsing' | 'parsed' | 'analyzing' | 'analyzed' | 'failed'
    uploadedAt: string
    parsedAt?: string
    analyzedAt?: string
    errorMessage?: string
  }
  
  export interface ParsedResume {
    personalInfo: {
      name?: string
      email?: string
      phone?: string
      location?: string
      linkedin?: string
      github?: string
      portfolio?: string
    }
    summary?: string
    skills: Record<string, Skill[]>
    workExperience: WorkExperience[]
    totalExperienceYears: number
    experienceLevel: string
    education: Education[]
    projects: Project[]
    certifications: Certification[]
    achievements: string[]
    languages: Language[]
  }

  export interface GapAnalysis {
    overall_readiness: number
    technical_readiness: number
    behavioral_readiness: number
    system_design_readiness: number
    skill_gaps: Array<{
      skill: string
      current_level: string
      required_level: string
      severity: string
      estimated_time: number
    }>
    experience_gap: {
      current: number
      required: number
      gap: number
    }
    education_gap: {
      current: string
      required: string
      gap: number
    }
    project_gap: {
      current: number
      required: number
      gap: number
    }
    high_priority_gaps: any[]
    estimated_preparation_time: number
    recommended_interview_date: string
  }

  export interface LearningRoadmap {
    roadmap_id: string
    target_company: string
    target_role: string
    created_at: string
    target_interview_date: string
    total_days: number
    overall_progress: number
    milestones: Array<{
      milestone_id: string
      title: string
      description: string
      category: string
      target_date: string
      completed: boolean
      completed_at?: string
      progress: number
      tasks: Array<{
        name: string
        completed: boolean
      }>
      resources: Array<{
        type: string
        name: string
        url?: string
      }>
    }>
    weekly_plan: Array<{
      week: number
      start_date: string
      end_date: string
      focus_areas: Array<{
        topic: string
        hours: number
        focus: string
      }>
      total_hours: number
    }>
    recommended_courses: Array<{
      name: string
      platform: string
      url: string
      duration_hours: number
    }>
    recommended_practice: Array<{
      name: string
      platform: string
      count: number
      type: string
    }>
  }
  
  export interface WorkExperience {
    role: string
    company: string
    duration: string
    startDate?: string
    endDate?: string
    durationMonths?: number
    achievements: string[]
    technologies?: string[]
  }
  
  export interface Education {
    degree: string
    institution: string
    graduationYear?: number
    gpa?: number
    field?: string
  }
  
  export interface Project {
    name: string
    description: string
    technologies: string[]
    link?: string
  }
  
  export interface Certification {
    name: string
    issuer?: string
    date?: string
    credentialId?: string
    url?: string
  }
  
  export interface Language {
    language: string
    proficiency: string
  }
  
  // Analytics Types
  export interface AnalyticsSummary {
    overallAccuracy: number
    totalQuestions: number
    currentStreak: number
    longestStreak: number
    totalPracticeTime: number
    averageDailyTime: number
  }
  
  export interface PerformanceTrend {
    dates: string[]
    accuracy: number[]
    volume: number[]
    timeSpent: number[]
  }
  
  export interface TopicMastery {
    masteredTopics: TopicMasteryItem[]
    inProgressTopics: TopicMasteryItem[]
    notStartedTopics: TopicMasteryItem[]
  }
  
  export interface TopicMasteryItem {
    topic: string
    accuracy: number
    attempts: number
    masteryLevel: string
    lastPracticed?: string
  }
  
  export interface CompanyReadiness {
    company: string
    overallScore: number
    readinessLevel: 'not_ready' | 'almost_ready' | 'ready' | 'highly_ready'
    technicalScore: number
    behavioralScore: number
    systemDesignScore: number
    interviewSuccessProbability: number
    estimatedPreparationTime: number
    criticalGaps: string[]
    logo?: string
  }
  
  // Interview Types
  export interface InterviewSession {
    sessionId: string
    interviewType: 'voice' | 'video' | 'text' | 'mixed'
    interviewMode: 'practice' | 'mock' | 'assessment' | 'company_specific'
    status: 'scheduled' | 'in_progress' | 'paused' | 'completed' | 'timed_out' | 'cancelled'
    
    title: string
    description?: string
    difficulty: 'beginner' | 'intermediate' | 'advanced' | 'expert'
    durationMinutes: number
    companyFocus?: string
    roleFocus?: string
    
    currentQuestion?: InterviewQuestion
    currentQuestionIndex: number
    totalQuestions: number
    questionsAnswered: number
    
    startedAt?: string
    completedAt?: string
    timeElapsed: number
    timeRemaining: number
    
    createdAt: string
  }
  
  export interface InterviewQuestion {
    questionId: string
    questionText: string
    context?: string
    category: 'technical' | 'behavioral' | 'system_design' | 'coding' | 'case_study' | 'ml_design' | 'research'
    difficulty: string
    
    // For coding
    codeSnippet?: string
    programmingLanguage?: string
    
    // For system design
    requirements?: string[]
    constraints?: string[]
    
    hint?: string
  }
  
  export interface InterviewFeedback {
    overallScore: number
    technicalScore: number
    communicationScore: number
    problemSolvingScore: number
    strengths: string[]
    weaknesses: string[]
    improvements: string[]
    categoryScores: Record<string, number>
    questionFeedback: Array<{
      questionId: string
      questionText: string
      score: number
      feedback: string
      strengths: string[]
      improvements: string[]
    }>
    recommendedTopics: string[]
    percentile?: number
    createdAt: string
  }
  
  // API Response Types
  export interface ApiResponse<T> {
    data: T
    message?: string
    status: number
  }
  
  export interface PaginatedResponse<T> {
    items: T[]
    total: number
    page: number
    limit: number
    totalPages: number
  }
  
  // Company Types
  export interface Company {
    name: string
    description: string
    logo?: string
    interviewProcess: string[]
    topics: string[]
    difficulty: 'medium' | 'hard'
    averageScore?: number
    userScore?: number
  }
  
  // Achievement Types
  export interface Achievement {
    id: string
    name: string
    description: string
    icon: string
    category: string
    earnedAt: string
    progress: number
  }
