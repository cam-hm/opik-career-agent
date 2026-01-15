"use client";

import { motion } from "framer-motion";
import { Video, MessageSquare } from "lucide-react";
import { useLanguage } from "@/contexts/LanguageContext";

const fadeInUp = {
    hidden: { opacity: 0, y: 30 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.6 } }
};

const staggerContainer = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { staggerChildren: 0.2 } }
};

const scaleIn = {
    hidden: { scale: 0.9, opacity: 0 },
    visible: { scale: 1, opacity: 1, transition: { duration: 0.8, ease: "easeOut" as const } }
};

export default function HowItWorks() {
    const { t } = useLanguage();

    return (
        <section className="py-24 bg-[#F4EEFF]/10 dark:bg-gray-800/20">
            <div className="container mx-auto px-6">
                <motion.h2
                    className="text-4xl font-serif font-bold text-center mb-16 text-[#424874] dark:text-[#A6B1E1]"
                    initial="hidden"
                    whileInView="visible"
                    viewport={{ once: true }}
                    variants={fadeInUp}
                >
                    {t('howItWorks.title')}
                </motion.h2>

                <div className="grid md:grid-cols-2 gap-16 items-center">
                    <motion.div
                        className="space-y-12"
                        initial="hidden"
                        whileInView="visible"
                        viewport={{ once: true, margin: "-50px" }}
                        variants={staggerContainer}
                    >
                        <Step
                            number="01"
                            title={t('howItWorks.steps.1.title')}
                            description={t('howItWorks.steps.1.desc')}
                        />
                        <Step
                            number="02"
                            title={t('howItWorks.steps.2.title')}
                            description={t('howItWorks.steps.2.desc')}
                        />
                        <Step
                            number="03"
                            title={t('howItWorks.steps.3.title')}
                            description={t('howItWorks.steps.3.desc')}
                        />
                    </motion.div>
                    <motion.div
                        className="bg-white dark:bg-gray-800 rounded-2xl p-8 border border-gray-100 dark:border-gray-700 shadow-xl h-[500px] flex items-center justify-center relative overflow-hidden group"
                        initial="hidden"
                        whileInView="visible"
                        viewport={{ once: true }}
                        variants={scaleIn}
                    >
                        <div className="absolute inset-0 bg-[#424874]/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>

                        {/* Illustration */}
                        <div className="relative w-64 h-80 bg-white dark:bg-gray-900 border border-gray-100 dark:border-gray-700 shadow-2xl rounded-xl p-6 flex flex-col gap-4 transform rotate-[-6deg] group-hover:rotate-0 transition-all duration-500">
                            <div className="w-12 h-12 rounded-full bg-[#424874] text-white flex items-center justify-center">
                                <Video className="w-6 h-6" />
                            </div>
                            <div className="h-2 w-20 bg-gray-100 dark:bg-gray-800 rounded"></div>
                            <div className="h-32 bg-gray-50 dark:bg-gray-800/50 rounded-lg border border-gray-100 dark:border-gray-700"></div>
                            <div className="space-y-2">
                                <div className="h-2 w-full bg-gray-50 dark:bg-gray-800/50 rounded"></div>
                                <div className="h-2 w-full bg-gray-50 dark:bg-gray-800/50 rounded"></div>
                                <div className="h-2 w-3/4 bg-gray-50 dark:bg-gray-800/50 rounded"></div>
                            </div>
                        </div>
                        <div className="absolute -right-4 -bottom-4 w-64 h-40 bg-white dark:bg-gray-900 border border-gray-100 dark:border-gray-700 shadow-2xl rounded-xl p-6 flex flex-col gap-3 transform rotate-[3deg] group-hover:translate-y-[-10px] transition-all duration-700 delay-100">
                            <div className="flex items-center gap-3">
                                <div className="w-8 h-8 rounded bg-[#DCD6F7] flex items-center justify-center text-[#424874]">
                                    <MessageSquare className="w-4 h-4" />
                                </div>
                                <div className="h-2 w-24 bg-gray-100 dark:bg-gray-800 rounded"></div>
                            </div>
                            <div className="h-full bg-gray-50 dark:bg-gray-800/50 rounded p-3 text-[10px] text-gray-500 dark:text-gray-400 leading-relaxed italic">
                                "Your strategy for conflict mitigation demonstrated high tactical awareness..."
                            </div>
                        </div>

                    </motion.div>
                </div>
            </div>
        </section>
    );
}

function Step({ number, title, description }: { number: string, title: string, description: string }) {
    return (
        <motion.div className="flex gap-8" variants={fadeInUp}>
            <div className="text-5xl font-serif font-bold text-[#DCD6F7] dark:text-[#A6B1E1]/20 -mt-2">
                {number}
            </div>
            <div>
                <h3 className="text-2xl font-bold mb-3 text-gray-900 dark:text-gray-100 font-serif">{title}</h3>
                <p className="text-gray-600 dark:text-gray-400 leading-relaxed font-light text-lg">
                    {description}
                </p>
            </div>
        </motion.div>
    );
}
