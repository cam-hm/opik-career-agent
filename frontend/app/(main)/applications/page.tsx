"use client";

import { useUser, useAuth } from "@clerk/nextjs";
import { useEffect, useState } from "react";
import Link from "next/link";
import { Loader2, Calendar, Layers, CheckCircle, XCircle, Clock, Plus, Briefcase, ChevronRight } from "lucide-react";
import { useLanguage } from "@/contexts/LanguageContext";
import { StatusBadge } from "@/components/common/StatusBadge";
import { fetchWithAuth } from "@/lib/api";
import { ENDPOINTS } from "@/lib/endpoints";

interface InterviewApplication {
    id: string;
    job_role: string;
    status: string;
    current_stage: number;
    created_at: string;
}

export default function ApplicationsPage() {
    const { user, isLoaded, isSignedIn } = useUser();
    const { getToken } = useAuth();
    const { t } = useLanguage();
    const [applications, setApplications] = useState<InterviewApplication[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (isLoaded && isSignedIn && user) {
            fetchApplications();
        } else if (isLoaded && !isSignedIn) {
            setLoading(false);
        }
    }, [isLoaded, isSignedIn, user]);

    const fetchApplications = async () => {
        try {
            const res = await fetchWithAuth(ENDPOINTS.APPLICATION.LIST, {}, getToken);
            if (res.ok) {
                const data = await res.json();
                setApplications(data);
            }
        } catch (error) {
            console.error("Failed to fetch applications", error);
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
                        <h1 className="text-2xl font-serif font-bold text-gray-800 dark:text-gray-100 italic">{t('applications.title')}</h1>
                        <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5">{t('applications.subtitle')}</p>
                    </div>
                    <Link
                        href="/applications/new"
                        className="inline-flex items-center gap-2 px-4 py-2 bg-[#424874] hover:bg-[#363B5E] text-white rounded-md text-sm font-medium transition-colors"
                    >
                        <Plus className="w-4 h-4" /> {t('applications.new')}
                    </Link>
                </div>
            </div>

            {applications.length === 0 ? (
                /* Empty State */
                <div className="text-center py-16 px-5">
                    <Layers className="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold mb-2 text-gray-800 dark:text-gray-100">{t('applications.noApps')}</h3>
                    <p className="text-gray-500 dark:text-gray-400 mb-6 max-w-sm mx-auto">{t('applications.noAppsDesc')}</p>
                    <Link
                        href="/applications/new"
                        className="inline-flex items-center gap-2 px-5 py-2.5 bg-[#424874] hover:bg-[#363B5E] text-white rounded-md font-medium transition-colors"
                    >
                        <Layers className="w-4 h-4" /> {t('setup.startApplication')}
                    </Link>
                </div>
            ) : (
                /* List View */
                <div className="divide-y divide-gray-100 dark:divide-gray-700/60">
                    {applications.map((app) => (
                        <Link
                            href={`/applications/${app.id}`}
                            key={app.id}
                            className="flex items-center gap-4 px-5 py-4 hover:bg-gray-50 dark:hover:bg-gray-700/30 transition-colors group"
                        >
                            {/* Icon */}
                            <div className="w-10 h-10 rounded-lg bg-gray-100 dark:bg-gray-700 flex items-center justify-center shrink-0">
                                <Briefcase className="w-5 h-5 text-gray-500 dark:text-gray-400" />
                            </div>

                            {/* Job Role & Date */}
                            <div className="flex-1 min-w-0">
                                <h3 className="font-medium text-gray-800 dark:text-gray-100 truncate">{app.job_role}</h3>
                                <p className="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-1 mt-0.5">
                                    <Calendar className="w-3 h-3" />
                                    {new Date(app.created_at).toLocaleDateString()}
                                </p>
                            </div>

                            {/* Progress */}
                            <div className="hidden sm:flex items-center gap-2">
                                <div className="flex gap-1">
                                    {[1, 2, 3].map((stage) => (
                                        <div
                                            key={stage}
                                            className={`w-6 h-1.5 rounded-full ${stage <= app.current_stage
                                                ? 'bg-green-500'
                                                : 'bg-gray-200 dark:bg-gray-600'
                                                }`}
                                        />
                                    ))}
                                </div>
                                <span className="text-xs text-gray-500 dark:text-gray-400 w-8">{app.current_stage}/3</span>
                            </div>

                            {/* Status Badge */}
                            <StatusBadge status={app.status} t={t} />

                            {/* Arrow */}
                            <ChevronRight className="w-4 h-4 text-gray-400 dark:text-gray-500 group-hover:text-gray-600 dark:group-hover:text-gray-300 transition-colors" />
                        </Link>
                    ))}
                </div>
            )}
        </div>
    );
}


