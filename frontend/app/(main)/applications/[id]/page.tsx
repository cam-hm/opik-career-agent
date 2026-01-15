"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useUser, useAuth } from "@clerk/nextjs";
import { Loader2, CheckCircle, PlayCircle, Lock, ArrowRight, Briefcase, ChevronLeft, Clock, Trophy, ChevronRight } from "lucide-react";
import { getScoreColor, getScoreBg } from "@/lib/design-tokens";
import FeedbackModal from "@/components/FeedbackModal";
import { useLanguage } from "@/contexts/LanguageContext";
import { fetchWithAuth } from "@/lib/api";
import { ENDPOINTS } from "@/lib/endpoints";
import { StageBadge } from "@/components/ui/StageBadge";

interface InterviewSession {
    id: number;
    session_id: string;
    stage_type: string;
    status: string;
    overall_score?: number;
    feedback_markdown?: string;
}

interface Application {
    id: string;
    job_role: string;
    status: string;
    current_stage: number;
    sessions: InterviewSession[];
}

const STAGE_CONFIGS = [
    { id: 1, type: "hr" },
    { id: 2, type: "technical" },
    { id: 3, type: "behavioral" },
] as const;

export default function ApplicationView() {
    const { id } = useParams();
    const { user } = useUser();
    const { getToken } = useAuth();
    const router = useRouter();
    const { t } = useLanguage();
    const [application, setApplication] = useState<Application | null>(null);
    const [loading, setLoading] = useState(true);
    const [actionLoading, setActionLoading] = useState(false);
    const [selectedSession, setSelectedSession] = useState<InterviewSession | null>(null);

    useEffect(() => {
        if (id && user) {
            fetchApplication();
        }
    }, [id, user]);

    const fetchApplication = async () => {
        try {
            const res = await fetchWithAuth(ENDPOINTS.APPLICATION.DETAIL(id as string), {}, getToken);
            if (res.ok) {
                const data = await res.json();
                setApplication(data);
            }
        } catch (error) {
            console.error("Failed to fetch application", error);
        } finally {
            setLoading(false);
        }
    };

    const handleStartStage = async () => {
        if (!application) return;
        setActionLoading(true);
        try {
            // This endpoint creates a new interview session for the current stage
            const res = await fetchWithAuth(ENDPOINTS.APPLICATION.START_STAGE(application.id), {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({})
            }, getToken);

            if (res.ok) {
                const data = await res.json();
                router.push(`/interview/${data.session_id}`);
            } else {
                alert("Failed to start stage");
            }
        } catch (error) {
            console.error("Error starting stage", error);
        } finally {
            setActionLoading(false);
        }
    };

    const handleSkipStage = async () => {
        if (!application) return;
        setActionLoading(true);
        try {
            const res = await fetchWithAuth(ENDPOINTS.APPLICATION.SKIP_STAGE(application.id), {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({})
            }, getToken);

            if (res.ok) {
                fetchApplication();
            } else {
                alert("Failed to skip stage");
            }
        } catch (error) {
            console.error("Error skipping stage", error);
        } finally {
            setActionLoading(false);
        }
    };

    const handleCompleteStage = async () => {
        if (!application) return;
        setActionLoading(true);
        try {
            const res = await fetchWithAuth(ENDPOINTS.APPLICATION.COMPLETE_STAGE(application.id), {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({})
            }, getToken);

            if (res.ok) {
                fetchApplication();
            } else {
                alert("Failed to complete stage");
            }
        } catch (error) {
            console.error("Error completing stage", error);
        } finally {
            setActionLoading(false);
        }
    };

    // Check if current stage has a completed session
    const currentStageConfig = STAGE_CONFIGS[application?.current_stage ? application.current_stage - 1 : 0];
    const currentStageType = currentStageConfig?.type;

    const hasCompletedSession = application?.sessions?.some(
        s => s.stage_type === currentStageType && s.status === "completed"
    );

    if (loading) {
        return (
            <div className="flex h-[50vh] items-center justify-center">
                <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
            </div>
        );
    }

    if (!application) {
        return (
            <div className="flex h-[50vh] flex-col items-center justify-center gap-4">
                <h2 className="text-xl font-bold text-gray-800 dark:text-gray-100">{t('applicationView.notFound')}</h2>
                <button
                    onClick={() => router.push('/applications')}
                    className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-200 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-md transition-colors"
                >
                    {t('applicationView.backToApps')}
                </button>
            </div>
        );
    }

    const isCompleted = application.status === "completed" || application.current_stage > 3;
    const avgScore = application.sessions.length > 0
        ? Math.round(application.sessions.reduce((acc, s) => acc + (s.overall_score || 0), 0) / application.sessions.length)
        : 0;

    return (
        <div className="space-y-6">
            {/* Header Container */}
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700/60">
                <div className="px-5 py-4 flex items-center gap-4">
                    {/* Back Button - Icon Circle */}
                    <button
                        onClick={() => router.push('/applications')}
                        className="w-9 h-9 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 flex items-center justify-center transition-colors shrink-0"
                        title={t('applicationView.backToApps')}
                    >
                        <ChevronLeft className="w-5 h-5 text-gray-600 dark:text-gray-300" />
                    </button>
                    {/* Job Icon */}
                    <div className="w-11 h-11 rounded-lg bg-[#DCD6F7] dark:bg-[#424874]/20 flex items-center justify-center shrink-0">
                        <Briefcase className="w-5 h-5 text-[#424874] dark:text-[#A6B1E1]" />
                    </div>
                    {/* Title */}
                    <div className="flex-1 min-w-0">
                        <h1 className="text-xl font-semibold text-gray-900 dark:text-white">{application.job_role}</h1>
                        <p className="text-sm text-gray-500 dark:text-gray-400">{t('applicationView.title')}</p>
                    </div>
                </div>
            </div>

            <div className="grid gap-6 lg:grid-cols-[300px_1fr]">
                {/* Sidebar - Stages Container */}
                <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700/60 overflow-hidden">
                    <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-700/60">
                        <h2 className="text-xs font-semibold uppercase text-gray-500 dark:text-gray-400">{t('applicationView.stagesTitle')}</h2>
                    </div>
                    <div className="divide-y divide-gray-100 dark:divide-gray-700/60">
                        {STAGE_CONFIGS.map((stage) => {
                            const stageCompleted = application.current_stage > stage.id || (application.current_stage === stage.id && isCompleted);
                            const stageCurrent = application.current_stage === stage.id && !isCompleted;

                            // Get translated strings
                            const stageName = t(`applicationView.stages.${stage.type}.name`);
                            const stageDesc = t(`applicationView.stages.${stage.type}.desc`);

                            return (
                                <div
                                    key={stage.id}
                                    className={`px-4 py-3 flex items-center gap-3 ${stageCurrent ? 'bg-gray-50 dark:bg-gray-500/10' : ''}`}
                                >
                                    <div className="shrink-0">
                                        <StageBadge
                                            stage={stage.type as import("@/components/ui/StageBadge").StageType}
                                            status={stageCompleted || stageCurrent ? "active" : "locked"}
                                            size="sm"
                                        />
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <h3 className={`font-medium text-sm ${stageCompleted || stageCurrent ? 'text-gray-800 dark:text-gray-100' : 'text-gray-500 dark:text-gray-400'}`}>
                                            {stageName}
                                        </h3>
                                        <p className="text-xs text-gray-500 dark:text-gray-500">{stageDesc}</p>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>

                {/* Main Content */}
                <div className="space-y-6">
                    {isCompleted ? (
                        /* Completed State */
                        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700/60 overflow-hidden">
                            <div className="bg-green-50 dark:bg-green-500/10 border-b border-green-200 dark:border-green-500/20 p-8 text-center">
                                <CheckCircle className="w-12 h-12 text-[#424874] dark:text-[#A6B1E1] mx-auto mb-4" />
                                <h2 className="text-2xl font-bold text-green-800 dark:text-[#DCD6F7] mb-2">{t('applicationView.completedTitle')}</h2>
                                <p className="text-green-700 dark:text-[#A6B1E1]">{t('applicationView.completedDesc')}</p>
                            </div>
                            <div className="p-8">
                                <div className={`${getScoreBg(avgScore)} rounded-xl p-6 text-center mb-6`}>
                                    <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">{t('applicationView.avgScore')}</p>
                                    <p className={`text-5xl font-bold ${getScoreColor(avgScore)}`}>{avgScore}</p>
                                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">/100</p>
                                </div>
                                <button
                                    onClick={() => router.push('/dashboard')}
                                    className="w-full py-3 bg-[#424874] hover:bg-[#363B5E] text-white rounded-md font-medium transition-colors"
                                >
                                    {t('applicationView.backToDashboard')}
                                </button>
                            </div>
                        </div>
                    ) : (
                        /* Current Stage */
                        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700/60 overflow-hidden">
                            <div className="px-5 py-4 border-b border-gray-200 dark:border-gray-700/60">
                                <h2 className="font-semibold text-gray-800 dark:text-gray-100">
                                    {t('applicationView.currentStage')} {currentStageConfig ? t(`applicationView.stages.${currentStageConfig.type}.name`) : ''}
                                </h2>
                                <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5">
                                    {currentStageConfig ? t(`applicationView.stages.${currentStageConfig.type}.desc`) : ''}
                                </p>
                            </div>
                            <div className="p-5">
                                <div className="bg-gray-50 dark:bg-gray-700/30 rounded-lg p-6 text-center mb-5">
                                    <Clock className="w-10 h-10 text-gray-400 dark:text-gray-500 mx-auto mb-3" />
                                    <p className="text-gray-600 dark:text-gray-300 mb-1">{t('applicationView.readyPrompt')}</p>
                                    <p className="text-sm text-gray-500 dark:text-gray-400">{t('applicationView.durationEstimate')}</p>
                                </div>
                                <div className="flex gap-3">
                                    <button
                                        onClick={handleStartStage}
                                        disabled={actionLoading}
                                        className="flex-1 py-3 bg-[#424874] hover:bg-[#363B5E] text-white rounded-md font-medium transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
                                    >
                                        {actionLoading ? (
                                            <Loader2 className="w-5 h-5 animate-spin" />
                                        ) : (
                                            <>
                                                {t('applicationView.startBtn')} <ArrowRight className="w-4 h-4" />
                                            </>
                                        )}
                                    </button>
                                    {hasCompletedSession && (
                                        <button
                                            onClick={handleCompleteStage}
                                            disabled={actionLoading}
                                            className="px-6 py-3 bg-green-600 hover:bg-green-700 text-white rounded-md font-medium transition-colors flex items-center gap-2 disabled:opacity-50"
                                        >
                                            <CheckCircle className="w-4 h-4" /> {t('applicationView.completeBtn')}
                                        </button>
                                    )}
                                    <button
                                        onClick={handleSkipStage}
                                        disabled={actionLoading}
                                        className="px-6 py-3 text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md font-medium transition-colors disabled:opacity-50"
                                    >
                                        {t('applicationView.skipBtn')}
                                    </button>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Session History */}
                    {application.sessions && application.sessions.length > 0 && (
                        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700/60 overflow-hidden">
                            <div className="px-5 py-4 border-b border-gray-200 dark:border-gray-700/60">
                                <h2 className="font-semibold text-gray-800 dark:text-gray-100 flex items-center gap-2">
                                    <Trophy className="w-4 h-4" /> {t('applicationView.historyTitle')}
                                </h2>
                            </div>
                            <div className="divide-y divide-gray-100 dark:divide-gray-700/60">
                                {application.sessions.map((session) => (
                                    <div
                                        key={session.id}
                                        className="flex items-center gap-4 px-5 py-3 hover:bg-gray-50 dark:hover:bg-gray-700/30 transition-colors group"
                                    >
                                        <div className="w-9 h-9 rounded-lg bg-gray-100 dark:bg-gray-700 flex items-center justify-center">
                                            <CheckCircle className="w-4 h-4 text-gray-500 dark:text-gray-400" />
                                        </div>
                                        <div className="flex-1 min-w-0">
                                            <p className="font-medium text-gray-800 dark:text-gray-100 capitalize">
                                                {/* Try to translate stage name if possible, or fallback manually */}
                                                {t(`applicationView.stages.${session.stage_type}.name`) || session.stage_type} {t('applicationView.roundSuffix')}
                                            </p>
                                            <p className="text-xs text-gray-500 dark:text-gray-400">{session.status}</p>
                                        </div>
                                        {session.overall_score !== undefined && (
                                            <span className={`text-lg font-bold ${getScoreColor(session.overall_score)}`}>
                                                {session.overall_score}
                                            </span>
                                        )}
                                        <button
                                            onClick={() => setSelectedSession(session)}
                                            className="text-sm font-medium text-[#424874] hover:text-[#363B5E] dark:text-[#A6B1E1] dark:hover:text-[#DCD6F7]"
                                        >
                                            {t('applicationView.viewResults')} →
                                        </button>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            </div>

            <FeedbackModal
                isOpen={!!selectedSession}
                onClose={() => setSelectedSession(null)}
                feedbackMarkdown={selectedSession?.feedback_markdown}
                title={selectedSession ? `${t(`applicationView.stages.${selectedSession.stage_type}.name`)}` : undefined}
            />
        </div>
    );
}
