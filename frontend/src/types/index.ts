export interface User {
  id: number
  email: string
  full_name: string
  college?: string | null
  branch?: string | null
  graduation_year?: number | null
  target_companies?: string[] | null
  leetcode_username?: string | null
  created_at: string
}

export interface LeetCodeStats {
  username: string
  ranking?: number | null
  total_solved: number
  easy_solved: number
  medium_solved: number
  hard_solved: number
  contest_rating: number
  contest_attended: number
  contest_global_ranking?: number | null
  contest_top_percentage?: number | null
  current_streak: number
  last_synced?: string | null
  profile_url: string
  tag_counts: Record<string, number>
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}

export interface DashboardData {
  dsa_progress_percent: number
  cs_subjects_progress: { subject_name: string; progress_percent: number }[]
  resume_score?: number | null
  mock_interview_score?: number | null
  contest_rating: number
  current_streak: number
  total_problems_solved: number
  readiness_score: number
  upcoming_companies: {
    id: number
    name: string
    difficulty_level: string
    description?: string | null
  }[]
}

export interface DsaProgressItem {
  id: number
  topic_id: number
  topic_name: string
  problems_solved: number
  total_problems: number
  proficiency_level: string
  progress_percent: number
}

export interface DsaFullProgress {
  items: DsaProgressItem[]
  contest_rating: number
  current_streak: number
  total_problems_solved: number
  leetcode?: LeetCodeStats | null
}

export interface ResumeReport {
  id: number
  filename: string
  analysis_json: {
    strengths?: string[]
    weaknesses?: string[]
    missing_skills?: string[]
    suggested_projects?: string[]
    summary?: string
  }
  score: number
  created_at: string
}

export interface Company {
  id: number
  name: string
  description?: string | null
  difficulty_level: string
  hiring_process?: string | null
}

export interface RoadmapResponse {
  id: number
  company_id: number
  company_name: string
  content_json: {
    overview?: string
    timeline_weeks?: number
    phases?: {
      week_range?: string
      title?: string
      topics?: string[]
      resources?: string[]
      milestones?: string[]
    }[]
    dsa_focus?: string[]
    cs_subjects?: string[]
    mock_interview_tips?: string[]
    daily_schedule?: string
  }
  created_at: string
}

export interface ChatMessage {
  id: number
  role: string
  content: string
  session_id: string
  created_at: string
}

export interface MentorHistory {
  session_id: string
  messages: ChatMessage[]
}

export interface InterviewSource {
  company: string
  role: string
  outcome: string
  relevance_score?: number | null
}

export interface MockQuestion {
  index: number
  category: string
  question: string
  difficulty?: string
}

export interface AnalyticsData {
  dsa_completion_percent: number
  strong_areas: string[]
  weak_areas: string[]
  readiness_score: number
  topic_breakdown: {
    topic_name: string
    progress_percent: number
    problems_solved: number
    total_problems: number
  }[]
  cs_subjects: Record<string, unknown>[]
  resume_score?: number | null
  mock_interview_avg?: number | null
  llm_insights?: string | null
}