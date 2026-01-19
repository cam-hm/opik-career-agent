"use client";

import { useUser, useAuth } from "@clerk/nextjs";
import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import {
    Loader2,
    TrendingUp,
    Target,
    Calendar,
    Award,
    ArrowUpRight,
    ArrowDownRight,
    Minus,
    ExternalLink,
    Activity,
    Sparkles
} from "lucide-react";
import { fetchWithAuth } from "@/lib/api";
import { ENDPOINTS } from "@/lib/endpoints";
import {
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    Area,
    AreaChart
} from "recharts";
import ResolutionTracker from "@/components/progress/ResolutionTracker";
import SkillGapAnalysis from "@/components/progress/SkillGapAnalysis";
import WeeklyInsights from "@/components/progress/WeeklyInsights";
import { getOpikDashboardUrl, getOpikTraceUrl } from "@/lib/opik";

interface InterviewSession {
    session_id: string;
    job_role: string;
    status: string;
    created_at: string;
    overall_score?: number;
    stage_type?: string;
    opik_trace_id?: string;
}

interface Resolution {
    id: string;
    title: string;
    description?: string;
    target_role?: string;
    target_skills: Record<string, number>;
    baseline_skills: Record<string, number>;
    target_date?: string;
    status: string;
    created_at?: string;
}

interface ResolutionProgress {
    resolution_id: string;
    title: string;
    overall_progress: number;
    skill_progress: Record<string, {
        baseline: number;
        current: number;
        target: number;
        progress_percent: number;
    }>;
    days_remaining?: number;
    status: string;
}

interface SkillGapData {
    user_id: string;
    target_role?: string;
    current_skills: Record<string, number>;
    target_requirements: Record<string, number>;
    verified_skills: string[];
    gaps: Array<{
        skill: string;
        current: number;
        target: number;
        gap: number;
        verified?: boolean;
        evidence?: string;
    }>;
    strengths: Array<{
        skill: string;
        current: number;
        target: number;
        gap: number;
    }>;
    identified_gaps_from_interviews: string[];
    recommendations: string[];
    analyzed_at?: string;
}

interface WeeklyInsightsData {
    user_id: string;
    period: string;
    period_start: string;
    period_end: string;
    sessions_count: number;
    average_score: number | null;
    score_trend?: number | null;
    trend_direction: "up" | "down" | "stable";
    competencies: Record<string, number>;
    strengths: string[];
    areas_to_improve: string[];
    recommendations: string[];
    highlights: string[];
    generated_at?: string;
    message?: string;
}

export default function ProgressPage() {
    const { user, isLoaded, isSignedIn } = useUser();
    const { getToken } = useAuth();
    const [sessions, setSessions] = useState<InterviewSession[]>([]);
    const [resolutions, setResolutions] = useState<Resolution[]>([]);
    const [resolutionProgress, setResolutionProgress] = useState<ResolutionProgress[]>([]);
    const [skillGapData, setSkillGapData] = useState<SkillGapData | null>(null);
    const [weeklyInsights, setWeeklyInsights] = useState<WeeklyInsightsData | null>(null);
    const [loading, setLoading] = useState(true);
    const [loadingInsights, setLoadingInsights] = useState(false);
    const [loadingSkillGap, setLoadingSkillGap] = useState(false);

    const fetchResolutions = useCallback(async () => {
        try {
            const res = await fetchWithAuth(ENDPOINTS.PROGRESS.RESOLUTIONS, {}, getToken);
            if (res.ok) {
                const data = await res.json();
                const resolutionsList = data.resolutions || [];
                setResolutions(resolutionsList);

                // Fetch progress for each resolution
                const progressPromises = resolutionsList.map(async (r: Resolution) => {
                    const progressRes = await fetchWithAuth(
                        ENDPOINTS.PROGRESS.RESOLUTION_DETAIL(r.id),
                        {},
                        getToken
                    );
                    if (progressRes.ok) {
                        return progressRes.json();
                    }
                    return null;
                });

                const progressResults = await Promise.all(progressPromises);
                setResolutionProgress(progressResults.filter(Boolean));
            }
        } catch (error) {
            console.error("Failed to fetch resolutions:", error);
        }
    }, [getToken]);

    const fetchSkillGap = useCallback(async () => {
        setLoadingSkillGap(true);
        try {
            const res = await fetchWithAuth(ENDPOINTS.PROGRESS.SKILL_GAP, {}, getToken);
            if (res.ok) {
                const data = await res.json();
                setSkillGapData(data);
            }
        } catch (error) {
            console.error("Failed to fetch skill gap:", error);
        } finally {
            setLoadingSkillGap(false);
        }
    }, [getToken]);

    const fetchWeeklyInsights = useCallback(async () => {
        setLoadingInsights(true);
        try {
            const res = await fetchWithAuth(ENDPOINTS.PROGRESS.WEEKLY_INSIGHTS, {}, getToken);
            if (res.ok) {
                const data = await res.json();
                setWeeklyInsights(data);
            }
        } catch (error) {
            console.error("Failed to fetch weekly insights:", error);
        } finally {
            setLoadingInsights(false);
        }
    }, [getToken]);

    useEffect(() => {
        if (isLoaded && isSignedIn && user) {
            fetchData();
        } else if (isLoaded && !isSignedIn) {
            setLoading(false);
        }
    }, [isLoaded, isSignedIn, user]);

    const fetchData = async () => {
        try {
            // Fetch sessions
            const res = await fetchWithAuth(ENDPOINTS.INTERVIEW.LIST, {}, getToken);
            if (res.ok) {
                const data = await res.json();
                const sorted = data.sort((a: InterviewSession, b: InterviewSession) =>
                    new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
                );
                setSessions(sorted);
            }

            // Fetch other data in parallel
            await Promise.all([
                fetchResolutions(),
                fetchSkillGap(),
                fetchWeeklyInsights(),
            ]);
        } catch (error) {
            console.error("Failed to fetch data:", error);
        } finally {
            setLoading(false);
        }
    };

    if (!isLoaded || loading) {
        return (
            <div className="flex h-[50vh] items-center justify-center">
                <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
            </div>
        );
    }

    if (!isSignedIn) {
        return (
            <div className="flex h-[50vh] flex-col items-center justify-center gap-4">
                <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-100">Sign in to view progress</h2>
                <p className="text-gray-500 dark:text-gray-400">Track your interview performance over time</p>
            </div>
        );
    }

    // Calculate statistics
    const completedSessions = sessions.filter(s => s.overall_score !== null && s.overall_score !== undefined);
    const totalSessions = completedSessions.length;
    const avgScore = totalSessions > 0
        ? Math.round(completedSessions.reduce((acc, s) => acc + (s.overall_score || 0), 0) / totalSessions)
        : 0;

    // Calculate improvement
    let improvement = 0;
    let improvementDirection: 'up' | 'down' | 'neutral' = 'neutral';
    if (completedSessions.length >= 4) {
        const firstHalf = completedSessions.slice(0, Math.floor(completedSessions.length / 2));
        const secondHalf = completedSessions.slice(Math.floor(completedSessions.length / 2));
        const firstAvg = firstHalf.reduce((acc, s) => acc + (s.overall_score || 0), 0) / firstHalf.length;
        const secondAvg = secondHalf.reduce((acc, s) => acc + (s.overall_score || 0), 0) / secondHalf.length;
        improvement = Math.round(secondAvg - firstAvg);
        improvementDirection = improvement > 0 ? 'up' : improvement < 0 ? 'down' : 'neutral';
    }

    // Prepare chart data
    const chartData = completedSessions.map((session, index) => ({
        name: new Date(session.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        score: session.overall_score || 0,
        session: index + 1
    }));

    // Best score
    const bestScore = totalSessions > 0
        ? Math.max(...completedSessions.map(s => s.overall_score || 0))
        : 0;

    // Count sessions with Opik traces
    const trackedSessionsCount = sessions.filter(s => s.opik_trace_id).length;

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700/60 overflow-hidden">
                <div className="px-5 py-5">
                    <h1 className="text-2xl font-serif font-bold text-gray-800 dark:text-gray-100 italic">
                        Your Progress
                    </h1>
                    <p className="text-sm text-gray-500 dark:text-gray-400 mt-1 font-medium tracking-wide">
                        Track your 2026 career resolutions and interview performance
                    </p>
                </div>
            </div>

            {/* Stats Row */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700/60 p-4">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-lg bg-[#DCD6F7] dark:bg-[#424874]/20 flex items-center justify-center">
                            <Calendar className="w-5 h-5 text-[#424874] dark:text-[#A6B1E1]" />
                        </div>
                        <div>
                            <p className="text-2xl font-bold text-gray-800 dark:text-gray-100">{totalSessions}</p>
                            <p className="text-xs text-gray-500 dark:text-gray-400">Total Sessions</p>
                        </div>
                    </div>
                </div>

                <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700/60 p-4">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-lg bg-blue-100 dark:bg-blue-500/20 flex items-center justify-center">
                            <Target className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                        </div>
                        <div>
                            <p className="text-2xl font-bold text-gray-800 dark:text-gray-100">{avgScore || '-'}</p>
                            <p className="text-xs text-gray-500 dark:text-gray-400">Average Score</p>
                        </div>
                    </div>
                </div>

                <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700/60 p-4">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-lg bg-amber-100 dark:bg-amber-500/20 flex items-center justify-center">
                            <Award className="w-5 h-5 text-amber-600 dark:text-amber-400" />
                        </div>
                        <div>
                            <p className="text-2xl font-bold text-gray-800 dark:text-gray-100">{bestScore || '-'}</p>
                            <p className="text-xs text-gray-500 dark:text-gray-400">Best Score</p>
                        </div>
                    </div>
                </div>

                <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700/60 p-4">
                    <div className="flex items-center gap-3">
                        <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                            improvementDirection === 'up'
                                ? 'bg-green-100 dark:bg-green-500/20'
                                : improvementDirection === 'down'
                                    ? 'bg-red-100 dark:bg-red-500/20'
                                    : 'bg-gray-100 dark:bg-gray-500/20'
                        }`}>
                            {improvementDirection === 'up' ? (
                                <ArrowUpRight className="w-5 h-5 text-green-600 dark:text-green-400" />
                            ) : improvementDirection === 'down' ? (
                                <ArrowDownRight className="w-5 h-5 text-red-600 dark:text-red-400" />
                            ) : (
                                <Minus className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                            )}
                        </div>
                        <div>
                            <p className={`text-2xl font-bold ${
                                improvementDirection === 'up'
                                    ? 'text-green-600 dark:text-green-400'
                                    : improvementDirection === 'down'
                                        ? 'text-red-600 dark:text-red-400'
                                        : 'text-gray-800 dark:text-gray-100'
                            }`}>
                                {improvement > 0 ? '+' : ''}{improvement || '-'}
                            </p>
                            <p className="text-xs text-gray-500 dark:text-gray-400">Improvement</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Opik Observability Banner */}
            {trackedSessionsCount > 0 && (
                <div className="bg-gradient-to-r from-[#424874]/5 via-[#A6B1E1]/10 to-[#424874]/5 dark:from-[#424874]/20 dark:via-[#A6B1E1]/15 dark:to-[#424874]/20 rounded-lg border border-[#424874]/20 dark:border-[#A6B1E1]/20 p-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                            <div className="w-12 h-12 rounded-xl bg-white dark:bg-gray-800 border border-[#424874]/20 dark:border-[#A6B1E1]/20 flex items-center justify-center">
                                <Activity className="w-6 h-6 text-[#424874] dark:text-[#A6B1E1]" />
                            </div>
                            <div>
                                <div className="flex items-center gap-2">
                                    <h3 className="font-semibold text-gray-800 dark:text-gray-100">
                                        AI Observability
                                    </h3>
                                    <span className="flex items-center gap-1 text-xs text-[#424874] dark:text-[#A6B1E1] bg-white dark:bg-gray-800 px-2 py-0.5 rounded-full border border-[#424874]/20 dark:border-[#A6B1E1]/20">
                                        <Sparkles className="w-3 h-3" />
                                        Powered by Opik
                                    </span>
                                </div>
                                <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5">
                                    {trackedSessionsCount} interview{trackedSessionsCount !== 1 ? 's' : ''} with full AI tracing and evaluation
                                </p>
                            </div>
                        </div>
                        <a
                            href={getOpikDashboardUrl()}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center gap-2 px-4 py-2 bg-[#424874] hover:bg-[#363B5E] text-white text-sm font-medium rounded-lg transition-colors"
                        >
                            <ExternalLink className="w-4 h-4" />
                            Open Opik Dashboard
                        </a>
                    </div>
                </div>
            )}

            {/* Resolution Tracker */}
            <ResolutionTracker
                resolutions={resolutions}
                resolutionProgress={resolutionProgress}
                onRefresh={fetchResolutions}
            />

            {/* Two Column Layout: Weekly Insights + Skill Gap */}
            <div className="grid lg:grid-cols-2 gap-6">
                <WeeklyInsights data={weeklyInsights} loading={loadingInsights} />
                <SkillGapAnalysis data={skillGapData} loading={loadingSkillGap} />
            </div>

            {/* Chart */}
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700/60 p-5">
                <h2 className="font-semibold text-gray-800 dark:text-gray-100 mb-4 flex items-center gap-2">
                    <TrendingUp className="w-4 h-4" /> Score Progression
                </h2>
                {chartData.length > 0 ? (
                    <div className="h-[300px]">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={chartData}>
                                <defs>
                                    <linearGradient id="scoreGradient" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#424874" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="#424874" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                                <XAxis
                                    dataKey="name"
                                    tick={{ fontSize: 12, fill: '#6b7280' }}
                                    axisLine={{ stroke: '#e5e7eb' }}
                                />
                                <YAxis
                                    domain={[0, 100]}
                                    tick={{ fontSize: 12, fill: '#6b7280' }}
                                    axisLine={{ stroke: '#e5e7eb' }}
                                />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: 'white',
                                        border: '1px solid #e5e7eb',
                                        borderRadius: '8px',
                                        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                                    }}
                                    formatter={(value) => [`${value ?? 0} points`, 'Score']}
                                />
                                <Area
                                    type="monotone"
                                    dataKey="score"
                                    stroke="#424874"
                                    strokeWidth={2}
                                    fill="url(#scoreGradient)"
                                />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                ) : (
                    <div className="h-[300px] flex items-center justify-center">
                        <div className="text-center">
                            <TrendingUp className="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-3" />
                            <p className="text-gray-500 dark:text-gray-400">
                                Complete interviews to see your progress chart
                            </p>
                            <Link
                                href="/practice/new"
                                className="inline-block mt-3 text-sm text-[#424874] hover:text-[#363B5E] dark:text-[#A6B1E1] font-medium"
                            >
                                Start your first practice session
                            </Link>
                        </div>
                    </div>
                )}
            </div>

            {/* Recent Sessions with Opik Links */}
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700/60 overflow-hidden">
                <div className="px-5 py-4 border-b border-gray-200 dark:border-gray-700/60">
                    <h2 className="font-semibold text-gray-800 dark:text-gray-100">Session History</h2>
                </div>
                {completedSessions.length > 0 ? (
                    <div className="divide-y divide-gray-100 dark:divide-gray-700/60">
                        {[...completedSessions].reverse().slice(0, 10).map((session) => (
                            <div
                                key={session.session_id}
                                className="flex items-center gap-4 px-5 py-3 hover:bg-gray-50 dark:hover:bg-gray-700/30 transition-colors"
                            >
                                <div className="flex-1 min-w-0">
                                    <p className="font-medium text-gray-800 dark:text-gray-100 truncate">
                                        {session.job_role}
                                    </p>
                                    <p className="text-xs text-gray-500 dark:text-gray-400">
                                        {new Date(session.created_at).toLocaleDateString('en-US', {
                                            weekday: 'short',
                                            month: 'short',
                                            day: 'numeric',
                                            hour: '2-digit',
                                            minute: '2-digit'
                                        })}
                                        {session.stage_type && (
                                            <span className="ml-2 px-1.5 py-0.5 bg-gray-100 dark:bg-gray-700 rounded text-[10px] uppercase">
                                                {session.stage_type}
                                            </span>
                                        )}
                                    </p>
                                </div>
                                <div className={`text-lg font-bold ${getScoreColor(session.overall_score || 0)}`}>
                                    {session.overall_score}
                                </div>
                                <div className="flex gap-2">
                                    <Link
                                        href={`/interview/${session.session_id}/feedback`}
                                        className="px-3 py-1.5 text-xs text-[#424874] dark:text-[#A6B1E1] border border-[#424874]/30 dark:border-[#A6B1E1]/30 rounded hover:bg-[#424874]/5 dark:hover:bg-[#A6B1E1]/5 transition-colors"
                                    >
                                        View Feedback
                                    </Link>
                                    {session.opik_trace_id && (
                                        <a
                                            href={getOpikTraceUrl(session.opik_trace_id)}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="flex items-center gap-1 px-2 py-1.5 text-xs text-gray-500 dark:text-gray-400 border border-gray-200 dark:border-gray-600 rounded hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                                            title="View AI Trace on Opik"
                                        >
                                            <ExternalLink className="w-3 h-3" />
                                            Trace
                                        </a>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="text-center py-10 px-5">
                        <Calendar className="w-10 h-10 text-gray-300 dark:text-gray-600 mx-auto mb-3" />
                        <p className="text-sm text-gray-500 dark:text-gray-400">No sessions yet</p>
                    </div>
                )}
            </div>
        </div>
    );
}

function getScoreColor(score: number) {
    if (score >= 80) return "text-green-600 dark:text-green-400";
    if (score >= 60) return "text-yellow-600 dark:text-yellow-400";
    return "text-red-600 dark:text-red-400";
}
