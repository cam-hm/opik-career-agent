"use client";

import {
    Sparkles,
    TrendingUp,
    TrendingDown,
    Minus,
    Calendar,
    Award,
    AlertCircle,
    CheckCircle,
    Target,
} from "lucide-react";

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

interface Props {
    data: WeeklyInsightsData | null;
    loading?: boolean;
}

export default function WeeklyInsights({ data, loading }: Props) {
    if (loading) {
        return (
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700/60 p-5">
                <div className="animate-pulse space-y-4">
                    <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-1/3"></div>
                    <div className="space-y-3">
                        {[1, 2, 3].map((i) => (
                            <div key={i} className="h-8 bg-gray-200 dark:bg-gray-700 rounded"></div>
                        ))}
                    </div>
                </div>
            </div>
        );
    }

    if (!data || data.sessions_count === 0) {
        return (
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700/60 p-5">
                <div className="flex items-center gap-2 mb-4">
                    <Sparkles className="w-5 h-5 text-[#424874] dark:text-[#A6B1E1]" />
                    <h2 className="font-semibold text-gray-800 dark:text-gray-100">
                        Weekly Insights
                    </h2>
                </div>
                <div className="text-center py-8">
                    <Calendar className="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-3" />
                    <p className="text-gray-500 dark:text-gray-400">
                        No sessions this week yet
                    </p>
                    <p className="text-sm text-gray-400 dark:text-gray-500 mt-1">
                        Complete interviews to get AI-powered insights
                    </p>
                </div>
            </div>
        );
    }

    const TrendIcon = data.trend_direction === "up" ? TrendingUp :
        data.trend_direction === "down" ? TrendingDown : Minus;

    const trendColor = data.trend_direction === "up"
        ? "text-green-500"
        : data.trend_direction === "down"
            ? "text-red-500"
            : "text-gray-400";

    return (
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700/60 overflow-hidden">
            <div className="px-5 py-4 border-b border-gray-200 dark:border-gray-700/60">
                <div className="flex items-center gap-2">
                    <Sparkles className="w-5 h-5 text-[#424874] dark:text-[#A6B1E1]" />
                    <h2 className="font-semibold text-gray-800 dark:text-gray-100">
                        Weekly Insights
                    </h2>
                </div>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    {new Date(data.period_start).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                    {' - '}
                    {new Date(data.period_end).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                </p>
            </div>

            <div className="p-5 space-y-5">
                {/* Summary Stats */}
                <div className="grid grid-cols-3 gap-4">
                    <div className="text-center">
                        <p className="text-2xl font-bold text-gray-800 dark:text-gray-100">
                            {data.sessions_count}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">Sessions</p>
                    </div>
                    <div className="text-center">
                        <p className="text-2xl font-bold text-gray-800 dark:text-gray-100">
                            {data.average_score !== null ? data.average_score : '-'}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">Avg Score</p>
                    </div>
                    <div className="text-center">
                        <div className={`inline-flex items-center gap-1 ${trendColor}`}>
                            <TrendIcon className="w-5 h-5" />
                            {data.score_trend !== undefined && data.score_trend !== null && (
                                <span className="text-lg font-bold">
                                    {data.score_trend > 0 ? '+' : ''}{data.score_trend}
                                </span>
                            )}
                        </div>
                        <p className="text-xs text-gray-500 dark:text-gray-400">Trend</p>
                    </div>
                </div>

                {/* Message (if no sessions) */}
                {data.message && (
                    <div className="bg-gradient-to-r from-[#424874]/5 to-[#A6B1E1]/5 dark:from-[#424874]/10 dark:to-[#A6B1E1]/10 rounded-lg p-4 border border-[#424874]/10 dark:border-[#A6B1E1]/10">
                        <div className="flex items-start gap-2">
                            <Sparkles className="w-4 h-4 text-[#424874] dark:text-[#A6B1E1] flex-shrink-0 mt-0.5" />
                            <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
                                {data.message}
                            </p>
                        </div>
                    </div>
                )}

                {/* Strengths */}
                {data.strengths && data.strengths.length > 0 && (
                    <div>
                        <h3 className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2 flex items-center gap-1">
                            <Award className="w-3.5 h-3.5" />
                            Strengths
                        </h3>
                        <div className="flex flex-wrap gap-2">
                            {data.strengths.map((strength, index) => (
                                <span
                                    key={index}
                                    className="inline-flex items-center gap-1 px-2.5 py-1 bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-400 text-xs rounded-full"
                                >
                                    <CheckCircle className="w-3 h-3" />
                                    {strength}
                                </span>
                            ))}
                        </div>
                    </div>
                )}

                {/* Areas to Improve */}
                {data.areas_to_improve && data.areas_to_improve.length > 0 && (
                    <div>
                        <h3 className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2 flex items-center gap-1">
                            <Target className="w-3.5 h-3.5" />
                            Focus Areas
                        </h3>
                        <div className="flex flex-wrap gap-2">
                            {data.areas_to_improve.map((area, index) => (
                                <span
                                    key={index}
                                    className="inline-flex items-center gap-1 px-2.5 py-1 bg-amber-50 dark:bg-amber-900/20 text-amber-700 dark:text-amber-400 text-xs rounded-full"
                                >
                                    <AlertCircle className="w-3 h-3" />
                                    {area}
                                </span>
                            ))}
                        </div>
                    </div>
                )}

                {/* Highlights */}
                {data.highlights && data.highlights.length > 0 && (
                    <div>
                        <h3 className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">
                            Highlights
                        </h3>
                        <ul className="space-y-1.5">
                            {data.highlights.map((highlight, index) => (
                                <li
                                    key={index}
                                    className="flex items-start gap-2 text-sm text-gray-600 dark:text-gray-400"
                                >
                                    <span className="w-1.5 h-1.5 rounded-full bg-[#424874] dark:bg-[#A6B1E1] mt-1.5 flex-shrink-0" />
                                    {highlight}
                                </li>
                            ))}
                        </ul>
                    </div>
                )}
            </div>
        </div>
    );
}
