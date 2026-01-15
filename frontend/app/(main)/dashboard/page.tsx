"use client";

import { useUser, useAuth } from "@clerk/nextjs";
import { useEffect, useState } from "react";
import { useLanguage } from "@/contexts/LanguageContext";
import Link from "next/link";
import { Loader2, Briefcase, Layers, PlayCircle, ChevronRight, TrendingUp, Target, Clock, CheckCircle, Calendar } from "lucide-react";
import { fetchWithAuth } from "@/lib/api";
import { ENDPOINTS } from "@/lib/endpoints";

interface InterviewSession {
    session_id: string;
    job_role: string;
    status: string;
    created_at: string;
    overall_score?: number;
    application_id?: string;
}

interface InterviewApplication {
    id: string;
    job_role: string;
    status: string;
    current_stage: number;
    created_at: string;
}

export default function DashboardPage() {
    const { user, isLoaded, isSignedIn } = useUser();
    const { getToken } = useAuth();
    const { t } = useLanguage();
    const [recentSessions, setRecentSessions] = useState<InterviewSession[]>([]);
    const [activeApplications, setActiveApplications] = useState<InterviewApplication[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (isLoaded && isSignedIn && user) {
            fetchData();
        } else if (isLoaded && !isSignedIn) {
            setLoading(false);
        }
    }, [isLoaded, isSignedIn, user]);

    const fetchData = async () => {
        try {
            const resSessions = await fetchWithAuth(`${ENDPOINTS.INTERVIEW.LIST}?mode=practice`, {}, getToken);
            if (resSessions.ok) {
                const data = await resSessions.json();
                setRecentSessions(data.slice(0, 5));  // API returns only practice sessions
            }

            const resApps = await fetchWithAuth(`${ENDPOINTS.APPLICATION.LIST}?status=in_progress`, {}, getToken);
            if (resApps.ok) {
                const data = await resApps.json();
                setActiveApplications(data);  // API returns only in-progress apps
            }


        } catch (error) {
            console.error("Failed to fetch data", error);
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
                <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-100">{t('dashboard.signIn')}</h2>
                <p className="text-gray-500 dark:text-gray-400">{t('dashboard.signInDesc')}</p>
            </div>
        );
    }

    const avgScore = recentSessions.length > 0
        ? Math.round(recentSessions.reduce((acc, s) => acc + (s.overall_score || 0), 0) / recentSessions.length)
        : null;

    return (
        <div className="space-y-6">
            {/* Welcome Section - GitHub style container */}
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700/60 overflow-hidden">
                <div className="px-5 py-5 flex items-center justify-between">
                    <div>
                        <h1 className="text-2xl font-serif font-bold text-gray-800 dark:text-gray-100 italic">
                            {t('dashboard.welcome')} {user?.firstName}
                        </h1>
                        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1 font-medium tracking-wide">
                            {t('dashboard.subtitle')}
                        </p>
                    </div>
                    <div className="flex gap-3">
                        <Link
                            href="/practice/new"
                            className="inline-flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-200 rounded-md text-sm font-medium transition-colors"
                        >
                            <PlayCircle className="w-5 h-5" />
                            <div className="flex flex-col items-start leading-none">
                                <span>{t('dashboard.quickPractice')}</span>
                                <span className="text-[10px] opacity-70 font-normal">{t('dashboard.quickPractice_sub')}</span>
                            </div>
                        </Link>
                        <Link
                            href="/applications/new"
                            className="inline-flex items-center gap-2 px-4 py-2 bg-[#424874] hover:bg-[#363B5E] text-white rounded-md text-sm font-medium transition-colors"
                        >
                            <Layers className="w-5 h-5" />
                            <div className="flex flex-col items-start leading-none">
                                <span>{t('dashboard.newApp')}</span>
                                <span className="text-[10px] opacity-80 font-normal text-blue-100">{t('dashboard.newApp_sub')}</span>
                            </div>
                        </Link>
                    </div>
                </div>
            </div>

            {/* Stats Row */}
            <div className="grid grid-cols-3 gap-4">
                <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700/60 p-4">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-lg bg-[#DCD6F7] dark:bg-[#424874]/20 flex items-center justify-center">
                            <Layers className="w-5 h-5 text-[#424874] dark:text-[#A6B1E1]" />
                        </div>
                        <div>
                            <p className="text-2xl font-bold text-gray-800 dark:text-gray-100">{activeApplications.length}</p>
                            <p className="text-xs text-gray-500 dark:text-gray-400">{t('dashboard.activeApps')}</p>
                        </div>
                    </div>
                </div>

                <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700/60 p-4">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-lg bg-blue-100 dark:bg-blue-500/20 flex items-center justify-center">
                            <PlayCircle className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                        </div>
                        <div>
                            <p className="text-2xl font-bold text-gray-800 dark:text-gray-100">{recentSessions.length}</p>
                            <p className="text-xs text-gray-500 dark:text-gray-400">{t('dashboard.practiceSessions')}</p>
                        </div>
                    </div>
                </div>

                <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700/60 p-4">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-lg bg-[#DCD6F7] dark:bg-[#424874]/20 flex items-center justify-center">
                            <Target className="w-5 h-5 text-[#424874] dark:text-[#A6B1E1]" />
                        </div>
                        <div>
                            <p className="text-2xl font-bold text-gray-800 dark:text-gray-100">{avgScore ?? "-"}</p>
                            <p className="text-xs text-gray-500 dark:text-gray-400">{t('dashboard.avgScore')}</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Main Content - Two Column */}
            <div className="grid grid-cols-12 gap-6">
                {/* Active Applications */}
                <div className="col-span-12 lg:col-span-7">
                    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700/60 overflow-hidden">
                        <div className="px-5 py-4 border-b border-gray-200 dark:border-gray-700/60 flex items-center justify-between">
                            <h2 className="font-semibold text-gray-800 dark:text-gray-100">{t('dashboard.activeApps')}</h2>
                            <Link href="/applications" className="text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200">
                                {t('dashboard.viewAll')} →
                            </Link>
                        </div>
                        {activeApplications.length > 0 ? (
                            <div className="divide-y divide-gray-100 dark:divide-gray-700/60">
                                {activeApplications.slice(0, 4).map(app => (
                                    <Link
                                        href={`/applications/${app.id}`}
                                        key={app.id}
                                        className="flex items-center gap-4 px-5 py-3 hover:bg-gray-50 dark:hover:bg-gray-700/30 transition-colors group"
                                    >
                                        <div className="w-9 h-9 rounded-lg bg-gray-100 dark:bg-gray-700 flex items-center justify-center">
                                            <Briefcase className="w-4 h-4 text-gray-500 dark:text-gray-400" />
                                        </div>
                                        <div className="flex-1 min-w-0">
                                            <p className="font-medium text-gray-800 dark:text-gray-100 truncate">{app.job_role}</p>
                                            <p className="text-xs text-gray-500 dark:text-gray-400">{t('dashboard.stage')} {app.current_stage}/3</p>
                                        </div>
                                        <div className="flex gap-1">
                                            {[1, 2, 3].map((stage) => (
                                                <div
                                                    key={stage}
                                                    className={`w-5 h-1.5 rounded-full ${stage <= app.current_stage
                                                        ? 'bg-green-500'
                                                        : 'bg-gray-200 dark:bg-gray-600'
                                                        }`}
                                                />
                                            ))}
                                        </div>
                                        <ChevronRight className="w-4 h-4 text-gray-400 group-hover:text-gray-600 dark:group-hover:text-gray-300" />
                                    </Link>
                                ))}
                            </div>
                        ) : (
                            <div className="text-center py-10 px-5">
                                <Layers className="w-10 h-10 text-gray-300 dark:text-gray-600 mx-auto mb-3" />
                                <p className="text-sm text-gray-500 dark:text-gray-400 mb-3">{t('dashboard.noApps')}</p>
                                <Link href="/applications/new" className="text-sm text-[#424874] hover:text-[#363B5E] dark:text-[#A6B1E1] font-medium">
                                    {t('dashboard.startNewApp')} →
                                </Link>
                            </div>
                        )}
                    </div>
                </div>

                {/* Recent Practice */}
                <div className="col-span-12 lg:col-span-5">
                    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700/60 overflow-hidden">
                        <div className="px-5 py-4 border-b border-gray-200 dark:border-gray-700/60 flex items-center justify-between">
                            <h2 className="font-semibold text-gray-800 dark:text-gray-100 flex items-center gap-2">
                                <Clock className="w-4 h-4" /> {t('dashboard.recentPractice')}
                            </h2>
                            <Link href="/practice" className="text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200">
                                {t('dashboard.viewAll')} →
                            </Link>
                        </div>
                        {recentSessions.length > 0 ? (
                            <div className="divide-y divide-gray-100 dark:divide-gray-700/60">
                                {recentSessions.slice(0, 4).map(session => (
                                    <Link
                                        href={`/interview/${session.session_id}`}
                                        key={session.session_id}
                                        className="flex items-center gap-3 px-5 py-3 hover:bg-gray-50 dark:hover:bg-gray-700/30 transition-colors group"
                                    >
                                        <div className="flex-1 min-w-0">
                                            <p className="font-medium text-gray-800 dark:text-gray-100 truncate text-sm">{session.job_role}</p>
                                            <p className="text-xs text-gray-500 dark:text-gray-400">
                                                {new Date(session.created_at).toLocaleDateString()}
                                            </p>
                                        </div>
                                        {session.overall_score && (
                                            <span className={`text-sm font-bold ${getScoreColor(session.overall_score)}`}>
                                                {session.overall_score}
                                            </span>
                                        )}
                                        <ChevronRight className="w-4 h-4 text-gray-400 group-hover:text-gray-600 dark:group-hover:text-gray-300" />
                                    </Link>
                                ))}
                            </div>
                        ) : (
                            <div className="text-center py-10 px-5">
                                <PlayCircle className="w-10 h-10 text-gray-300 dark:text-gray-600 mx-auto mb-3" />
                                <p className="text-sm text-gray-500 dark:text-gray-400 mb-3">{t('dashboard.noSessions')}</p>
                                <Link href="/practice/new" className="text-sm text-[#424874] hover:text-[#363B5E] dark:text-[#A6B1E1] font-medium">
                                    {t('dashboard.startPractice')} →
                                </Link>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}

function getScoreColor(score: number) {
    if (score >= 80) return "text-[#424874] dark:text-[#A6B1E1]";
    if (score >= 60) return "text-yellow-600 dark:text-yellow-400";
    return "text-red-600 dark:text-red-400";
}
