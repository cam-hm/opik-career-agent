"use client";

import { useUser, useAuth } from "@clerk/nextjs";
import { useEffect, useState } from "react";
import Link from "next/link";
import { Loader2, Calendar, Briefcase, CheckCircle, XCircle, Clock, PlayCircle, Plus, ChevronRight } from "lucide-react";
import { useLanguage } from "@/contexts/LanguageContext";
import { StatusBadge } from "@/components/common/StatusBadge";
import { fetchWithAuth } from "@/lib/api";
import { ENDPOINTS } from "@/lib/endpoints";

interface InterviewSession {
    session_id: string;
    job_role: string;
    status: string;
    created_at: string;
    overall_score?: number;
    application_id?: string;
    stage_type?: string;
}

export default function PracticePage() {
    const { user, isLoaded, isSignedIn } = useUser();
    const { getToken } = useAuth();
    const { t } = useLanguage();
    const [sessions, setSessions] = useState<InterviewSession[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (isLoaded && isSignedIn && user) {
            fetchSessions();
        } else if (isLoaded && !isSignedIn) {
            setLoading(false);
        }
    }, [isLoaded, isSignedIn, user]);

    const fetchSessions = async () => {
        try {
            const res = await fetchWithAuth(`${ENDPOINTS.INTERVIEW.LIST}?mode=practice`, {}, getToken);
            if (res.ok) {
                const data = await res.json();
                setSessions(data);  // No client-side filter - API returns only practice sessions
            }
        } catch (error) {
            console.error("Failed to fetch sessions", error);
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

    return (
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700/60 overflow-hidden">
            {/* Header Row */}
            <div className="px-5 py-4 border-b border-gray-200 dark:border-gray-700/60">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-2xl font-serif font-bold text-gray-800 dark:text-gray-100 italic">{t('practice.title')}</h1>
                        <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5">{t('practice.subtitle')}</p>
                    </div>
                    <Link
                        href="/practice/new"
                        className="inline-flex items-center gap-2 px-4 py-2 bg-[#424874] hover:bg-[#363B5E] text-white rounded-md text-sm font-medium transition-colors"
                    >
                        <Plus className="w-4 h-4" /> {t('practice.new')}
                    </Link>
                </div>
            </div>

            {sessions.length === 0 ? (
                /* Empty State */
                <div className="text-center py-16 px-5">
                    <PlayCircle className="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold mb-2 text-gray-800 dark:text-gray-100">{t('practice.noSessions')}</h3>
                    <p className="text-gray-500 dark:text-gray-400 mb-6 max-w-sm mx-auto">{t('practice.noSessionsDesc')}</p>
                    <Link
                        href="/practice/new"
                        className="inline-flex items-center gap-2 px-5 py-2.5 bg-[#424874] hover:bg-[#363B5E] text-white rounded-md font-medium transition-colors"
                    >
                        <PlayCircle className="w-4 h-4" /> {t('setup.startPractice')}
                    </Link>
                </div>
            ) : (
                /* List View */
                <div className="divide-y divide-gray-100 dark:divide-gray-700/60">
                    {sessions.map((session) => (
                        <Link
                            href={`/interview/${session.session_id}`}
                            key={session.session_id}
                            className="flex items-center gap-4 px-5 py-4 hover:bg-gray-50 dark:hover:bg-gray-700/30 transition-colors group"
                        >
                            {/* Icon */}
                            <div className="w-10 h-10 rounded-lg bg-gray-100 dark:bg-gray-700 flex items-center justify-center shrink-0">
                                <Briefcase className="w-5 h-5 text-gray-500 dark:text-gray-400" />
                            </div>

                            {/* Job Role & Date */}
                            <div className="flex-1 min-w-0">
                                <h3 className="font-medium text-gray-800 dark:text-gray-100 truncate">{session.job_role || "Untitled"}</h3>
                                <p className="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-1 mt-0.5">
                                    <Calendar className="w-3 h-3" />
                                    {new Date(session.created_at).toLocaleDateString()}
                                </p>
                            </div>

                            {/* Score */}
                            <div className="hidden sm:block">
                                {session.overall_score ? (
                                    <span className={`text-lg font-bold ${getScoreColor(session.overall_score)}`}>
                                        {session.overall_score}
                                    </span>
                                ) : (
                                    <span className="text-gray-400">-</span>
                                )}
                            </div>

                            {/* Status Badge */}
                            <StatusBadge status={session.status} t={t} />

                            {/* Arrow */}
                            <ChevronRight className="w-4 h-4 text-gray-400 dark:text-gray-500 group-hover:text-gray-600 dark:group-hover:text-gray-300 transition-colors" />
                        </Link>
                    ))}
                </div>
            )}
        </div>
    );
}



function getScoreColor(score: number) {
    if (score >= 80) return "text-[#424874] dark:text-[#A6B1E1]";
    if (score >= 60) return "text-yellow-600 dark:text-yellow-400";
    return "text-red-600 dark:text-red-400";
}
