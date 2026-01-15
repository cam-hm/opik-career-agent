"use client"

import { useEffect, useState } from "react"
import { Loader2, ChevronLeft } from "lucide-react"
import Link from "next/link"
import { useAuth } from "@clerk/nextjs"
import { fetchWithAuth } from "@/lib/api"
import { ENDPOINTS } from "@/lib/endpoints"
import { useLanguage } from '@/contexts/LanguageContext';

interface InterviewSession {
    id: number
    session_id: string
    status: string
    feedback_markdown: string | null
    created_at: string
}

export default function ResultsView({ sessionId }: { sessionId: string }) {
    const { t } = useLanguage();
    const { getToken } = useAuth();
    const [session, setSession] = useState<InterviewSession | null>(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const fetchSession = async () => {
            try {
                const res = await fetchWithAuth(ENDPOINTS.INTERVIEW.DETAIL(sessionId), {}, getToken)
                if (res.ok) {
                    const data = await res.json()
                    setSession(data)
                }
            } catch (error) {
                console.error(error)
            } finally {
                setLoading(false)
            }
        }

        fetchSession()

        const interval = setInterval(() => {
            if (session?.status === 'completed') {
                clearInterval(interval)
                return
            }
            fetchSession()
        }, 5000)

        return () => clearInterval(interval)
    }, [sessionId, session?.status, getToken])

    if (loading && !session) {
        return (
            <div className="flex items-center justify-center h-64">
                <Loader2 className="h-8 w-8 animate-spin text-[#424874] dark:text-[#A6B1E1]" />
            </div>
        )
    }

    if (!session) {
        return (
            <div className="text-center py-12">
                <p className="text-gray-500 dark:text-gray-400">{t('feedback.sessionNotFound')}</p>
            </div>
        )
    }

    return (
        <div className="space-y-6">
            {/* Header Container */}
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700/60">
                <div className="px-5 py-4 flex items-center justify-between">
                    <div>
                        <Link
                            href="/practice"
                            className="flex items-center gap-1 text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 mb-2 transition-colors"
                        >
                            <ChevronLeft className="w-4 h-4" /> {t('feedback.backToPractice')}
                        </Link>
                        <h2 className="text-xl font-serif font-bold text-gray-800 dark:text-gray-100 italic">{t('feedback.sessionResults')}</h2>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-sm font-medium capitalize ${session.status === 'completed'
                        ? 'bg-[#DCD6F7] dark:bg-[#424874]/20 text-green-700 dark:text-[#A6B1E1]'
                        : 'bg-yellow-100 dark:bg-yellow-500/20 text-yellow-700 dark:text-yellow-400'
                        }`}>
                        {t(`status.${session.status}`) || session.status}
                    </span>
                </div>
            </div>

            {/* Feedback Container */}
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700/60 overflow-hidden">
                <div className="p-5">
                    {session.status === 'completed' && session.feedback_markdown ? (
                        <div className="prose dark:prose-invert max-w-none">
                            <pre className="whitespace-pre-wrap font-sans text-gray-700 dark:text-gray-300 leading-relaxed bg-gray-50 dark:bg-gray-700/30 p-6 rounded-xl border border-gray-100 dark:border-gray-700/60 shadow-inner">
                                {session.feedback_markdown}
                            </pre>
                        </div>
                    ) : (
                        <div className="text-center py-12">
                            <Loader2 className="h-10 w-10 animate-spin mx-auto mb-4 text-[#424874] dark:text-[#A6B1E1]" />
                            <p className="text-gray-800 dark:text-gray-100 font-medium">{t('feedback.analyzing')}</p>
                            <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">{t('feedback.analyzingWait')}</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}
