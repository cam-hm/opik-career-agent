"use client";

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { Loader2, CheckCircle, XCircle, Trophy, TrendingUp, ChevronLeft, Calendar, Briefcase, MessageSquare, PlayCircle, AlertCircle, ArrowRight, Home } from 'lucide-react';
import { getScoreColor, getScoreBg } from "@/lib/design-tokens";
import { useAuth } from '@clerk/nextjs';
import { fetchWithAuth } from '@/lib/api';
import { ENDPOINTS } from '@/lib/endpoints';
import FeedbackView from '@/components/feedback/FeedbackView';

interface Feedback {
    score: number;
    summary: string;
    pros: string[];
    cons: string[];
    feedback: string;
}

// Helper to check if feedback has meaningful data
function hasValidFeedback(feedback: Feedback | null): boolean {
    if (!feedback) return false;
    if (feedback.score === 0) return false;

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

    const hasPros = !!(feedback.pros && feedback.pros.length > 0 && feedback.pros.some(p => p.trim().length > 0));
    const hasCons = !!(feedback.cons && feedback.cons.length > 0 && feedback.cons.some(c => c.trim().length > 0));
    const hasDetailedFeedback = !!(feedback.feedback && feedback.feedback.trim().length > 0);

    return hasPros || hasCons || hasDetailedFeedback;
}

import { useLanguage } from '@/contexts/LanguageContext';

export default function FeedbackPage() {
    const { t } = useLanguage();
    const params = useParams();
    const router = useRouter();
    const sessionId = params.id as string;
    const [feedback, setFeedback] = useState<Feedback | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const { getToken } = useAuth();
    const [sessionDetails, setSessionDetails] = useState<{ application_id?: string; job_role?: string; created_at?: string; stage_type?: string } | null>(null);
    const [isStartingNextStage, setIsStartingNextStage] = useState(false);

    useEffect(() => {
        const fetchFeedback = async () => {
            const maxRetries = 5;
            let retryCount = 0;
            try {
                const sessionRes = await fetchWithAuth(ENDPOINTS.INTERVIEW.DETAIL(sessionId), {}, getToken);
                if (sessionRes.ok) {
                    const sessionData = await sessionRes.json();
                    setSessionDetails(sessionData);
                }
            } catch (e) {
                console.error("Failed to fetch session details", e);
            }


            while (retryCount < maxRetries) {
                try {
                    const res = await fetchWithAuth(ENDPOINTS.INTERVIEW.FEEDBACK(sessionId), {
                        method: 'POST',
                    }, getToken);


                    if (res.ok) {
                        const data = await res.json();
                        setFeedback(data);
                        setLoading(false);
                        return;
                    }

                    if (res.status === 400) {
                        await new Promise(resolve => setTimeout(resolve, 1000));
                        retryCount++;
                        continue;
                    }

                    throw new Error("Failed to generate feedback");
                } catch (err) {
                    console.error(err);
                    if (retryCount === maxRetries - 1) {
                        setError("Could not generate feedback. Please try again later.");
                        setLoading(false);
                    }
                    retryCount++;
                    await new Promise(resolve => setTimeout(resolve, 1000));
                }
            }
        };

        fetchFeedback();
    }, [sessionId]);

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[60vh]">
                <Loader2 className="h-10 w-10 animate-spin text-[#424874] dark:text-[#A6B1E1] mb-4" />
                <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-100 mb-2">{t('feedback.analyzing')}</h2>
                <p className="text-gray-500 dark:text-gray-400 text-center max-w-md">
                    {t('feedback.analyzingDesc')}
                </p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[60vh]">
                <div className="bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/30 p-8 rounded-xl max-w-md text-center">
                    <XCircle className="w-12 h-12 text-red-600 dark:text-red-400 mx-auto mb-4" />
                    <h2 className="text-xl font-semibold text-red-700 dark:text-red-400 mb-2">{t('feedback.analysisError')}</h2>
                    <p className="text-gray-600 dark:text-gray-400">{error}</p>
                </div>
            </div>
        );
    }

    const isEmptySession = !hasValidFeedback(feedback);
    const stageType = sessionDetails?.stage_type || 'practice';
    const isApplicationInterview = stageType !== 'practice';
    const isFinalStage = stageType === 'behavioral';
    const backUrl = isApplicationInterview ? `/applications/${sessionDetails?.application_id}` : '/dashboard';
    const backLabel = isApplicationInterview ? t('feedback.backToApp') : t('common.goToDashboard');

    const handleProceedToNextStage = async () => {
        if (!sessionDetails?.application_id) return;
        setIsStartingNextStage(true);
        try {
            // Use proceed_to_next_stage which advances stage AND starts next interview
            const res = await fetchWithAuth(ENDPOINTS.APPLICATION.PROCEED_STAGE(sessionDetails.application_id), {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
            }, getToken);
            if (res.ok) {
                const data = await res.json();
                if (data.completed) {
                    // All stages completed - go to application page
                    router.push(`/applications/${sessionDetails.application_id}`);
                } else {
                    // Start next interview
                    router.push(`/interview/${data.session_id}`);
                }
            } else {
                const errorData = await res.json().catch(() => ({}));
                console.error('Failed to proceed to next stage:', errorData);
                setIsStartingNextStage(false);
            }
        } catch (e) {
            console.error(e);
            setIsStartingNextStage(false);
        }
    };

    // Empty Session State
    if (isEmptySession) {
        return (
            <div className="space-y-6">
                {/* Header Container */}
                <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700/60">
                    <div className="px-5 py-4 flex items-center gap-4">
                        {/* Back Button - Icon Circle */}
                        <button
                            onClick={() => router.push(backUrl)}
                            className="w-9 h-9 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 flex items-center justify-center transition-colors shrink-0"
                            title={backLabel}
                        >
                            <ChevronLeft className="w-5 h-5 text-gray-600 dark:text-gray-300" />
                        </button>
                        {/* Title */}
                        <div className="flex-1 min-w-0">
                            <h1 className="text-xl font-serif font-bold text-gray-900 dark:text-white italic">{t('feedback.performanceReview')}</h1>
                            <p className="text-sm text-gray-500 dark:text-gray-400">{t('feedback.analysisDesc')}</p>
                        </div>
                        {/* Badges */}
                        <div className="flex gap-2 shrink-0">
                            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300">
                                <Briefcase className="w-3 h-3" />
                                {sessionDetails?.job_role || "Unknown Role"}
                            </span>
                            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300">
                                <Calendar className="w-3 h-3" />
                                {sessionDetails?.created_at ? new Date(sessionDetails.created_at).toLocaleDateString() : "Just now"}
                            </span>
                        </div>
                    </div>
                </div>

                {/* Empty Session Card */}
                <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700/60 p-8 text-center">
                    <div className="w-16 h-16 rounded-full bg-gray-100 dark:bg-gray-700 flex items-center justify-center mx-auto mb-6">
                        <AlertCircle className="w-8 h-8 text-gray-400 dark:text-gray-500" />
                    </div>
                    <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-100 mb-3">
                        {t('feedback.noResponses')}
                    </h2>
                    <p className="text-gray-500 dark:text-gray-400 mb-6 max-w-md mx-auto">
                        {t('feedback.noResponsesDesc')}
                    </p>
                    <div className="bg-gray-100 dark:bg-gray-700/50 rounded-xl p-6 mb-6 inline-block">
                        <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">{t('feedback.score')}</p>
                        <p className="text-4xl font-bold text-gray-400 dark:text-gray-500">N/A</p>
                    </div>
                    <div className="flex flex-col sm:flex-row gap-3 justify-center">
                        {isApplicationInterview ? (
                            <>
                                {!isFinalStage && (
                                    <button
                                        onClick={handleProceedToNextStage}
                                        disabled={isStartingNextStage}
                                        className="inline-flex items-center justify-center gap-2 px-5 py-2.5 bg-[#424874] hover:bg-[#363B5E] text-white rounded-md font-medium transition-colors disabled:opacity-50"
                                    >
                                        {isStartingNextStage ? <Loader2 className="w-4 h-4 animate-spin" /> : <ArrowRight className="w-4 h-4" />}
                                        {t('feedback.nextStage')}
                                    </button>
                                )}
                                <Link href={backUrl} className="inline-flex items-center justify-center gap-2 px-5 py-2.5 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-200 rounded-md font-medium transition-colors">
                                    <Home className="w-4 h-4" /> {t('feedback.returnToApp')}
                                </Link>
                            </>
                        ) : (
                            <>
                                <Link href="/practice/new" className="inline-flex items-center justify-center gap-2 px-5 py-2.5 bg-[#424874] hover:bg-[#363B5E] text-white rounded-md font-medium transition-colors">
                                    <PlayCircle className="w-4 h-4" /> {t('common.startPractice')}
                                </Link>
                                <Link href="/dashboard" className="inline-flex items-center justify-center gap-2 px-5 py-2.5 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-200 rounded-md font-medium transition-colors">
                                    {t('common.goToDashboard')}
                                </Link>
                            </>
                        )}
                    </div>
                </div>
            </div>
        );
    }

    if (!feedback) return null;

    const hasPros = feedback.pros && feedback.pros.length > 0 && feedback.pros.some(p => p.trim().length > 0);
    const hasCons = feedback.cons && feedback.cons.length > 0 && feedback.cons.some(c => c.trim().length > 0);
    const hasDetailedFeedback = feedback.feedback && feedback.feedback.trim().length > 0;

    return (
        <div className="space-y-6">
            {/* Header Container */}
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700/60">
                <div className="px-5 py-4 flex items-center gap-4">
                    {/* Back Button - Icon Circle */}
                    <button
                        onClick={() => router.push(backUrl)}
                        className="w-9 h-9 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 flex items-center justify-center transition-colors shrink-0"
                        title={backLabel}
                    >
                        <ChevronLeft className="w-5 h-5 text-gray-600 dark:text-gray-300" />
                    </button>
                    {/* Title */}
                    <div className="flex-1 min-w-0">
                        <h1 className="text-xl font-serif font-bold text-gray-900 dark:text-white italic">{t('feedback.performanceReview')}</h1>
                        <p className="text-sm text-gray-500 dark:text-gray-400">{t('feedback.analysisDesc')}</p>
                    </div>
                    {/* Badges */}
                    <div className="flex gap-2 shrink-0">
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300">
                            <Briefcase className="w-3 h-3" />
                            {sessionDetails?.job_role || "Unknown Role"}
                        </span>
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300">
                            <Calendar className="w-3 h-3" />
                            {sessionDetails?.created_at ? new Date(sessionDetails.created_at).toLocaleDateString() : "Just now"}
                        </span>
                    </div>
                </div>
            </div>

            <FeedbackView feedback={feedback} sessionDetails={sessionDetails} />

            {/* Actions */}
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700/60 p-5">
                <div className="flex flex-wrap gap-3">
                    {isApplicationInterview ? (
                        <>
                            {!isFinalStage && (
                                <button
                                    onClick={handleProceedToNextStage}
                                    disabled={isStartingNextStage}
                                    className="inline-flex items-center gap-2 px-5 py-2.5 bg-[#424874] hover:bg-[#363B5E] text-white rounded-md font-medium transition-colors disabled:opacity-50"
                                >
                                    {isStartingNextStage ? <Loader2 className="w-4 h-4 animate-spin" /> : <ArrowRight className="w-4 h-4" />}
                                    {t('feedback.nextStage')}
                                </button>
                            )}
                            <Link href={backUrl} className="inline-flex items-center gap-2 px-5 py-2.5 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-200 rounded-md font-medium transition-colors">
                                <Home className="w-4 h-4" /> {t('feedback.returnToApp')}
                            </Link>
                            {isFinalStage && (
                                <Link href="/applications" className="inline-flex items-center gap-2 px-5 py-2.5 bg-green-600 hover:bg-green-700 text-white rounded-md font-medium transition-colors">
                                    <Trophy className="w-4 h-4" /> {t('feedback.viewApps')}
                                </Link>
                            )}
                        </>
                    ) : (
                        <>
                            <Link href="/practice/new" className="inline-flex items-center gap-2 px-5 py-2.5 bg-[#424874] hover:bg-[#363B5E] text-white rounded-md font-medium transition-colors">
                                <PlayCircle className="w-4 h-4" /> {t('common.startPractice')}
                            </Link>
                            <Link href="/dashboard" className="inline-flex items-center gap-2 px-5 py-2.5 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-200 rounded-md font-medium transition-colors">
                                {t('common.goToDashboard')}
                            </Link>
                        </>
                    )}
                </div>
            </div>
        </div>
    );
}
