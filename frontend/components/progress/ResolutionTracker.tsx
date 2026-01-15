"use client";

import { useState } from "react";
import { useAuth } from "@clerk/nextjs";
import {
    Target,
    Plus,
    CheckCircle2,
    Clock,
    TrendingUp,
    ChevronRight,
    Sparkles,
    X,
} from "lucide-react";
import { fetchWithAuth } from "@/lib/api";
import { ENDPOINTS } from "@/lib/endpoints";

interface Resolution {
    id: string;
    title: string;
    description?: string;
    target_role?: string;
    target_skills: Record<string, number>;
    baseline_skills: Record<string, number>;
    target_date?: string;
    status: string;
    created_at?: string;
}

interface ResolutionProgress {
    resolution_id: string;
    title: string;
    overall_progress: number;
    skill_progress: Record<string, {
        baseline: number;
        current: number;
        target: number;
        progress_percent: number;
    }>;
    days_remaining?: number;
    status: string;
}

interface Props {
    resolutions: Resolution[];
    resolutionProgress: ResolutionProgress[];
    onRefresh: () => void;
}

export default function ResolutionTracker({ resolutions, resolutionProgress, onRefresh }: Props) {
    const { getToken } = useAuth();
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [creating, setCreating] = useState(false);
    const [formData, setFormData] = useState({
        title: "",
        description: "",
        target_role: "",
    });

    const handleCreate = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!formData.title.trim()) return;

        setCreating(true);
        try {
            const res = await fetchWithAuth(
                ENDPOINTS.PROGRESS.RESOLUTIONS,
                {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(formData),
                },
                getToken
            );

            if (res.ok) {
                setShowCreateModal(false);
                setFormData({ title: "", description: "", target_role: "" });
                onRefresh();
            }
        } catch (error) {
            console.error("Failed to create resolution:", error);
        } finally {
            setCreating(false);
        }
    };

    const handleComplete = async (resolutionId: string) => {
        try {
            const res = await fetchWithAuth(
                ENDPOINTS.PROGRESS.RESOLUTION_COMPLETE(resolutionId),
                { method: "POST" },
                getToken
            );

            if (res.ok) {
                onRefresh();
            }
        } catch (error) {
            console.error("Failed to complete resolution:", error);
        }
    };

    const getProgressForResolution = (resolutionId: string) => {
        return resolutionProgress.find(p => p.resolution_id === resolutionId);
    };

    return (
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700/60 overflow-hidden">
            <div className="px-5 py-4 border-b border-gray-200 dark:border-gray-700/60 flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <Sparkles className="w-5 h-5 text-amber-500" />
                    <h2 className="font-semibold text-gray-800 dark:text-gray-100">
                        2026 Career Resolutions
                    </h2>
                </div>
                <button
                    onClick={() => setShowCreateModal(true)}
                    className="flex items-center gap-1 px-3 py-1.5 text-sm bg-[#424874] hover:bg-[#363B5E] text-white rounded-lg transition-colors"
                >
                    <Plus className="w-4 h-4" />
                    New Resolution
                </button>
            </div>

            {resolutions.length === 0 ? (
                <div className="text-center py-12 px-5">
                    <Target className="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-800 dark:text-gray-100 mb-2">
                        Set Your 2026 Career Goals
                    </h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400 mb-4 max-w-sm mx-auto">
                        Create resolutions to track your career growth. We'll automatically
                        measure your progress through interview sessions.
                    </p>
                    <button
                        onClick={() => setShowCreateModal(true)}
                        className="inline-flex items-center gap-2 px-4 py-2 bg-[#424874] hover:bg-[#363B5E] text-white rounded-lg transition-colors"
                    >
                        <Plus className="w-4 h-4" />
                        Create Your First Resolution
                    </button>
                </div>
            ) : (
                <div className="divide-y divide-gray-100 dark:divide-gray-700/60">
                    {resolutions.map((resolution) => {
                        const progress = getProgressForResolution(resolution.id);
                        const progressPercent = progress?.overall_progress || 0;

                        return (
                            <div
                                key={resolution.id}
                                className="p-5 hover:bg-gray-50 dark:hover:bg-gray-700/30 transition-colors"
                            >
                                <div className="flex items-start justify-between mb-3">
                                    <div className="flex-1">
                                        <div className="flex items-center gap-2">
                                            <h3 className="font-medium text-gray-800 dark:text-gray-100">
                                                {resolution.title}
                                            </h3>
                                            {resolution.status === "completed" && (
                                                <span className="px-2 py-0.5 text-xs bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 rounded-full">
                                                    Completed
                                                </span>
                                            )}
                                        </div>
                                        {resolution.description && (
                                            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                                                {resolution.description}
                                            </p>
                                        )}
                                        {resolution.target_role && (
                                            <p className="text-xs text-[#424874] dark:text-[#A6B1E1] mt-1">
                                                Target: {resolution.target_role}
                                            </p>
                                        )}
                                    </div>
                                    {resolution.status === "active" && (
                                        <button
                                            onClick={() => handleComplete(resolution.id)}
                                            className="p-2 text-gray-400 hover:text-green-500 transition-colors"
                                            title="Mark as completed"
                                        >
                                            <CheckCircle2 className="w-5 h-5" />
                                        </button>
                                    )}
                                </div>

                                {/* Progress bar */}
                                <div className="mb-3">
                                    <div className="flex items-center justify-between text-xs mb-1">
                                        <span className="text-gray-500 dark:text-gray-400">Progress</span>
                                        <span className="font-medium text-gray-700 dark:text-gray-300">
                                            {progressPercent}%
                                        </span>
                                    </div>
                                    <div className="h-2 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden">
                                        <div
                                            className="h-full bg-gradient-to-r from-[#424874] to-[#A6B1E1] rounded-full transition-all duration-500"
                                            style={{ width: `${progressPercent}%` }}
                                        />
                                    </div>
                                </div>

                                {/* Skill progress breakdown */}
                                {progress?.skill_progress && Object.keys(progress.skill_progress).length > 0 && (
                                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 mt-3">
                                        {Object.entries(progress.skill_progress).slice(0, 6).map(([skill, data]) => (
                                            <div
                                                key={skill}
                                                className="flex items-center gap-2 text-xs bg-gray-50 dark:bg-gray-700/50 px-2 py-1.5 rounded"
                                            >
                                                <TrendingUp className={`w-3 h-3 ${
                                                    data.progress_percent >= 100
                                                        ? 'text-green-500'
                                                        : data.progress_percent >= 50
                                                            ? 'text-amber-500'
                                                            : 'text-gray-400'
                                                }`} />
                                                <span className="text-gray-600 dark:text-gray-300 capitalize truncate">
                                                    {skill.replace(/_/g, ' ')}
                                                </span>
                                                <span className="ml-auto text-gray-400">
                                                    {data.progress_percent}%
                                                </span>
                                            </div>
                                        ))}
                                    </div>
                                )}

                                {/* Days remaining */}
                                {progress?.days_remaining !== undefined && progress.days_remaining > 0 && (
                                    <div className="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400 mt-3">
                                        <Clock className="w-3 h-3" />
                                        {progress.days_remaining} days remaining
                                    </div>
                                )}
                            </div>
                        );
                    })}
                </div>
            )}

            {/* Create Modal */}
            {showCreateModal && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
                    <div className="bg-white dark:bg-gray-800 rounded-xl w-full max-w-md shadow-xl">
                        <div className="px-5 py-4 border-b border-gray-200 dark:border-gray-700/60 flex items-center justify-between">
                            <h3 className="font-semibold text-gray-800 dark:text-gray-100">
                                New 2026 Resolution
                            </h3>
                            <button
                                onClick={() => setShowCreateModal(false)}
                                className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
                            >
                                <X className="w-5 h-5" />
                            </button>
                        </div>
                        <form onSubmit={handleCreate} className="p-5 space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                                    Resolution Title *
                                </label>
                                <input
                                    type="text"
                                    value={formData.title}
                                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                                    placeholder="e.g., Master System Design interviews"
                                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-100 focus:ring-2 focus:ring-[#424874] focus:border-transparent"
                                    required
                                    minLength={3}
                                    maxLength={200}
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                                    Description
                                </label>
                                <textarea
                                    value={formData.description}
                                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                    placeholder="What do you want to achieve?"
                                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-100 focus:ring-2 focus:ring-[#424874] focus:border-transparent resize-none h-20"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                                    Target Role
                                </label>
                                <input
                                    type="text"
                                    value={formData.target_role}
                                    onChange={(e) => setFormData({ ...formData, target_role: e.target.value })}
                                    placeholder="e.g., Senior Software Engineer"
                                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-100 focus:ring-2 focus:ring-[#424874] focus:border-transparent"
                                />
                            </div>
                            <div className="flex gap-3 pt-2">
                                <button
                                    type="button"
                                    onClick={() => setShowCreateModal(false)}
                                    className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    disabled={creating || !formData.title.trim()}
                                    className="flex-1 px-4 py-2 bg-[#424874] hover:bg-[#363B5E] text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    {creating ? "Creating..." : "Create Resolution"}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}
