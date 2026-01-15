"use client";

import { motion } from "framer-motion";
import { Star } from "lucide-react";
import { useLanguage } from "@/contexts/LanguageContext";

const fadeInUp = {
    hidden: { opacity: 0, y: 30 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.6 } }
};

const staggerContainer = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { staggerChildren: 0.2 } }
};

export default function Testimonials() {
    const { t } = useLanguage();

    const testimonials = [
        { key: "1", avatarGradient: "from-pink-500 to-rose-500" },
        { key: "2", avatarGradient: "from-blue-500 to-indigo-500" },
        { key: "3", avatarGradient: "from-emerald-500 to-teal-500" },
    ];

    return (
        <section className="py-24 bg-[#424874] text-white relative overflow-hidden">
            <div className="absolute top-0 right-0 w-96 h-96 bg-[#A6B1E1] opacity-10 rounded-full blur-3xl transform translate-x-1/2 -translate-y-1/2"></div>

            <div className="container mx-auto px-6 relative z-10">
                <motion.h2
                    className="text-4xl font-serif font-bold text-center mb-16 text-white"
                    initial="hidden"
                    whileInView="visible"
                    viewport={{ once: true }}
                    variants={fadeInUp}
                >
                    {t('common.trustedBy')}
                </motion.h2>
                <motion.div
                    className="grid md:grid-cols-3 gap-8"
                    initial="hidden"
                    whileInView="visible"
                    viewport={{ once: true, margin: "-50px" }}
                    variants={staggerContainer}
                >
                    {testimonials.map((item) => (
                        <TestimonialCard
                            key={item.key}
                            quote={t(`testimonials.items.${item.key}.quote`)}
                            author={t(`testimonials.items.${item.key}.author`)}
                            role={t(`testimonials.items.${item.key}.role`)}
                            avatarGradient={item.avatarGradient}
                        />
                    ))}
                </motion.div>
            </div>
        </section>
    );
}

function TestimonialCard({ quote, author, role, avatarGradient }: { quote: string, author: string, role: string, avatarGradient: string }) {
    return (
        <motion.div
            className="bg-white/5 p-8 rounded-xl border border-white/10 hover:bg-white/10 transition-colors duration-300 relative"
            variants={fadeInUp}
        >
            <div className="absolute top-6 left-6 text-4xl font-serif text-[#A6B1E1] opacity-50">"</div>
            <div className="flex gap-1 mb-6 mt-4">
                {[1, 2, 3, 4, 5].map(i => <Star key={i} className="w-4 h-4 fill-[#A6B1E1] text-[#A6B1E1]" />)}
            </div>
            <p className="text-lg italic mb-8 text-gray-100 leading-relaxed font-light relative z-10">{quote}</p>
            <div className="flex items-center gap-4">
                <div className={`w-10 h-10 rounded-full bg-gradient-to-br ${avatarGradient} flex items-center justify-center text-white font-bold text-sm shadow-lg`}>
                    {author.charAt(0)}
                </div>
                <div>
                    <p className="font-bold text-white">{author}</p>
                    <p className="text-xs text-[#A6B1E1] uppercase tracking-widest">{role}</p>
                </div>
            </div>
        </motion.div>
    );
}
