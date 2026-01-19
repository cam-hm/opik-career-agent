/**
 * Centralized API Endpoints
 * 
 * Defines all backend API routes in a single location to avoid hardcoding.
 * The prefix /api/v1 is configurable here.
 */

const API_PREFIX = "/api/v1";

export const ENDPOINTS = {
    INTERVIEW: {
        LIST: `${API_PREFIX}/interviews`,
        DETAIL: (sessionId: string) => `${API_PREFIX}/interviews/${sessionId}`,
        FEEDBACK: (sessionId: string) => `${API_PREFIX}/interviews/${sessionId}/feedback`,
        ANALYZE: (sessionId: string) => `${API_PREFIX}/interviews/${sessionId}/analyze`,
        TOKEN: (sessionId: string) => `${API_PREFIX}/interviews/${sessionId}/token`,
        PRACTICE_CREATE: `${API_PREFIX}/practice`,
    },
    APPLICATION: {
        LIST: `${API_PREFIX}/applications`,
        DETAIL: (id: string) => `${API_PREFIX}/applications/${id}`,
        START_STAGE: (id: string) => `${API_PREFIX}/applications/${id}/start_stage`,
        SKIP_STAGE: (id: string) => `${API_PREFIX}/applications/${id}/skip_stage`,
        COMPLETE_STAGE: (id: string) => `${API_PREFIX}/applications/${id}/complete_stage`,
        PROCEED_STAGE: (id: string) => `${API_PREFIX}/applications/${id}/proceed_to_next_stage`,
    },
    RESUME: {
        GENERATE_JD: `${API_PREFIX}/generate-jd`,
    },
    DEBUG: {
        TEST_TTS: `${API_PREFIX}/debug/test-tts`,
        VOICES: `${API_PREFIX}/debug/voices`,
    },
    PROGRESS: {
        DASHBOARD: `${API_PREFIX}/progress/dashboard`,
        RESOLUTIONS: `${API_PREFIX}/progress/resolutions`,
        RESOLUTION_DETAIL: (id: string) => `${API_PREFIX}/progress/resolutions/${id}`,
        RESOLUTION_COMPLETE: (id: string) => `${API_PREFIX}/progress/resolutions/${id}/complete`,
        SKILL_GAP: `${API_PREFIX}/progress/skill-gap`,
        WEEKLY_INSIGHTS: `${API_PREFIX}/progress/insights/weekly`,
        HISTORY: `${API_PREFIX}/progress/history`,
    },
    ANALYTICS: {
        OVERVIEW: `${API_PREFIX}/analytics/overview`,
        EVALUATION: `${API_PREFIX}/analytics/evaluation`,
        COMPONENTS: `${API_PREFIX}/analytics/components`,
    },
} as const;
