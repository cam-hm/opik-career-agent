"use client";

import UploadDropzone from "@/components/UploadDropzone";
import { ChevronLeft } from "lucide-react";
import { useRouter } from "next/navigation";
import { useLanguage } from "@/contexts/LanguageContext";

export default function NewPracticePage() {
    const router = useRouter();
    const { t } = useLanguage();

    return (
        <div className="space-y-6">
            {/* Header Container */}
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700/60">
                <div className="px-5 py-4 flex items-center gap-4">
                    {/* Back Button - Icon Circle */}
                    <button
                        onClick={() => router.push('/practice')}
                        className="w-9 h-9 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 flex items-center justify-center transition-colors shrink-0"
                        title="Back to Practice"
                    >
                        <ChevronLeft className="w-5 h-5 text-gray-600 dark:text-gray-300" />
                    </button>
                    {/* Title */}
                    <div className="flex-1 min-w-0">
                        <h1 className="text-xl font-semibold text-gray-900 dark:text-white">{t('setup.sparringTitle')}</h1>
                        <p className="text-sm text-gray-500 dark:text-gray-400">{t('setup.sparringDesc')}</p>
                    </div>
                </div>
            </div>

            {/* Form Container */}
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700/60 p-5">
                <UploadDropzone mode="practice" />
            </div>
        </div>
    );
}
