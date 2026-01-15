"use client";

import { motion } from "framer-motion";
import { ChevronDown } from "lucide-react";
import { useState } from "react";
import { useLanguage } from "@/contexts/LanguageContext";

const fadeInUp = {
    hidden: { opacity: 0, y: 30 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.6 } }
};

const staggerContainer = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { staggerChildren: 0.1 } }
};

export default function FAQ() {
    const { t } = useLanguage();

    const faqKeys = ["1", "2", "3", "4", "5"];

    return (
        <section id="faq" className="py-24 bg-white dark:bg-gray-900 transition-colors">
            <div className="container mx-auto px-6">
                <motion.div
                    className="text-center max-w-2xl mx-auto mb-16"
                    initial="hidden"
                    whileInView="visible"
                    viewport={{ once: true, margin: "-100px" }}
                    variants={fadeInUp}
                >
                    <h2 className="text-4xl font-serif font-bold mb-4 text-[#424874] dark:text-[#A6B1E1]">
                        {t('faq.title')}
                    </h2>
                    <div className="w-20 h-1 bg-[#DCD6F7] mx-auto mb-6"></div>
                    <p className="text-lg text-gray-600 dark:text-gray-400 font-light">
                        {t('faq.subtitle')}
                    </p>
                </motion.div>

                <motion.div
                    className="max-w-3xl mx-auto space-y-4"
                    initial="hidden"
                    whileInView="visible"
                    viewport={{ once: true, margin: "-50px" }}
                    variants={staggerContainer}
                >
                    {faqKeys.map((key) => (
                        <FAQItem
                            key={key}
                            question={t(`faq.items.${key}.q`)}
                            answer={t(`faq.items.${key}.a`)}
                        />
                    ))}
                </motion.div>
            </div>
        </section>
    );
}

function FAQItem({ question, answer }: { question: string; answer: string }) {
    const [isOpen, setIsOpen] = useState(false);

    return (
        <motion.div
            className="border border-gray-200 dark:border-gray-700 rounded-xl overflow-hidden"
            variants={fadeInUp}
        >
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="w-full px-6 py-5 flex items-center justify-between text-left bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-750 transition-colors cursor-pointer"
            >
                <span className="font-medium text-gray-900 dark:text-gray-100 pr-4">
                    {question}
                </span>
                <ChevronDown
                    className={`w-5 h-5 text-[#424874] dark:text-[#A6B1E1] flex-shrink-0 transition-transform duration-300 ${isOpen ? 'rotate-180' : ''
                        }`}
                />
            </button>
            <motion.div
                initial={false}
                animate={{
                    height: isOpen ? 'auto' : 0,
                    opacity: isOpen ? 1 : 0
                }}
                transition={{ duration: 0.3, ease: "easeInOut" }}
                className="overflow-hidden"
            >
                <div className="px-6 pb-5 pt-2 bg-gray-50 dark:bg-gray-800/50">
                    <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
                        {answer}
                    </p>
                </div>
            </motion.div>
        </motion.div>
    );
}
