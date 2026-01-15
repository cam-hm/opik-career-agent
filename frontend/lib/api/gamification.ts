// Ensure API URL ends with /api/v1
const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_URL = BASE_URL.endsWith('/api/v1') ? BASE_URL : `${BASE_URL}/api/v1`;

export interface Badge {
    id: string;
    name: string | Record<string, string>;
    description: string | Record<string, string>;
    icon: string;
    unlocked_at?: string;
}

export interface GamificationStatus {
    level: number;
    xp: number;
    rank_title: string;
    target_role?: string;
    stats: Record<string, number>;
    nodes: Record<string, UserNodeStatus>;
    badges?: Badge[];
}

export interface UserNodeStatus {
    node_id: string;
    status: 'locked' | 'unlocked' | 'completed';
    high_score: number;
}

export interface CareerNode {
    id: string;
    title: string | Record<string, string>;
    type: string;
    rank_required?: number;
    description: string | Record<string, string>;
    unlocks: string[];
    // Duolingo-style layout
    order?: number;
    section?: string;
    icon?: string;
    // Legacy position (fallback)
    position?: { x: number; y: number };
    metadata?: {
        pass_rate?: string;
        fail_rate?: string;
        difficulty?: string;
        duration?: string;
        reward?: string;
    };
}

export const gamificationApi = {
    getTree: async (token: string): Promise<{ nodes: CareerNode[] }> => {
        const res = await fetch(`${API_URL}/gamification/tree`, {
            headers: { Authorization: `Bearer ${token}` },
        });
        if (!res.ok) throw new Error('Failed to fetch career tree');
        return res.json();
    },

    getStatus: async (token: string): Promise<GamificationStatus> => {
        const res = await fetch(`${API_URL}/gamification/status`, {
            headers: { Authorization: `Bearer ${token}` },
        });
        if (!res.ok) throw new Error('Failed to fetch gamification status');
        return res.json();
    },

    setupProfile: async (token: string, targetRole: string) => {
        const res = await fetch(`${API_URL}/gamification/setup`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify({ target_role: targetRole }),
        });
        if (!res.ok) throw new Error('Failed to setup profile');
        return res.json();
    },
};
