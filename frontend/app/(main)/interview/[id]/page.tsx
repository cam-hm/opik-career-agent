"use client";

import { useParams } from 'next/navigation';
import dynamic from 'next/dynamic';
import { useState, useEffect } from 'react';
import { fetchWithAuth } from "@/lib/api";
import { ENDPOINTS } from "@/lib/endpoints";
import { useAuth } from '@clerk/nextjs';
import ResumeAnalysis from '@/components/ResumeAnalysis';
import { Loader2 } from 'lucide-react';

const InterviewRoom = dynamic(() => import('@/components/InterviewRoom'), {
    ssr: false,
    loading: () => (
        <div className="flex items-center justify-center h-full bg-gray-900">
            <Loader2 className="w-8 h-8 animate-spin text-[#424874]" />
            <span className="ml-3 text-gray-300">Loading Interview Room...</span>
        </div>
    ),
});

export default function InterviewPage() {
    const params = useParams();
    const sessionId = params.id as string;
    const { getToken } = useAuth();
    const [started, setStarted] = useState(false);
    const [status, setStatus] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const checkStatus = async () => {
            try {
                // Use fetchWithAuth for consistent API calls
                const res = await fetchWithAuth(ENDPOINTS.INTERVIEW.DETAIL(sessionId), {}, getToken);
                if (res.ok) {
                    const data = await res.json();
                    setStatus(data.status);
                }
            } catch (error) {
                console.error("Failed to check session status", error);
            } finally {
                setLoading(false);
            }
        };
        checkStatus();
    }, [sessionId, getToken]);

    if (loading) {
        return (
            <div className="flex h-full items-center justify-center bg-gray-900">
                <Loader2 className="h-8 w-8 animate-spin text-[#424874]" />
            </div>
        );
    }

    if (status === 'completed') {
        if (typeof window !== 'undefined') {
            window.location.href = `/interview/${sessionId}/feedback`;
        }
        return (
            <div className="flex h-full items-center justify-center bg-gray-900">
                <Loader2 className="h-8 w-8 animate-spin text-[#424874]" />
                <span className="ml-3 text-gray-300">Redirecting to feedback...</span>
            </div>
        );
    }

    if (!started) {
        return (
            <main className="h-full w-full bg-gray-100 dark:bg-gray-900 py-12 overflow-y-auto">
                <ResumeAnalysis
                    sessionId={sessionId}
                    onStartInterview={() => setStarted(true)}
                />
            </main>
        )
    }

    return (
        <main className="h-full w-full bg-gray-900">
            <InterviewRoom sessionId={sessionId} />
        </main>
    );
}
