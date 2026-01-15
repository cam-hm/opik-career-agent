"use client";

import { X, CheckCircle, TrendingUp, AlertCircle } from "lucide-react";
import { useEffect, useState } from "react";
import { useLanguage } from "@/contexts/LanguageContext";

interface Feedback {
    score: number;
    summary: string;
    pros: string[];
    cons: string[];
    feedback: string;
}

interface FeedbackModalProps {
    isOpen: boolean;
    onClose: () => void;
    feedbackMarkdown?: string | null;
    title?: string;
}

// Helper to check if feedback has meaningful data (same logic as feedback page)
function hasValidFeedback(feedback: Feedback | null): boolean {
    if (!feedback) return false;

    // Check if score is 0 - strong indicator of empty session
    if (feedback.score === 0) return false;

    // Check for known "empty session" messages from API
    const emptySummaryIndicators = [
        "no conversation recorded",
        "no responses were recorded",
        "session ended without",
        "no transcript available"
    ];

    const summaryLower = (feedback.summary || "").toLowerCase();
    const isEmptySummary = emptySummaryIndicators.some(indicator =>
        summaryLower.includes(indicator)
    );

    if (isEmptySummary) return false;

    // Check if there's actual content beyond default empty values
    const hasPros = feedback.pros && feedback.pros.length > 0 && feedback.pros.some(p => p.trim().length > 0);
    const hasCons = feedback.cons && feedback.cons.length > 0 && feedback.cons.some(c => c.trim().length > 0);
    const hasDetailedFeedback = !!(feedback.feedback && feedback.feedback.trim().length > 0);

    return !!(hasPros || hasCons || hasDetailedFeedback);
}

export default function FeedbackModal({ isOpen, onClose, feedbackMarkdown, title }: FeedbackModalProps) {
    const { t } = useLanguage();
    const [feedback, setFeedback] = useState<Feedback | null>(null);

    useEffect(() => {
        if (feedbackMarkdown) {
            try {
                const parsed = JSON.parse(feedbackMarkdown);
                setFeedback(parsed);
            } catch (e) {
                console.error("Failed to parse feedback markdown", e);
                setFeedback(null);
            }
        } else {
            setFeedback(null);
        }
    }, [feedbackMarkdown]);

    if (!isOpen) return null;

    const getScoreColor = (score: number) => {
        if (score >= 80) return "text-[#424874] dark:text-[#A6B1E1]";
        if (score >= 60) return "text-yellow-600 dark:text-yellow-400";
        return "text-red-600 dark:text-red-400";
    };

    const getScoreBg = (score: number) => {
        if (score >= 80) return "bg-[#DCD6F7] dark:bg-[#424874]/20";
        if (score >= 60) return "bg-yellow-100 dark:bg-yellow-500/20";
        return "bg-red-100 dark:bg-red-500/20";
    };

    // Check if this is an empty session
    const isEmptySession = !hasValidFeedback(feedback);

    // Helper to check if there's content
    const hasPros = feedback?.pros && feedback.pros.length > 0 && feedback.pros.some(p => p.trim().length > 0);
    const hasCons = feedback?.cons && feedback.cons.length > 0 && feedback.cons.some(c => c.trim().length > 0);

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
            <div className="relative w-full max-w-2xl max-h-[90vh] overflow-y-auto bg-white dark:bg-gray-800 rounded-xl shadow-xl border border-gray-200 dark:border-gray-700/60">
                {/* Header */}
                <div className="sticky top-0 z-10 flex items-center justify-between px-6 py-4 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700/60">
                    <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100 uppercase tracking-wide">
                        {title || t('feedback.sessionResults')}
                    </h2>
                    <button
                        onClick={onClose}
                        className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700/50 text-gray-500 dark:text-gray-400 transition-colors"
                    >
                        <X className="h-5 w-5" />
                    </button>
                </div>

                <div className="p-6 space-y-6">
                    {!feedback ? (
                        <div className="text-center py-12">
                            <p className="text-gray-500 dark:text-gray-400">{t('feedback.noData')}</p>
                        </div>
                    ) : isEmptySession ? (
                        /* Empty Session State - Similar to feedback page */
                        <div className="text-center py-8">
                            <div className="w-16 h-16 rounded-full bg-gray-100 dark:bg-gray-700 flex items-center justify-center mx-auto mb-6">
                                <AlertCircle className="w-8 h-8 text-gray-400 dark:text-gray-500" />
                            </div>

                            <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-2">
                                {t('feedback.noResponses')}
                            </h3>

                            <p className="text-gray-500 dark:text-gray-400 mb-6 max-w-md mx-auto">
                                {t('feedback.noResponsesDesc')}
                            </p>

                            {/* Score Display - N/A instead of 0 */}
                            <div className="bg-gray-100 dark:bg-gray-700/50 rounded-xl p-6 inline-block">
                                <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">{t('feedback.score')}</p>
                                <p className="text-4xl font-bold text-gray-400 dark:text-gray-500">N/A</p>
                            </div>
                        </div>
                    ) : (
                        /* Normal Feedback Display */
                        <>
                            {/* Score Card */}
                            <div className={`rounded-xl p-6 ${getScoreBg(feedback.score)}`}>
                                <div className="flex items-center justify-between">
                                    <div>
                                        <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">{t('feedback.score')}</h3>
                                        <p className="text-xs text-gray-500 dark:text-gray-500">{t('feedback.performanceAssessment')}</p>
                                    </div>
                                    <div className="flex items-baseline gap-1">
                                        <span className={`text-5xl font-bold ${getScoreColor(feedback.score)}`}>
                                            {feedback.score}
                                        </span>
                                        <span className="text-gray-500 dark:text-gray-400 text-sm">/100</span>
                                    </div>
                                </div>
                            </div>

                            {/* Summary */}
                            <div className="bg-gray-50 dark:bg-gray-700/30 rounded-xl p-5 border border-gray-200 dark:border-gray-700/60">
                                <h3 className="flex items-center gap-2 font-semibold text-gray-800 dark:text-gray-100 mb-3">
                                    <TrendingUp className="w-4 h-4" /> {t('feedback.summary')}
                                </h3>
                                <p className="text-gray-600 dark:text-gray-300 leading-relaxed">{feedback.summary}</p>
                            </div>

                            {/* Pros & Cons */}
                            <div className="grid md:grid-cols-2 gap-4">
                                {/* Strengths - Conditional color based on content */}
                                <div className={`rounded-xl p-5 border ${hasPros
                                    ? 'bg-green-50 dark:bg-green-500/10 border-green-200 dark:border-green-500/30'
                                    : 'bg-gray-50 dark:bg-gray-700/30 border-gray-200 dark:border-gray-700/60'
                                    }`}>
                                    <h3 className={`flex items-center gap-2 font-semibold mb-3 ${hasPros
                                        ? 'text-green-800 dark:text-[#A6B1E1]'
                                        : 'text-gray-600 dark:text-gray-400'
                                        }`}>
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
                                        <p className="text-sm text-gray-500 dark:text-gray-400 italic">
                                            {t('feedback.noStrengths')}
                                        </p>
                                    )}
                                </div>

                                {/* Areas for Improvement - Amber instead of Red */}
                                <div className={`rounded-xl p-5 border ${hasCons
                                    ? 'bg-amber-50 dark:bg-amber-500/10 border-amber-200 dark:border-amber-500/30'
                                    : 'bg-gray-50 dark:bg-gray-700/30 border-gray-200 dark:border-gray-700/60'
                                    }`}>
                                    <h3 className={`flex items-center gap-2 font-semibold mb-3 ${hasCons
                                        ? 'text-amber-800 dark:text-amber-400'
                                        : 'text-gray-600 dark:text-gray-400'
                                        }`}>
                                        <AlertCircle className="w-4 h-4" /> {t('feedback.areasImprovement')}
                                    </h3>
                                    {hasCons ? (
                                        <ul className="space-y-2">
                                            {feedback.cons.filter(c => c.trim().length > 0).map((item, i) => (
                                                <li key={i} className="flex items-start text-sm text-amber-900 dark:text-amber-200 font-medium">
                                                    <span className="mr-2 mt-1.5 w-1.5 h-1.5 rounded-full bg-amber-600 shrink-0"></span>
                                                    {item}
                                                </li>
                                            ))}
                                        </ul>
                                    ) : (
                                        <p className="text-sm text-gray-500 dark:text-gray-400 italic">
                                            {t('feedback.noImprovements')}
                                        </p>
                                    )}
                                </div>
                            </div>
                        </>
                    )}
                </div>

                {/* Footer */}
                <div className="px-6 py-4 border-t border-gray-200 dark:border-gray-700/60">
                    <button
                        onClick={onClose}
                        className="w-full py-2.5 bg-[#424874] hover:bg-[#363B5E] text-white rounded-lg font-medium transition-colors"
                    >
                        {t('feedback.close')}
                    </button>
                </div>
            </div>
        </div>
    );
}
