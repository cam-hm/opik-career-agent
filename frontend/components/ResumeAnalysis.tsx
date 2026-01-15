"use client"

import { useState, useEffect } from "react"
import { Loader2, CheckCircle, AlertTriangle, Lightbulb, ArrowRight, Sparkles, ShieldCheck } from "lucide-react"
import { styles, getScoreColor, getScoreBg } from "@/lib/design-tokens"
import { useLanguage } from "@/contexts/LanguageContext";
import { useAuth } from "@clerk/nextjs";
import { fetchWithAuth } from "@/lib/api";
import { ENDPOINTS } from "@/lib/endpoints";

interface AnalysisResult {
    summary: string
    strengths: string[]
    weaknesses: string[]
    suggested_questions: string[]
    overall_score: number
}

interface ResumeAnalysisProps {
    sessionId: string
    onStartInterview: () => void
}

export default function ResumeAnalysis({ sessionId, onStartInterview }: ResumeAnalysisProps) {
    const { t } = useLanguage();
    const { getToken } = useAuth();
    const [analysis, setAnalysis] = useState<AnalysisResult | null>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        const fetchAnalysis = async () => {
            try {
                const res = await fetchWithAuth(ENDPOINTS.INTERVIEW.ANALYZE(sessionId), {
                    method: "POST"
                }, getToken)


                if (!res.ok) {
                    throw new Error("Failed to analyze resume")
                }

                const data = await res.json()
                setAnalysis(data)
            } catch (err) {
                console.error(err)
                setError(t('analysis.error'))
            } finally {
                setLoading(false)
            }
        }

        fetchAnalysis()
    }, [sessionId])

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
                <Loader2 className="h-10 w-10 animate-spin text-[#424874] dark:text-[#A6B1E1]" />
                <p className="text-gray-500 dark:text-gray-400">{t('analysis.loading')}</p>
            </div>
        )
    }

    if (error) {
        return (
            <div className="w-full max-w-2xl mx-auto">
                <div className="bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/30 rounded-xl p-6 text-center">
                    <AlertTriangle className="w-10 h-10 text-red-600 dark:text-red-400 mx-auto mb-3" />
                    <p className="text-red-700 dark:text-red-400 mb-4">{error}</p>
                    <button
                        onClick={onStartInterview}
                        className={`${styles.button.primary} px-6 py-3`}
                    >
                        {t('analysis.skip')}
                    </button>
                </div>
            </div>
        )
    }

    if (!analysis) return null

    return (
        <div className="w-full max-w-4xl mx-auto space-y-6 px-4 animate-fade-in-up">
            {/* Header */}
            <div className="text-center space-y-4 mb-10 relative">

                <div className="flex flex-col items-center gap-2">
                    <span className="text-[10px] font-mono tracking-widest text-gray-400 uppercase">
                        Confidential - Authorized Agents Only
                    </span>
                    <div className="inline-flex items-center gap-2 px-3 py-1 bg-[#DCD6F7]/50 dark:bg-[#424874]/30 text-[#424874] dark:text-[#A6B1E1] rounded-full text-xs font-semibold backdrop-blur-sm border border-[#A6B1E1]/20">
                        <ShieldCheck className="w-3.5 h-3.5" /> {t('analysis.complete')}
                    </div>
                </div>

                <h1 className="text-4xl md:text-5xl font-serif font-bold text-gray-900 dark:text-white tracking-tight">
                    {t('analysis.title')}
                </h1>
                <p className="text-lg text-gray-500 dark:text-gray-400 font-medium max-w-xl mx-auto">
                    {t('analysis.subtitle')}
                </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Score Card */}
                <div className={`${styles.card.base} p-8 relative overflow-hidden group`}>
                    <h3 className="text-xs font-bold text-gray-400 uppercase tracking-widest text-center mb-6">
                        {t('analysis.overallScore')}
                    </h3>
                    <div className={`aspect-square rounded-full border-4 border-[#DCD6F7] dark:border-[#424874] flex flex-col items-center justify-center relative z-10 mx-auto w-32 h-32`}>
                        <span className={`text-4xl font-serif font-bold ${getScoreColor(analysis.overall_score)}`}>
                            {analysis.overall_score}
                        </span>
                        <div className="h-px w-8 bg-gray-200 dark:bg-gray-700 my-1" />
                        <span className="text-xs font-mono text-gray-400">100</span>
                    </div>
                </div>

                {/* Summary Card */}
                <div className={`${styles.card.base} p-8 md:col-span-2 relative overflow-hidden`}>
                    <div className="absolute top-0 left-0 w-1 h-full bg-[#A6B1E1]" />
                    <h3 className="font-serif text-xl font-bold text-gray-900 dark:text-white mb-4">
                        {t('analysis.summary')}
                    </h3>
                    <p className="text-gray-600 dark:text-gray-300 leading-relaxed italic border-l-2 border-gray-100 dark:border-gray-700 pl-4">
                        "{analysis.summary}"
                    </p>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Strengths */}
                <div className="bg-white dark:bg-gray-800 rounded-xl p-8 border-t-4 border-green-500 shadow-sm">
                    <h3 className="flex items-center gap-2 font-serif text-lg font-bold text-gray-900 dark:text-white mb-6">
                        <CheckCircle className="w-5 h-5 text-green-500" /> {t('analysis.strengths')}
                    </h3>
                    <ul className="space-y-4">
                        {(analysis.strengths || []).map((item, i) => (
                            <li key={i} className="flex items-start text-sm text-gray-600 dark:text-gray-400">
                                <span className="mr-3 mt-1.5 w-1.5 h-1.5 rounded-full bg-green-500 shrink-0 shadow-[0_0_8px_rgba(34,197,94,0.5)]" />
                                {item}
                            </li>
                        ))}
                    </ul>
                </div>

                {/* Weaknesses */}
                <div className="bg-white dark:bg-gray-800 rounded-xl p-8 border-t-4 border-red-500 shadow-sm">
                    <h3 className="flex items-center gap-2 font-serif text-lg font-bold text-gray-900 dark:text-white mb-6">
                        <AlertTriangle className="w-5 h-5 text-red-500" /> {t('analysis.weaknesses')}
                    </h3>
                    <ul className="space-y-4">
                        {(analysis.weaknesses || []).map((item, i) => (
                            <li key={i} className="flex items-start text-sm text-gray-600 dark:text-gray-400">
                                <span className="mr-3 mt-1.5 w-1.5 h-1.5 rounded-full bg-red-500 shrink-0 shadow-[0_0_8px_rgba(239,68,68,0.5)]" />
                                {item}
                            </li>
                        ))}
                    </ul>
                </div>
            </div>

            {/* Suggested Questions */}
            <div className="bg-[#424874] dark:bg-gray-800/80 rounded-xl p-8 border border-[#A6B1E1]/20 shadow-xl relative overflow-hidden">
                <div className="absolute top-0 right-0 p-4 opacity-10">
                    <Lightbulb className="w-24 h-24 text-white" />
                </div>
                <h3 className="flex items-center gap-2 font-serif text-xl font-bold text-white mb-2 relative z-10">
                    <Lightbulb className="w-6 h-6 text-[#A6B1E1]" /> {t('analysis.questions')}
                </h3>
                <p className="text-sm text-[#DCD6F7] mb-6 relative z-10">{t('analysis.questionsDesc')}</p>
                <div className="space-y-3 relative z-10">
                    {(analysis.suggested_questions || []).map((q, i) => (
                        <div key={i} className="p-4 rounded-lg bg-white/10 dark:bg-black/20 text-[#F4EEFF] text-sm border border-white/10 backdrop-blur-md hover:bg-white/20 transition-all cursor-default">
                            {q}
                        </div>
                    ))}
                </div>
            </div>

            {/* CTA */}
            <div className="flex flex-col items-center pt-8 pb-12 space-y-4">
                <button
                    onClick={onStartInterview}
                    className="bg-[#424874] hover:bg-[#363B5E] text-white px-10 py-5 rounded-xl font-bold text-xl flex items-center gap-3 shadow-2xl hover:scale-105 transition-all group"
                >
                    {t('analysis.start')}
                    <ArrowRight className="w-6 h-6 group-hover:translate-x-1 transition-transform" />
                </button>
                <p className="text-xs text-gray-400 font-mono uppercase tracking-[0.2em]">
                    System Ready for Deployment
                </p>
            </div>
        </div>
    )
}
