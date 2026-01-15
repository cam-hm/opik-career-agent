"use client";

import { useState } from "react";
import Link from "next/link";
import { ArrowLeft, Send } from "lucide-react";

export default function ContactPage() {
    const [submitted, setSubmitted] = useState(false);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        setSubmitted(true);
    };

    return (
        <div className="min-h-screen bg-white">
            <div className="container mx-auto px-6 py-12 max-w-2xl">
                <Link
                    href="/"
                    className="inline-flex items-center text-slate-500 hover:text-slate-800 transition-colors mb-8"
                >
                    <ArrowLeft className="w-4 h-4 mr-2" />
                    Back to Home
                </Link>

                <div className="bg-white rounded-2xl shadow-xl border border-slate-100 p-8 md:p-12 overflow-hidden relative">
                    {/* Background decorations */}
                    <div className="absolute top-0 right-0 w-64 h-64 bg-yellow-50 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 -z-10" />

                    <h1 className="text-3xl md:text-4xl font-serif font-bold text-[#1a1a1a] mb-4">
                        Contact Support
                    </h1>
                    <p className="text-slate-600 mb-8">
                        Have questions or need help? Send us a message and we'll get back to you as soon as possible.
                    </p>

                    {submitted ? (
                        <div className="bg-green-50 text-green-800 p-6 rounded-xl border border-green-100 flex flex-col items-center text-center animate-in fade-in duration-500">
                            <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mb-3 text-2xl">
                                ✨
                            </div>
                            <h3 className="font-bold text-lg mb-1">Message Sent!</h3>
                            <p className="text-sm opacity-90">
                                Thanks for reaching out. We'll be in touch shortly.
                            </p>
                            <button
                                onClick={() => setSubmitted(false)}
                                className="mt-6 text-sm font-medium text-green-700 hover:text-green-900 underline underline-offset-4"
                            >
                                Send another message
                            </button>
                        </div>
                    ) : (
                        <form onSubmit={handleSubmit} className="space-y-6">
                            <div>
                                <label htmlFor="email" className="block text-sm font-medium text-[#1a1a1a] mb-2">
                                    Email Address
                                </label>
                                <input
                                    type="email"
                                    id="email"
                                    required
                                    className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-[#1a1a1a] focus:ring-1 focus:ring-[#1a1a1a] outline-none transition-all placeholder:text-slate-400 bg-slate-50/50"
                                    placeholder="you@example.com"
                                />
                            </div>

                            <div>
                                <label htmlFor="subject" className="block text-sm font-medium text-[#1a1a1a] mb-2">
                                    Subject
                                </label>
                                <select
                                    id="subject"
                                    className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-[#1a1a1a] focus:ring-1 focus:ring-[#1a1a1a] outline-none transition-all bg-slate-50/50"
                                >
                                    <option>Account Issue</option>
                                    <option>Feedback & Suggestions</option>
                                    <option>Billing Question</option>
                                    <option>Other</option>
                                </select>
                            </div>

                            <div>
                                <label htmlFor="message" className="block text-sm font-medium text-[#1a1a1a] mb-2">
                                    Message
                                </label>
                                <textarea
                                    id="message"
                                    required
                                    rows={5}
                                    className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-[#1a1a1a] focus:ring-1 focus:ring-[#1a1a1a] outline-none transition-all placeholder:text-slate-400 bg-slate-50/50 resize-none"
                                    placeholder="How can we help you?"
                                ></textarea>
                            </div>

                            <button
                                type="submit"
                                className="w-full bg-[#1a1a1a] text-white font-medium py-3.5 rounded-xl hover:bg-black transition-all transform active:scale-[0.98] flex items-center justify-center gap-2 group shadow-lg shadow-black/5"
                            >
                                Send Message
                                <Send className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                            </button>
                        </form>
                    )}
                </div>
            </div>
        </div>
    );
}
