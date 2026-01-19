"use client";

import { useLanguage } from "@/contexts/LanguageContext";
import Image from "next/image";

export default function Footer() {
    const { t } = useLanguage();

    return (
        <footer className="py-12 border-t border-gray-100 dark:border-gray-800 bg-white dark:bg-gray-900 transition-colors">
            <div className="container mx-auto px-6 flex flex-col md:flex-row justify-between items-center text-gray-500 dark:text-gray-400 text-sm">

                <div className="flex items-center gap-2 mb-4 md:mb-0">
                    <Image
                        src="/logo.svg"
                        alt="Opik Agent Logo"
                        width={24}
                        height={24}
                        className="rounded"
                    />
                    <span className="font-serif font-bold text-[#424874] dark:text-[#A6B1E1]">Opik Agent</span>
                    <span className="mx-2 text-gray-300 dark:text-gray-700">|</span>
                    <span>&copy; {new Date().getFullYear()} Opik Agent.</span>
                </div>

                {/* Powered by Opik Badge */}
                <a
                    href="https://www.comet.com/site/products/opik/"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 px-3 py-1.5 mb-4 md:mb-0 bg-gradient-to-r from-[#424874]/10 to-[#A6B1E1]/10 dark:from-[#424874]/20 dark:to-[#A6B1E1]/20 border border-[#424874]/20 dark:border-[#A6B1E1]/30 rounded-full hover:border-[#424874]/40 dark:hover:border-[#A6B1E1]/50 transition-colors group"
                >
                    <span className="text-xs text-gray-500 dark:text-gray-400">Powered by</span>
                    <span className="text-xs font-semibold text-[#424874] dark:text-[#A6B1E1] group-hover:text-[#363B5E] dark:group-hover:text-white transition-colors">
                        Opik
                    </span>
                    <svg className="w-3 h-3 text-[#424874] dark:text-[#A6B1E1]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                    </svg>
                </a>

                <div className="flex gap-8">
                    <a href="/privacy" className="hover:text-[#424874] dark:hover:text-[#A6B1E1] transition-colors">{t('common.privacy')}</a>
                    <a href="/terms" className="hover:text-[#424874] dark:hover:text-[#A6B1E1] transition-colors">{t('common.terms')}</a>
                    <a href="/contact" className="hover:text-[#424874] dark:hover:text-[#A6B1E1] transition-colors">{t('common.contact')}</a>
                </div>
            </div>
        </footer>
    );
}
