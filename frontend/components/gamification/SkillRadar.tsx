"use client";

import React from "react";
import {
    Radar,
    RadarChart,
    PolarGrid,
    PolarAngleAxis,
    PolarRadiusAxis,
    ResponsiveContainer,
} from "recharts";
import { useLanguage } from "@/contexts/LanguageContext";

type StatData = {
    subject: string;
    A: number;
    fullMark: number;
};

interface SkillRadarProps {
    stats: Record<string, number>;
    className?: string;
}

export const SkillRadar: React.FC<SkillRadarProps> = ({ stats, className }) => {
    // Map backend keys to Radar keys, defaulting to 0 if missing
    // Current Backend Keys: technical, communication, problem_solving, experience, professionalism, cultural_fit
    // Target Radar Axis: Clean Code, System Design, Algorithms, Communication, Tech Stack, Debugging

    // Mapping strategy:
    // technical -> Tech Stack
    // communication -> Communication
    // problem_solving -> Algorithms
    // experience -> System Design (ish)
    // professionalism -> Clean Code (ish)
    // cultural_fit -> Debugging (lol, no)

    // Better: Just check for the keys expected by the UI, if they exist use them, else fallback.
    // Or map all available keys dynamically?
    // Let's stick to the 6 fixed axes for the visual, but map standard gamification stats to them.

    const { t } = useLanguage();

    const data: StatData[] = [
        { subject: t('radar.standards'), A: stats.coding_standards || stats.professionalism || 0, fullMark: 100 },
        { subject: t('radar.design'), A: stats.system_design || stats.experience || 0, fullMark: 100 },
        { subject: t('radar.algorithms'), A: stats.algorithms || stats.problem_solving || 0, fullMark: 100 },
        { subject: t('radar.communication'), A: stats.communication || 0, fullMark: 100 },
        { subject: t('radar.stack'), A: stats.tech_proficiency || stats.technical || 0, fullMark: 100 },
        { subject: t('radar.debugging'), A: stats.debugging || stats.cultural_fit || 0, fullMark: 100 },
    ];

    return (
        <div className={`w-full h-full ${className}`}>
            <ResponsiveContainer width="100%" height="100%">
                <RadarChart cx="50%" cy="50%" outerRadius="70%" data={data}>
                    <PolarGrid stroke="#e5e7eb" />
                    <PolarAngleAxis
                        dataKey="subject"
                        tick={{ fill: "#6b7280", fontSize: 12 }}
                    />
                    <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                    <Radar
                        name="Skills"
                        dataKey="A"
                        stroke="#8884d8"
                        fill="#8884d8"
                        fillOpacity={0.6}
                    />
                </RadarChart>
            </ResponsiveContainer>
        </div>
    );
};
