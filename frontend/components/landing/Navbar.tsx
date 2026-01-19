"use client";

import Link from "next/link";
import Image from "next/image";
import { SignInButton, SignedIn, SignedOut } from "@clerk/nextjs";
import { Button } from "@/components/ui/button";
import { useLanguage } from "@/contexts/LanguageContext";
import ThemeToggle from "@/components/layout/ThemeToggle";



export default function Navbar() {
    const { t } = useLanguage();

    return (
        <nav className="border-b border-gray-100 dark:border-gray-800 bg-white/80 dark:bg-gray-900/80 backdrop-blur-md sticky top-0 z-50 transition-all duration-300">
            <div className="container mx-auto px-6 h-20 flex items-center justify-between">

                <div className="flex items-center gap-2">
                    <Image
                        src="/logo.svg"
                        alt="Opik Agent Logo"
                        width={32}
                        height={32}
                        className="rounded"
                    />
                    <span className="font-serif text-2xl font-bold tracking-tight text-[#424874] dark:text-[#A6B1E1]">Opik Agent</span>
                </div>

                <div className="flex items-center gap-4">
                    <ThemeToggle />

                    <SignedIn>
                        <Link href="/dashboard">
                            <Button className="bg-[#424874] text-white hover:bg-[#363B5E] rounded-md px-6 shadow-sm font-medium cursor-pointer">
                                {t('common.dashboard')}
                            </Button>
                        </Link>
                    </SignedIn>
                    <SignedOut>
                        <SignInButton mode="modal">
                            <Button variant="ghost" className="text-gray-600 hover:text-[#424874] dark:text-gray-400 dark:hover:text-[#A6B1E1] font-medium cursor-pointer">
                                {t('common.signIn')}
                            </Button>
                        </SignInButton>
                        <SignInButton mode="modal">
                            <Button className="bg-[#424874] text-white hover:bg-[#363B5E] rounded-md px-6 shadow-sm font-medium cursor-pointer">
                                {t('common.getStarted')}
                            </Button>
                        </SignInButton>
                    </SignedOut>
                </div>
            </div>
        </nav>
    );
}
