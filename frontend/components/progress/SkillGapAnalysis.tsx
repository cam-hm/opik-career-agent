"use client";

import {
    TrendingUp,
    TrendingDown,
    AlertTriangle,
    CheckCircle,
    Lightbulb,
    BarChart3,
} from "lucide-react";

interface SkillGap {
    skill: string;
    current: number;
    target: number;
    gap: number;
    verified?: boolean;
    evidence?: string;
}

interface SkillGapData {
    user_id: string;
    target_role?: string;
    current_skills: Record<string, number>;
    target_requirements: Record<string, number>;
    verified_skills: string[];
    gaps: SkillGap[];
    strengths: SkillGap[];
    identified_gaps_from_interviews: string[];
    recommendations: string[];
    analyzed_at?: string;
}

interface Props {
    data: SkillGapData | null;
    loading?: boolean;
}

export default function SkillGapAnalysis({ data, loading }: Props) {
    if (loading) {
        return (
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700/60 p-5">
                <div className="animate-pulse space-y-4">
                    <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-1/3"></div>
                    <div className="space-y-3">
                        {[1, 2, 3].map((i) => (
                            <div key={i} className="h-12 bg-gray-200 dark:bg-gray-700 rounded"></div>
                        ))}
                    </div>
                </div>
            </div>
        );
    }

    if (!data || (data.gaps.length === 0 && data.strengths.length === 0)) {
        return (
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700/60 p-5">
                <div className="flex items-center gap-2 mb-4">
                    <BarChart3 className="w-5 h-5 text-[#424874] dark:text-[#A6B1E1]" />
                    <h2 className="font-semibold text-gray-800 dark:text-gray-100">
                        Skill Gap Analysis
                    </h2>
                </div>
                <div className="text-center py-8">
                    <BarChart3 className="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-3" />
                    <p className="text-gray-500 dark:text-gray-400">
                        Complete more interviews to see skill gap analysis
                    </p>
                </div>
            </div>
        );
    }

    const getPriorityColor = (priority: string) => {
        switch (priority) {
            case "high":
                return "text-red-500 bg-red-50 dark:bg-red-900/20";
            case "medium":
                return "text-amber-500 bg-amber-50 dark:bg-amber-900/20";
            case "low":
                return "text-blue-500 bg-blue-50 dark:bg-blue-900/20";
            default:
                return "text-gray-500 bg-gray-50 dark:bg-gray-700";
        }
    };

    return (
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700/60 overflow-hidden">
            <div className="px-5 py-4 border-b border-gray-200 dark:border-gray-700/60">
                <div className="flex items-center gap-2">
                    <BarChart3 className="w-5 h-5 text-[#424874] dark:text-[#A6B1E1]" />
                    <h2 className="font-semibold text-gray-800 dark:text-gray-100">
                        Skill Gap Analysis
                    </h2>
                </div>
                {data.target_role && (
                    <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                        Compared to: {data.target_role}
                    </p>
                )}
            </div>

            <div className="p-5 space-y-6">
                {/* Skills to Improve */}
                {data.gaps.length > 0 && (
                    <div>
                        <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3 flex items-center gap-2">
                            <TrendingUp className="w-4 h-4 text-amber-500" />
                            Areas to Improve
                        </h3>
                        <div className="space-y-3">
                            {data.gaps.map((gap, index) => {
                                const priority = gap.gap > 30 ? 'high' : gap.gap > 20 ? 'medium' : 'low';
                                return (
                                    <div key={index} className="space-y-1.5">
                                        <div className="flex items-center justify-between">
                                            <span className="text-sm text-gray-700 dark:text-gray-300 capitalize">
                                                {gap.skill.replace(/_/g, ' ')}
                                            </span>
                                            <div className="flex items-center gap-2">
                                                <span className={`text-xs px-2 py-0.5 rounded-full ${getPriorityColor(priority)}`}>
                                                    {priority}
                                                </span>
                                                <span className="text-xs text-gray-500 dark:text-gray-400">
                                                    {gap.current} / {gap.target}
                                                </span>
                                            </div>
                                        </div>
                                        <div className="relative h-2 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden">
                                            {/* Current level */}
                                            <div
                                                className="absolute h-full bg-[#424874] rounded-full"
                                                style={{ width: `${(gap.current / gap.target) * 100}%` }}
                                            />
                                            {/* Target indicator */}
                                            <div
                                                className="absolute h-full w-0.5 bg-amber-500"
                                                style={{ left: '100%', transform: 'translateX(-100%)' }}
                                            />
                                        </div>
                                        <p className="text-xs text-gray-500 dark:text-gray-400">
                                            Gap: {gap.gap} points to reach target
                                        </p>
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                )}

                {/* Strengths */}
                {data.strengths.length > 0 && (
                    <div>
                        <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3 flex items-center gap-2">
                            <CheckCircle className="w-4 h-4 text-green-500" />
                            Your Strengths
                        </h3>
                        <div className="flex flex-wrap gap-2">
                            {data.strengths.map((strength, index) => (
                                <span
                                    key={index}
                                    className="inline-flex items-center gap-1 px-3 py-1.5 bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-400 text-sm rounded-full"
                                >
                                    <CheckCircle className="w-3.5 h-3.5" />
                                    <span className="capitalize">{strength.skill.replace(/_/g, ' ')}</span>
                                    <span className="text-xs opacity-75">({strength.current})</span>
                                </span>
                            ))}
                        </div>
                    </div>
                )}

                {/* Recommendations */}
                {data.recommendations.length > 0 && (
                    <div>
                        <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3 flex items-center gap-2">
                            <Lightbulb className="w-4 h-4 text-amber-500" />
                            Recommendations
                        </h3>
                        <ul className="space-y-2">
                            {data.recommendations.map((rec, index) => (
                                <li
                                    key={index}
                                    className="flex items-start gap-2 text-sm text-gray-600 dark:text-gray-400"
                                >
                                    <span className="w-5 h-5 flex items-center justify-center rounded-full bg-amber-100 dark:bg-amber-900/20 text-amber-600 dark:text-amber-400 text-xs flex-shrink-0 mt-0.5">
                                        {index + 1}
                                    </span>
                                    {rec}
                                </li>
                            ))}
                        </ul>
                    </div>
                )}
            </div>
        </div>
    );
}
