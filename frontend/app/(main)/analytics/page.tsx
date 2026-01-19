"use client";

import { useUser, useAuth } from "@clerk/nextjs";
import { useEffect, useState, useCallback } from "react";
import {
    Loader2,
    BarChart3,
    Activity,
    Sparkles,
    ExternalLink,
    TrendingUp,
    TrendingDown,
    Minus,
    Calendar
} from "lucide-react";
import { fetchWithAuth } from "@/lib/api";
import { ENDPOINTS } from "@/lib/endpoints";
import { getOpikDashboardUrl } from "@/lib/opik";
import OverviewStats from "@/components/analytics/OverviewStats";
import EvaluationChart from "@/components/analytics/EvaluationChart";
import ComponentBreakdown from "@/components/analytics/ComponentBreakdown";

interface OverviewMetrics {
    total_sessions: number;
    avg_score: number | null;
    opik_tracked_sessions: number;
    opik_coverage_percent: number;
    stage_distribution: Record<string, number>;
    score_trend: "up" | "down" | "stable" | "no_data";
    date_range_days: number;
}

interface SessionSummary {
    session_id: string;
    job_role: string | null;
    stage_type: string | null;
    overall_score: number | null;
    created_at: string | null;
    opik_trace_id: string | null;
}

interface EvaluationMetrics {
    avg_scores_by_stage: Record<string, number>;
    competency_breakdown: Record<string, number>;
    score_distribution: Record<string, number>;
    recent_sessions: SessionSummary[];
}

interface ComponentMetrics {
    total_sessions_analyzed: number;
    total_turns: number;
    estimated_llm_calls: number;
    components_used: string[];
    note: string;
}

export default function AnalyticsPage() {
    const { user, isLoaded, isSignedIn } = useUser();
    const { getToken } = useAuth();
    const [overviewMetrics, setOverviewMetrics] = useState<OverviewMetrics | null>(null);
    const [evaluationMetrics, setEvaluationMetrics] = useState<EvaluationMetrics | null>(null);
    const [componentMetrics, setComponentMetrics] = useState<ComponentMetrics | null>(null);
    const [loading, setLoading] = useState(true);
    const [dateRange, setDateRange] = useState<number>(30);

    const fetchAllData = useCallback(async () => {
        setLoading(true);
        try {
            const [overviewRes, evaluationRes, componentRes] = await Promise.all([
                fetchWithAuth(`${ENDPOINTS.ANALYTICS.OVERVIEW}?days=${dateRange}`, {}, getToken),
                fetchWithAuth(`${ENDPOINTS.ANALYTICS.EVALUATION}?days=${dateRange}`, {}, getToken),
                fetchWithAuth(`${ENDPOINTS.ANALYTICS.COMPONENTS}?days=${dateRange}`, {}, getToken),
            ]);

            if (overviewRes.ok) {
                const data = await overviewRes.json();
                setOverviewMetrics(data);
            }

            if (evaluationRes.ok) {
                const data = await evaluationRes.json();
                setEvaluationMetrics(data);
            }

            if (componentRes.ok) {
                const data = await componentRes.json();
                setComponentMetrics(data);
            }
        } catch (error) {
            console.error("Failed to fetch analytics:", error);
        } finally {
            setLoading(false);
        }
    }, [getToken, dateRange]);

    useEffect(() => {
        if (isLoaded && isSignedIn) {
            fetchAllData();
        } else if (isLoaded && !isSignedIn) {
            setLoading(false);
        }
    }, [isLoaded, isSignedIn, fetchAllData]);

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
                <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-100">Sign in to view analytics</h2>
                <p className="text-gray-500 dark:text-gray-400">Track AI performance and evaluation metrics</p>
            </div>
        );
    }

    const trendIcon = overviewMetrics?.score_trend === "up" ? (
        <TrendingUp className="w-4 h-4 text-green-500" />
    ) : overviewMetrics?.score_trend === "down" ? (
        <TrendingDown className="w-4 h-4 text-red-500" />
    ) : (
        <Minus className="w-4 h-4 text-gray-500" />
    );

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700/60 overflow-hidden">
                <div className="px-5 py-5">
                    <div className="flex items-center justify-between">
                        <div>
                            <h1 className="text-2xl font-serif font-bold text-gray-800 dark:text-gray-100 italic flex items-center gap-2">
                                <BarChart3 className="w-6 h-6" />
                                AI Observability Analytics
                            </h1>
                            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1 font-medium tracking-wide">
                                LLM performance, evaluation metrics, and system health powered by Opik
                            </p>
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
            </div>

            {/* Date Range Selector */}
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700/60 p-4">
                <div className="flex items-center gap-4">
                    <Calendar className="w-5 h-5 text-gray-500 dark:text-gray-400" />
                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Date Range:</span>
                    <div className="flex gap-2">
                        {[7, 30, 90, 365].map((days) => (
                            <button
                                key={days}
                                onClick={() => setDateRange(days)}
                                className={`px-3 py-1.5 text-sm rounded-lg transition-colors ${
                                    dateRange === days
                                        ? "bg-[#424874] text-white"
                                        : "bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600"
                                }`}
                            >
                                {days === 365 ? "1 Year" : `${days} Days`}
                            </button>
                        ))}
                    </div>
                </div>
            </div>

            {/* Overview Stats */}
            {overviewMetrics && <OverviewStats metrics={overviewMetrics} trendIcon={trendIcon} />}

            {/* Opik Integration Banner */}
            {overviewMetrics && overviewMetrics.opik_tracked_sessions > 0 && (
                <div className="bg-gradient-to-r from-[#424874]/5 via-[#A6B1E1]/10 to-[#424874]/5 dark:from-[#424874]/20 dark:via-[#A6B1E1]/15 dark:to-[#424874]/20 rounded-lg border border-[#424874]/20 dark:border-[#A6B1E1]/20 p-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                            <div className="w-12 h-12 rounded-xl bg-white dark:bg-gray-800 border border-[#424874]/20 dark:border-[#A6B1E1]/20 flex items-center justify-center">
                                <Activity className="w-6 h-6 text-[#424874] dark:text-[#A6B1E1]" />
                            </div>
                            <div>
                                <div className="flex items-center gap-2">
                                    <h3 className="font-semibold text-gray-800 dark:text-gray-100">
                                        Full Observability Pipeline
                                    </h3>
                                    <span className="flex items-center gap-1 text-xs text-[#424874] dark:text-[#A6B1E1] bg-white dark:bg-gray-800 px-2 py-0.5 rounded-full border border-[#424874]/20 dark:border-[#A6B1E1]/20">
                                        <Sparkles className="w-3 h-3" />
                                        Powered by Opik
                                    </span>
                                </div>
                                <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5">
                                    {overviewMetrics.opik_coverage_percent.toFixed(0)}% coverage • {overviewMetrics.opik_tracked_sessions} sessions with full AI tracing
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Evaluation Metrics */}
            {evaluationMetrics && <EvaluationChart metrics={evaluationMetrics} />}

            {/* Component Metrics */}
            {componentMetrics && <ComponentBreakdown metrics={componentMetrics} />}

            {/* No Data State */}
            {overviewMetrics?.total_sessions === 0 && (
                <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700/60 p-10 text-center">
                    <BarChart3 className="w-16 h-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-2">
                        No Analytics Data Yet
                    </h3>
                    <p className="text-gray-500 dark:text-gray-400 mb-4">
                        Complete interview sessions to see AI performance metrics and evaluation insights
                    </p>
                </div>
            )}
        </div>
    );
}
