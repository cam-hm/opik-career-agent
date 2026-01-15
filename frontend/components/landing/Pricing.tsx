"use client";

import { motion } from "framer-motion";
import { Check, Sparkles, Building2, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useLanguage } from "@/contexts/LanguageContext";
import { SignInButton, SignedIn, SignedOut } from "@clerk/nextjs";
import Link from "next/link";

const fadeInUp = {
    hidden: { opacity: 0, y: 30 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.6 } }
};

const staggerContainer = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { staggerChildren: 0.15 } }
};

export default function Pricing() {
    const { t } = useLanguage();

    const plans = [
        {
            key: "free",
            icon: <Zap className="w-6 h-6" />,
            popular: false,
        },
        {
            key: "pro",
            icon: <Sparkles className="w-6 h-6" />,
            popular: true,
        },
        {
            key: "enterprise",
            icon: <Building2 className="w-6 h-6" />,
            popular: false,
        }
    ];

    return (
        <section id="pricing" className="py-24 bg-[#F4EEFF]/20 dark:bg-gray-900/50 transition-colors">
            <div className="container mx-auto px-6">
                <motion.div
                    className="text-center max-w-2xl mx-auto mb-16"
                    initial="hidden"
                    whileInView="visible"
                    viewport={{ once: true, margin: "-100px" }}
                    variants={fadeInUp}
                >
                    <h2 className="text-4xl font-serif font-bold mb-4 text-[#424874] dark:text-[#A6B1E1]">
                        {t('pricing.title')}
                    </h2>
                    <div className="w-20 h-1 bg-[#DCD6F7] mx-auto mb-6"></div>
                    <p className="text-lg text-gray-600 dark:text-gray-400 font-light">
                        {t('pricing.subtitle')}
                    </p>
                </motion.div>

                <motion.div
                    className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto"
                    initial="hidden"
                    whileInView="visible"
                    viewport={{ once: true, margin: "-50px" }}
                    variants={staggerContainer}
                >
                    {plans.map((plan) => (
                        <PricingCard
                            key={plan.key}
                            planKey={plan.key}
                            icon={plan.icon}
                            popular={plan.popular}
                            t={t}
                        />
                    ))}
                </motion.div>
            </div>
        </section>
    );
}

function PricingCard({
    planKey,
    icon,
    popular,
    t
}: {
    planKey: string;
    icon: React.ReactNode;
    popular: boolean;
    t: (key: string) => string;
}) {
    const name = t(`pricing.plans.${planKey}.name`);
    const price = t(`pricing.plans.${planKey}.price`);
    const period = t(`pricing.plans.${planKey}.period`);
    const desc = t(`pricing.plans.${planKey}.desc`);
    const featuresStr = t(`pricing.plans.${planKey}.features`);
    const features = featuresStr.split('|');
    const cta = t(`pricing.plans.${planKey}.cta`);

    return (
        <motion.div
            className={`relative bg-white dark:bg-gray-800 rounded-2xl p-8 transition-all duration-300 group
                ${popular
                    ? 'border-2 border-[#424874] shadow-2xl scale-105 z-10'
                    : 'border border-gray-200 dark:border-gray-700 hover:shadow-xl hover:border-[#424874]/30'
                }`}
            variants={fadeInUp}
        >
            {popular && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                    <span className="bg-gradient-to-r from-[#424874] to-[#A6B1E1] text-white px-4 py-1 rounded-full text-sm font-medium shadow-lg">
                        {t('pricing.popular')}
                    </span>
                </div>
            )}

            <div className={`w-12 h-12 rounded-xl flex items-center justify-center mb-6
                ${popular
                    ? 'bg-[#424874] text-white'
                    : 'bg-[#F4EEFF] dark:bg-[#424874]/20 text-[#424874] dark:text-[#A6B1E1] group-hover:bg-[#424874] group-hover:text-white transition-colors'
                }`}
            >
                {icon}
            </div>

            <h3 className="text-2xl font-serif font-bold text-[#424874] dark:text-gray-100 mb-2">
                {name}
            </h3>

            <div className="mb-4">
                <span className="text-4xl font-bold text-gray-900 dark:text-white">{price}</span>
                {period && !period.includes('pricing.') && <span className="text-gray-500 dark:text-gray-400 ml-1">{period}</span>}
            </div>

            <p className="text-gray-600 dark:text-gray-400 mb-6 font-light">
                {desc}
            </p>

            <ul className="space-y-3 mb-8">
                {features.map((feature, idx) => (
                    <li key={idx} className="flex items-start gap-3">
                        <Check className="w-5 h-5 text-[#424874] dark:text-[#A6B1E1] flex-shrink-0 mt-0.5" />
                        <span className="text-gray-700 dark:text-gray-300 text-sm">{feature}</span>
                    </li>
                ))}
            </ul>

            <SignedOut>
                <SignInButton mode="modal">
                    <Button
                        className={`w-full h-12 rounded-xl font-medium transition-all duration-300 cursor-pointer
                            ${popular
                                ? 'bg-[#424874] text-white hover:bg-[#363B5E] hover:scale-105 shadow-lg'
                                : 'bg-white dark:bg-gray-700 text-[#424874] dark:text-white border-2 border-[#424874] hover:bg-[#424874] hover:text-white'
                            }`}
                    >
                        {cta}
                    </Button>
                </SignInButton>
            </SignedOut>
            <SignedIn>
                <Link href="/dashboard">
                    <Button
                        className={`w-full h-12 rounded-xl font-medium transition-all duration-300 cursor-pointer
                            ${popular
                                ? 'bg-[#424874] text-white hover:bg-[#363B5E] hover:scale-105 shadow-lg'
                                : 'bg-white dark:bg-gray-700 text-[#424874] dark:text-white border-2 border-[#424874] hover:bg-[#424874] hover:text-white'
                            }`}
                    >
                        {cta}
                    </Button>
                </Link>
            </SignedIn>
        </motion.div>
    );
}
