"use client";

import { motion } from "framer-motion";
import { Mic, Zap, Shield } from "lucide-react";
import { useLanguage } from "@/contexts/LanguageContext";

const fadeInUp = {
    hidden: { opacity: 0, y: 30 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.6 } }
};

const staggerContainer = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { staggerChildren: 0.2 } }
};

export default function Features() {
    const { t } = useLanguage();

    return (
        <section className="py-24 bg-white dark:bg-gray-900 transition-colors">
            <div className="container mx-auto px-6">
                <motion.div
                    className="text-center max-w-2xl mx-auto mb-20"
                    initial="hidden"
                    whileInView="visible"
                    viewport={{ once: true, margin: "-100px" }}
                    variants={fadeInUp}
                >
                    <h2 className="text-4xl font-serif font-bold mb-4 text-[#424874] dark:text-[#A6B1E1]">{t('features.title')}</h2>
                    <div className="w-20 h-1 bg-[#DCD6F7] mx-auto mb-6"></div>
                    <p className="text-lg text-gray-600 dark:text-gray-400 font-light">{t('features.subtitle')}</p>
                </motion.div>

                <motion.div
                    className="grid md:grid-cols-3 gap-10"
                    initial="hidden"
                    whileInView="visible"
                    viewport={{ once: true, margin: "-50px" }}
                    variants={staggerContainer}
                >
                    <FeatureCard
                        icon={<Mic className="w-8 h-8" />}
                        title={t('features.cards.voice.title')}
                        description={t('features.cards.voice.desc')}
                    />
                    <FeatureCard
                        icon={<Zap className="w-8 h-8" />}
                        title={t('features.cards.feedback.title')}
                        description={t('features.cards.feedback.desc')}
                    />
                    <FeatureCard
                        icon={<Shield className="w-8 h-8" />}
                        title={t('features.cards.safe.title')}
                        description={t('features.cards.safe.desc')}
                    />
                </motion.div>
            </div>
        </section>
    );
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode, title: string, description: string }) {
    return (
        <motion.div
            className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 p-8 hover:shadow-xl hover:border-[#424874]/20 transition-all duration-300 group"
            variants={fadeInUp}
        >
            <div className="w-14 h-14 bg-[#F4EEFF] dark:bg-[#424874]/20 rounded-lg flex items-center justify-center mb-6 group-hover:bg-[#424874] group-hover:text-white transition-colors duration-300 text-[#424874] dark:text-[#A6B1E1]">
                {icon}
            </div>
            <h3 className="text-xl font-bold mb-3 font-serif text-[#424874] dark:text-gray-100">{title}</h3>
            <p className="text-gray-600 dark:text-gray-400 leading-relaxed font-light">
                {description}
            </p>
        </motion.div>
    );
}
