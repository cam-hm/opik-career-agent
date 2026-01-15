"use client";

import React, { useEffect, useState } from "react";
import { useAuth } from "@clerk/nextjs";
import { SkillRadar } from "@/components/gamification/SkillRadar";
import { CareerMap } from "@/components/gamification/CareerMap";
import { Loader2, Info } from "lucide-react";
import { gamificationApi, GamificationStatus, CareerNode } from "@/lib/api/gamification";
import { useRouter } from 'next/navigation';
import { useLanguage } from "@/contexts/LanguageContext";

// Simple Tooltip Component
function InfoTooltip({ text }: { text: string }) {
    return (
        <div className="relative group inline-flex ml-1.5">
            <Info className="h-4 w-4 text-muted-foreground cursor-help" />
            <div className="absolute top-full left-0 mt-2 px-3 py-2 bg-popover text-popover-foreground text-xs rounded-lg shadow-lg border border-border opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 whitespace-nowrap z-[100]">
                {text}
                <div className="absolute bottom-full left-2 border-4 border-transparent border-b-popover" />
            </div>
        </div>
    );
}

// Section Header Component for consistency
function SectionHeader({ title, tooltip, subtitle }: { title: string; tooltip: string; subtitle: string }) {
    return (
        <div className="flex flex-col space-y-1 pb-3">
            <div className="flex items-center">
                <h3 className="font-semibold leading-none tracking-tight">{title}</h3>
                <InfoTooltip text={tooltip} />
            </div>
            <p className="text-sm text-muted-foreground">{subtitle}</p>
        </div>
    );
}

export default function CareerPage() {
    const { getToken, isLoaded, isSignedIn } = useAuth();
    const { getLocalized } = useLanguage();
    const [loading, setLoading] = useState(true);
    const router = useRouter();

    // Data State
    const [status, setStatus] = useState<GamificationStatus | null>(null);
    const [nodes, setNodes] = useState<CareerNode[]>([]);

    useEffect(() => {
        if (isLoaded && !isSignedIn) {
            router.push('/');
            return;
        }

        const fetchData = async () => {
            if (!isLoaded || !isSignedIn) return;

            try {
                const token = await getToken();
                if (!token) return;

                const [statusData, treeData] = await Promise.all([
                    gamificationApi.getStatus(token),
                    gamificationApi.getTree(token)
                ]);

                setStatus(statusData);
                setNodes(treeData.nodes);

            } catch (error) {
                console.error("Failed to load gamification data", error);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, [isLoaded, isSignedIn, getToken, router]);

    const handleNodeClick = (nodeId: string, nodeStatus: string) => {
        if (nodeStatus === 'locked') return;
        router.push(`/practice?node_id=${nodeId}`);
    };

    if (!isLoaded || loading) {
        return (
            <div className="flex h-full items-center justify-center min-h-screen bg-background">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
        );
    }

    if (!isSignedIn) {
        return null;
    }

    return (
        <div className="flex flex-col h-[calc(100vh-64px)] p-6 bg-background text-foreground relative overflow-hidden">
            {/* Adaptive Grid Background */}
            <div className="absolute inset-0 bg-grid-pattern opacity-[0.03] dark:opacity-[0.1] pointer-events-none"></div>

            {/* Page Header */}
            <div className="flex items-center justify-between relative z-10 mb-4">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight text-primary">
                        Victory Road
                    </h2>
                    <p className="text-muted-foreground">
                        Practice interviews, unlock milestones, level up.
                    </p>
                </div>
            </div>

            {/* 3-Column Equal Layout */}
            <div className="grid gap-4 grid-cols-1 lg:grid-cols-3 flex-1 min-h-0 relative z-10">

                {/* COLUMN 1: Milestones */}
                <div className="flex flex-col min-h-0">
                    <div className="rounded-xl border border-border bg-card text-card-foreground shadow flex-1 p-4 relative flex flex-col min-h-0">
                        <SectionHeader
                            title="Milestones"
                            tooltip="Complete each milestone to progress. Click to start."
                            subtitle="Click to practice"
                        />

                        <CareerMap
                            nodes={nodes}
                            userNodes={status?.nodes || {}}
                            onNodeClick={handleNodeClick}
                            className="bg-muted/30 border-input flex-1 min-h-0"
                        />

                        {/* Legend */}
                        <div className="absolute bottom-4 right-4 flex flex-col gap-1.5 p-2 bg-background/80 backdrop-blur rounded-lg border border-border text-[10px] shadow-sm z-20">
                            <div className="flex items-center gap-1.5">
                                <div className="w-2.5 h-2.5 rounded-full bg-green-500"></div>
                                <span>Completed</span>
                            </div>
                            <div className="flex items-center gap-1.5">
                                <div className="w-2.5 h-2.5 rounded-full bg-indigo-500"></div>
                                <span>Ready</span>
                            </div>
                            <div className="flex items-center gap-1.5">
                                <div className="w-2.5 h-2.5 rounded-full bg-gray-300 dark:bg-gray-600"></div>
                                <span className="text-muted-foreground">Locked</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* COLUMN 2: Trainer Card */}
                <div className="flex flex-col min-h-0">
                    <div className="rounded-xl border border-border bg-card text-card-foreground shadow flex-1 p-4 flex flex-col min-h-0 overflow-auto">
                        <SectionHeader
                            title="Trainer Card"
                            tooltip="Your progress and skill ratings"
                            subtitle="Level up by completing milestones"
                        />

                        {/* Level & XP */}
                        <div className="flex items-center gap-3 mb-4">
                            <div className="h-12 w-12 rounded-full bg-gradient-to-br from-green-400 to-green-600 flex items-center justify-center text-lg font-bold text-white shadow-lg">
                                {status?.level || 1}
                            </div>
                            <div>
                                <div className="font-bold">{status?.rank_title || "Associate"}</div>
                                <div className="text-sm text-muted-foreground">{status?.xp || 0} XP</div>
                            </div>
                        </div>

                        {/* Radar Chart */}
                        {status?.stats && (
                            <div className="flex-1 min-h-[150px] w-full">
                                <SkillRadar stats={status.stats} />
                            </div>
                        )}
                    </div>
                </div>

                {/* COLUMN 3: Badges */}
                <div className="flex flex-col min-h-0">
                    <div className="rounded-xl border border-border bg-card text-card-foreground shadow flex-1 p-4 flex flex-col min-h-0 overflow-auto">
                        <SectionHeader
                            title="Badges"
                            tooltip="Earned by completing achievements"
                            subtitle="Collect them all!"
                        />

                        {/* Badge Grid */}
                        <div className="grid grid-cols-3 gap-3 flex-1 content-start">
                            {/* All Available Badges */}
                            {[
                                { id: 'first_step', name: { en: 'First Step', vi: 'Bước Đầu Tiên' }, icon: '🎯' },
                                { id: 'speed_demon', name: { en: 'Speed Demon', vi: 'Thần Tốc' }, icon: '⚡' },
                                { id: 'perfectionist', name: { en: 'Perfectionist', vi: 'Người Hoàn Hảo' }, icon: '💎' },
                                { id: 'streak_master', name: { en: 'Streak Master', vi: 'Trùm Streak' }, icon: '🔥' },
                                { id: 'expert', name: { en: 'Expert', vi: 'Chuyên Gia' }, icon: '🏆' },
                                { id: 'guru', name: { en: 'Guru', vi: 'Bậc Thầy' }, icon: '🧙' },
                                { id: 'legend', name: { en: 'Legend', vi: 'Huyền Thoại' }, icon: '👑' },
                                { id: 'champion', name: { en: 'Champion', vi: 'Nhà Vô Địch' }, icon: '🥇' },
                                { id: 'elite', name: { en: 'Elite', vi: 'Tinh Anh' }, icon: '⭐' },
                            ].map((badge) => {
                                const isUnlocked = status?.badges?.some(b => b.id === badge.id);
                                return (
                                    <div key={badge.id} className={`flex flex-col items-center ${!isUnlocked ? 'opacity-40' : ''}`}>
                                        <div className={`w-14 h-14 rounded-xl flex items-center justify-center shadow-md border-2 ${isUnlocked
                                            ? 'bg-gradient-to-br from-green-400 to-green-600 border-green-300'
                                            : 'bg-muted border-muted-foreground/20'
                                            }`}>
                                            <span className={`text-2xl ${!isUnlocked ? 'grayscale' : ''}`}>
                                                {isUnlocked ? badge.icon : '🔒'}
                                            </span>
                                        </div>
                                        <span className={`text-xs mt-1.5 text-center ${isUnlocked ? 'font-medium' : 'text-muted-foreground'}`}>
                                            {getLocalized(badge.name)}
                                        </span >
                                    </div >
                                );
                            })}
                        </div >
                    </div >
                </div >
            </div >
        </div >
    );
}
