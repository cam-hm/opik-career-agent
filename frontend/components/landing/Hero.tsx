"use client";

import { SignInButton, SignedIn, SignedOut } from "@clerk/nextjs";
import { Button } from "@/components/ui/button";
import { ArrowRight, Star } from "lucide-react";
import Link from "next/link";
import Image from "next/image";
import { motion } from "framer-motion";
import { useLanguage } from "@/contexts/LanguageContext";

const AVATARS = [
    { name: "Emma", bg: "from-pink-400 to-rose-500" },
    { name: "James", bg: "from-blue-400 to-indigo-500" },
    { name: "Sophia", bg: "from-amber-400 to-orange-500" },
    { name: "Lucas", bg: "from-emerald-400 to-teal-500" },
];

const fadeInUp = {
    hidden: { opacity: 0, y: 40 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.6, ease: [0.25, 0.46, 0.45, 0.94] as const } }
};

const staggerContainer = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { staggerChildren: 0.15 } }
};

export default function Hero() {
    const { t } = useLanguage();

    return (
        <section className="relative pt-20 pb-32 overflow-hidden bg-[#F4EEFF]/30 dark:bg-gray-900">
            <div className="absolute inset-0 z-0">
                <div className="absolute top-0 -left-4 w-72 h-72 bg-[#A6B1E1] rounded-full mix-blend-multiply filter blur-3xl opacity-10 animate-blob"></div>
                <div className="absolute top-0 -right-4 w-72 h-72 bg-[#424874] rounded-full mix-blend-multiply filter blur-3xl opacity-10 animate-blob animation-delay-2000"></div>
            </div>

            <div className="container mx-auto px-6 relative z-10">
                <div className="grid lg:grid-cols-2 gap-16 items-center">
                    <motion.div
                        className="space-y-8"
                        initial="hidden"
                        animate="visible"
                        variants={staggerContainer}
                    >
                        <motion.div variants={fadeInUp}>
                            <span className="inline-block py-1 px-3 rounded-full bg-[#424874]/5 text-[#424874] dark:bg-[#A6B1E1]/10 dark:text-[#A6B1E1] text-xs font-bold mb-6 tracking-widest uppercase border border-[#424874]/10 dark:border-[#A6B1E1]/20">
                                {t('hero.badge')}
                            </span>
                            <h1 className="text-5xl lg:text-7xl font-serif font-bold leading-[1.1] mb-6 text-gray-950 dark:text-white">
                                {t('hero.title')} <br />
                                <span className="relative inline-block">
                                    {t('hero.titleHighlight')}
                                    <div className="absolute -bottom-2 left-0 w-full h-3 bg-[#A6B1E1]/30 -rotate-1 rounded-full"></div>
                                </span>
                            </h1>
                            <p className="text-xl text-gray-600 dark:text-gray-400 leading-relaxed max-w-xl font-light">
                                {t('hero.subtitle')}
                            </p>
                        </motion.div>

                        <motion.div className="flex flex-col sm:flex-row gap-4" variants={fadeInUp}>
                            <SignedOut>
                                <SignInButton mode="modal">
                                    <Button className="h-14 px-8 text-lg bg-[#424874] text-white hover:bg-[#363B5E] hover:-translate-y-1 transition-all duration-300 rounded-md shadow-lg shadow-[#424874]/20 cursor-pointer">
                                        {t('common.startPractice')}
                                        <ArrowRight className="ml-2 h-5 w-5" />
                                    </Button>
                                </SignInButton>
                                <p className="text-sm text-gray-500 dark:text-gray-400 mt-2 sm:mt-0 sm:self-center px-4 italic">
                                    {t('common.noCreditCard')}
                                </p>
                            </SignedOut>
                            <SignedIn>
                                <Link href="/dashboard">
                                    <Button className="h-14 px-8 text-lg bg-[#424874] text-white hover:bg-[#363B5E] hover:-translate-y-1 transition-all duration-300 rounded-md shadow-lg shadow-[#424874]/20 cursor-pointer">
                                        {t('common.goToDashboard')}
                                        <ArrowRight className="ml-2 h-5 w-5" />
                                    </Button>
                                </Link>
                            </SignedIn>
                        </motion.div>

                        <motion.div className="flex items-center gap-4 pt-6 border-t border-gray-100 dark:border-gray-800" variants={fadeInUp}>
                            <div className="flex -space-x-3">
                                {AVATARS.map((avatar, i) => (
                                    <div
                                        key={i}
                                        className={`w-10 h-10 rounded-full border-2 border-white dark:border-gray-800 bg-gradient-to-br ${avatar.bg} flex items-center justify-center text-white text-xs font-bold shadow-md`}
                                    >
                                        {avatar.name.charAt(0)}
                                    </div>
                                ))}
                            </div>
                            <div className="text-sm">
                                <div className="flex gap-0.5 text-[#A6B1E1] mb-1">
                                    <Star className="w-4 h-4 fill-current" />
                                    <Star className="w-4 h-4 fill-current" />
                                    <Star className="w-4 h-4 fill-current" />
                                    <Star className="w-4 h-4 fill-current" />
                                    <Star className="w-4 h-4 fill-current" />
                                </div>
                                <p className="text-gray-500 dark:text-gray-400">{t('hero.lovedBy')}</p>
                            </div>
                        </motion.div>
                    </motion.div>

                    <motion.div
                        className="relative"
                        initial={{ opacity: 0, x: 50 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.8, delay: 0.3 }}
                    >
                        <div className="absolute -inset-4 bg-gradient-to-tr from-[#A6B1E1]/10 to-[#424874]/10 rounded-[2rem] transform rotate-3 z-0"></div>
                        <div className="relative z-10 bg-white dark:bg-gray-800 rounded-2xl shadow-2xl overflow-hidden border border-gray-100 dark:border-gray-700 group hover:shadow-[0_20px_50px_rgba(0,0,0,0.1)] transition-shadow duration-500">
                            <Image
                                src="/images/hero-illustration.png"
                                alt="Interview Simulation"
                                width={600}
                                height={400}
                                className="w-full h-auto object-cover transform scale-100 group-hover:scale-105 transition-transform duration-700"
                            />
                        </div>
                    </motion.div>
                </div>
            </div>
        </section>
    );
}
