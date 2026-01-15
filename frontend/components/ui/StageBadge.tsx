import React from "react";
import { Users, Terminal, Brain, Check, Lock, Loader2 } from "lucide-react";

export type StageType = "hr" | "technical" | "behavioral";
export type StageStatus = "locked" | "active" | "completed";

interface StageBadgeProps {
    stage: StageType;
    status?: StageStatus;
    size?: "sm" | "md" | "lg";
    className?: string;
}

const STAGE_CONFIG = {
    hr: {
        icon: Users,
        color: "text-blue-600 dark:text-blue-400",
        bg: "bg-blue-100 dark:bg-blue-900/30",
        border: "border-blue-200 dark:border-blue-800",
        solid: "bg-blue-600 dark:bg-blue-500",
        ring: "ring-blue-500"
    },
    technical: {
        icon: Terminal,
        color: "text-purple-600 dark:text-purple-400",
        bg: "bg-purple-100 dark:bg-purple-900/30",
        border: "border-purple-200 dark:border-purple-800",
        solid: "bg-purple-600 dark:bg-purple-500",
        ring: "ring-purple-500"
    },
    behavioral: {
        icon: Brain,
        color: "text-yellow-600 dark:text-yellow-400",
        bg: "bg-yellow-100 dark:bg-yellow-900/30",
        border: "border-yellow-200 dark:border-yellow-800",
        solid: "bg-yellow-500 dark:bg-yellow-400",
        ring: "ring-yellow-500"
    }
};

const SIZES = {
    sm: { box: "w-8 h-8", icon: "w-4 h-4" },
    md: { box: "w-12 h-12", icon: "w-6 h-6" },
    lg: { box: "w-16 h-16", icon: "w-8 h-8" }
};

export const StageBadge: React.FC<StageBadgeProps> = ({ stage, status = "active", size = "md", className = "" }) => {
    const config = STAGE_CONFIG[stage];
    const sizeConfig = SIZES[size];
    const Icon = config.icon;

    if (status === "locked") {
        return (
            <div className={`relative flex items-center justify-center rounded-full bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-400 dark:text-gray-500 ${sizeConfig.box} ${className}`}>
                <Lock className={sizeConfig.icon} />
            </div>
        );
    }

    if (status === "completed") {
        return (
            <div className={`relative flex items-center justify-center rounded-full ${config.solid} text-white shadow-sm ${sizeConfig.box} ${className}`}>
                <Check className={sizeConfig.icon} strokeWidth={3} />
            </div>
        );
    }

    // Active State (Processing)
    return (
        <div className={`relative ${sizeConfig.box} ${className}`}>
            {/* Processing Spinner Ring */}
            <div className="absolute inset-0 rounded-full border-2 border-dashed border-gray-300 dark:border-gray-600" />
            <div className={`absolute inset-0 rounded-full border-2 border-dashed ${config.color} animate-spin-slow`} style={{ borderRightColor: 'transparent', borderBottomColor: 'transparent' }} />

            {/* Inner Content */}
            <div className={`absolute inset-0.5 rounded-full ${config.bg} flex items-center justify-center`}>
                <Icon className={`${sizeConfig.icon} ${config.color}`} />
            </div>

            {/* Pulse Effect for "Live" feeling */}
            <div className={`absolute -inset-1 rounded-full ${config.bg} opacity-20 animate-pulse`} />
        </div>
    );
};
