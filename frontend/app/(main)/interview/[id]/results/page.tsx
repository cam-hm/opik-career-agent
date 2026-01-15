"use client";

import { useParams } from 'next/navigation';
import ResultsView from "@/components/ResultsView";

export default function ResultsPage() {
    const params = useParams();
    const sessionId = params.id as string;

    return (
        <main className="min-h-screen bg-gray-100 dark:bg-gray-900 p-8">
            <div className="max-w-4xl mx-auto">
                <ResultsView sessionId={sessionId} />
            </div>
        </main>
    );
}
