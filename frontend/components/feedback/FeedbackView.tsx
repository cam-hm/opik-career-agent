"use client";

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { CheckCircle, Trophy, TrendingUp, AlertCircle, MessageSquare, ExternalLink } from 'lucide-react';
import { getScoreColor, getScoreBg } from "@/lib/design-tokens";
import { useLanguage } from '@/contexts/LanguageContext';

interface Feedback {
    score: number;
    summary: string;
    pros: string[];
    cons: string[];
    feedback: string;
    opik_trace_id?: string;
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
                {feedback.opik_trace_id && (
                    <a
                        href={`https://www.comet.com/opik/traces/${feedback.opik_trace_id}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center justify-center gap-2 w-full mt-3 py-2 text-sm text-[#424874] dark:text-[#A6B1E1] hover:text-[#363B5E] dark:hover:text-white border border-[#424874]/30 dark:border-[#A6B1E1]/30 rounded-md transition-colors"
                    >
                        <ExternalLink className="w-3.5 h-3.5" />
                        View AI Trace on Opik
                    </a>
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
        </div>
    );
}
