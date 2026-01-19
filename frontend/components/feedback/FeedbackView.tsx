"use client";

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { CheckCircle, Trophy, TrendingUp, AlertCircle, MessageSquare, ExternalLink, Activity, BarChart3, Sparkles } from 'lucide-react';
import { getScoreColor, getScoreBg } from "@/lib/design-tokens";
import { useLanguage } from '@/contexts/LanguageContext';
import { getOpikTraceUrl } from "@/lib/opik";

interface CompetencyScore {
    score: number;
    rubric_level?: string;
}

interface Feedback {
    score: number;
    summary: string;
    pros: string[];
    cons: string[];
    feedback: string;
    opik_trace_id?: string;
    competency_scores?: Record<string, CompetencyScore>;
    skill_assessments?: Array<{
        turn: number;
        score: number;
        dimension?: string;
    }>;
}

interface FeedbackViewProps {
    feedback: Feedback;
    sessionDetails: {
        application_id?: string;
    } | null;
}

export default function FeedbackView({ feedback, sessionDetails }: FeedbackViewProps) {
    const { t } = useLanguage();
    const router = useRouter();

    const hasPros = feedback.pros && feedback.pros.length > 0 && feedback.pros.some(p => p.trim().length > 0);
    const hasCons = feedback.cons && feedback.cons.length > 0 && feedback.cons.some(c => c.trim().length > 0);
    const hasDetailedFeedback = feedback.feedback && feedback.feedback.trim().length > 0;

    return (
        <div className="grid gap-6 lg:grid-cols-3">
            {/* Score Card */}
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700/60 p-5">
                <div className={`${getScoreBg(feedback.score)} rounded-lg p-6 text-center`}>
                    <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">{t('feedback.score')}</p>
                    <p className={`text-5xl font-bold ${getScoreColor(feedback.score)}`}>{feedback.score}</p>
                    <div className="flex items-center justify-center gap-2 mt-2">
                        <Trophy className={`w-4 h-4 ${feedback.score >= 70 ? 'text-yellow-500' : 'text-gray-400'}`} />
                        <span className="text-sm text-gray-500 dark:text-gray-400">/100</span>
                    </div>
                </div>
                {sessionDetails?.application_id && (
                    <button
                        onClick={() => router.push(`/applications/${sessionDetails.application_id}`)}
                        className="w-full mt-4 py-2.5 bg-[#424874] hover:bg-[#363B5E] text-white rounded-md font-medium transition-colors"
                    >
                        {t('feedback.continueApp')}
                    </button>
                )}
            </div>

            {/* Summary */}
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700/60 p-5 lg:col-span-2">
                <h3 className="flex items-center gap-2 font-semibold text-gray-800 dark:text-gray-100 mb-4">
                    <TrendingUp className="w-4 h-4" /> {t('feedback.executiveSummary')}
                </h3>
                <p className="text-gray-600 dark:text-gray-300 leading-relaxed">{feedback.summary}</p>
            </div>

            {/* Strengths */}
            <div className={`rounded-lg p-5 border min-h-[180px] ${hasPros
                ? 'bg-green-50 dark:bg-green-500/10 border-green-200 dark:border-green-500/30'
                : 'bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700/60'}`}>
                <h3 className={`flex items-center gap-2 font-semibold mb-4 ${hasPros ? 'text-green-800 dark:text-[#A6B1E1]' : 'text-gray-600 dark:text-gray-400'}`}>
                    <CheckCircle className="w-4 h-4" /> {t('feedback.keyStrengths')}
                </h3>
                {hasPros ? (
                    <ul className="space-y-2">
                        {feedback.pros.filter(p => p.trim().length > 0).map((item, i) => (
                            <li key={i} className="flex items-start text-sm text-green-900 dark:text-[#DCD6F7] font-medium">
                                <span className="mr-2 mt-1.5 w-1.5 h-1.5 rounded-full bg-green-600 shrink-0"></span>
                                {item}
                            </li>
                        ))}
                    </ul>
                ) : (
                    <p className="text-sm text-gray-500 dark:text-gray-400 italic">{t('feedback.noStrengths')}</p>
                )}
            </div>

            {/* Areas for Improvement */}
            <div className={`rounded-lg p-5 border min-h-[180px] ${hasCons
                ? 'bg-amber-50 dark:bg-amber-500/10 border-amber-200 dark:border-amber-500/30'
                : 'bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700/60'}`}>
                <h3 className={`flex items-center gap-2 font-semibold mb-4 ${hasCons ? 'text-amber-800 dark:text-amber-400' : 'text-gray-600 dark:text-gray-400'}`}>
                    <AlertCircle className="w-4 h-4" /> {t('feedback.areasImprovement')}
                </h3>
                {hasCons ? (
                    <ul className="space-y-2">
                        {feedback.cons.filter(c => c.trim().length > 0).map((item, i) => (
                            <li key={i} className="flex items-start text-sm text-amber-900 dark:text-amber-300 font-medium">
                                <span className="mr-2 mt-1.5 w-1.5 h-1.5 rounded-full bg-amber-500 shrink-0"></span>
                                {item}
                            </li>
                        ))}
                    </ul>
                ) : (
                    <p className="text-sm text-gray-500 dark:text-gray-400 italic">{t('feedback.noImprovements')}</p>
                )}
            </div>

            {/* Detailed Feedback */}
            {hasDetailedFeedback && (
                <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700/60 p-5 lg:col-span-3">
                    <h3 className="flex items-center gap-2 font-semibold text-gray-800 dark:text-gray-100 mb-4">
                        <MessageSquare className="w-4 h-4" /> {t('feedback.detailedFeedback')}
                    </h3>
                    <div className="prose dark:prose-invert max-w-none text-sm text-gray-600 dark:text-gray-300">
                        <p className="whitespace-pre-line">{feedback.feedback}</p>
                    </div>
                </div>
            )}

            {/* AI Evaluation Insights - Powered by Opik */}
            {(feedback.competency_scores || feedback.opik_trace_id) && (
                <div className="bg-gradient-to-br from-[#424874]/5 to-[#A6B1E1]/10 dark:from-[#424874]/20 dark:to-[#A6B1E1]/10 rounded-lg border border-[#424874]/20 dark:border-[#A6B1E1]/20 p-5 lg:col-span-3">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="flex items-center gap-2 font-semibold text-gray-800 dark:text-gray-100">
                            <Sparkles className="w-4 h-4 text-[#424874] dark:text-[#A6B1E1]" />
                            AI Evaluation Insights
                        </h3>
                        <span className="flex items-center gap-1.5 text-xs text-[#424874] dark:text-[#A6B1E1] bg-white dark:bg-gray-800 px-2 py-1 rounded-full border border-[#424874]/20 dark:border-[#A6B1E1]/20">
                            <Activity className="w-3 h-3" />
                            Powered by Opik
                        </span>
                    </div>

                    {/* Competency Scores Grid */}
                    {feedback.competency_scores && Object.keys(feedback.competency_scores).length > 0 && (
                        <div className="mb-4">
                            <p className="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3 flex items-center gap-1">
                                <BarChart3 className="w-3 h-3" />
                                Competency Breakdown
                            </p>
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                                {Object.entries(feedback.competency_scores).map(([key, value]) => (
                                    <div
                                        key={key}
                                        className="bg-white dark:bg-gray-800 rounded-lg p-3 border border-gray-200 dark:border-gray-700"
                                    >
                                        <p className="text-xs text-gray-500 dark:text-gray-400 capitalize mb-1">
                                            {key.replace(/_/g, ' ')}
                                        </p>
                                        <div className="flex items-baseline gap-1">
                                            <span className={`text-xl font-bold ${getCompetencyColor(value.score)}`}>
                                                {value.score}
                                            </span>
                                            {value.rubric_level && (
                                                <span className="text-xs text-gray-400 dark:text-gray-500">
                                                    {value.rubric_level}
                                                </span>
                                            )}
                                        </div>
                                        {/* Progress bar */}
                                        <div className="mt-2 h-1 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden">
                                            <div
                                                className={`h-full rounded-full transition-all ${getCompetencyBgColor(value.score)}`}
                                                style={{ width: `${value.score}%` }}
                                            />
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Opik Trace CTA */}
                    {feedback.opik_trace_id && (
                        <div className="flex items-center justify-between bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
                            <div className="flex items-center gap-3">
                                <div className="w-10 h-10 rounded-lg bg-[#424874]/10 dark:bg-[#A6B1E1]/10 flex items-center justify-center">
                                    <Activity className="w-5 h-5 text-[#424874] dark:text-[#A6B1E1]" />
                                </div>
                                <div>
                                    <p className="text-sm font-medium text-gray-800 dark:text-gray-100">
                                        Full AI Trace Available
                                    </p>
                                    <p className="text-xs text-gray-500 dark:text-gray-400">
                                        View complete LLM calls, evaluation scores, and latency metrics
                                    </p>
                                </div>
                            </div>
                            <a
                                href={getOpikTraceUrl(feedback.opik_trace_id)}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="flex items-center gap-2 px-4 py-2 bg-[#424874] hover:bg-[#363B5E] text-white text-sm font-medium rounded-lg transition-colors"
                            >
                                <ExternalLink className="w-4 h-4" />
                                View on Opik
                            </a>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

function getCompetencyColor(score: number): string {
    if (score >= 80) return "text-green-600 dark:text-green-400";
    if (score >= 60) return "text-yellow-600 dark:text-yellow-400";
    if (score >= 40) return "text-orange-600 dark:text-orange-400";
    return "text-red-600 dark:text-red-400";
}

function getCompetencyBgColor(score: number): string {
    if (score >= 80) return "bg-green-500";
    if (score >= 60) return "bg-yellow-500";
    if (score >= 40) return "bg-orange-500";
    return "bg-red-500";
}
