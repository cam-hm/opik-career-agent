"use client";

import { motion } from "framer-motion";
import { SignInButton, SignedIn, SignedOut } from "@clerk/nextjs";
import { Button } from "@/components/ui/button";
import { useLanguage } from "@/contexts/LanguageContext";
import Link from "next/link";

const fadeInUp = {
    hidden: { opacity: 0, y: 30 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.6 } }
};

export default function CTA() {
    const { t } = useLanguage();

    return (
        <section className="py-32 text-center bg-[#F4EEFF]/30 dark:bg-gray-900 transition-colors">
            <motion.div
                className="container mx-auto px-6 max-w-3xl"
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true }}
                variants={fadeInUp}
            >
                <h2 className="text-5xl font-serif font-bold mb-6 text-[#424874] dark:text-[#A6B1E1]">{t('cta.title')}</h2>
                <p className="text-xl text-gray-600 dark:text-gray-400 mb-12 font-light">
                    {t('cta.subtitle')}
                </p>
                <SignedOut>
                    <SignInButton mode="modal">
                        <Button className="h-16 px-12 text-xl bg-[#424874] text-white hover:bg-[#363B5E] hover:scale-105 transition-all duration-300 rounded-full shadow-2xl cursor-pointer">
                            {t('common.startTrial')}
                        </Button>
                    </SignInButton>
                </SignedOut>
                <SignedIn>
                    <Link href="/dashboard">
                        <Button className="h-16 px-12 text-xl bg-[#424874] text-white hover:bg-[#363B5E] hover:scale-105 transition-all duration-300 rounded-full shadow-2xl cursor-pointer">
                            {t('common.continuePractice')}
                        </Button>
                    </Link>
                </SignedIn>
            </motion.div>
        </section>
    );
}
