"use client";

import Navbar from "./landing/Navbar";
import Hero from "./landing/Hero";
import Features from "./landing/Features";
import HowItWorks from "./landing/HowItWorks";
import Testimonials from "./landing/Testimonials";
import Pricing from "./landing/Pricing";
import FAQ from "./landing/FAQ";
import CTA from "./landing/CTA";
import Footer from "./landing/Footer";

/**
 * LandingPage component
 * Assembles the modular sections of the landing page.
 * Standardized to brand design tokens (Navy/Lavender).
 */
export default function LandingPage() {
    return (
        <div className="min-h-screen bg-white dark:bg-gray-950 transition-colors">
            <Navbar />
            <main>
                <Hero />
                <Features />
                <HowItWorks />
                <Testimonials />
                <Pricing />
                <FAQ />
                <CTA />
            </main>
            <Footer />
        </div>
    );
}
