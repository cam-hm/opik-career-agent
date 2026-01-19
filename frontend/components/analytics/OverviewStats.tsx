import { Target, Calendar, Activity, TrendingUp } from "lucide-react";

interface OverviewMetrics {
    total_sessions: number;
    avg_score: number | null;
    opik_tracked_sessions: number;
    opik_coverage_percent: number;
    stage_distribution: Record<string, number>;
    score_trend: "up" | "down" | "stable" | "no_data";
    date_range_days: number;
}

interface OverviewStatsProps {
    metrics: OverviewMetrics;
    trendIcon: React.ReactNode;
}

export default function OverviewStats({ metrics, trendIcon }: OverviewStatsProps) {
    const stages = Object.entries(metrics.stage_distribution);

    return (
        <div className="space-y-4">
            {/* Primary Stats */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700/60 p-4">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-lg bg-[#DCD6F7] dark:bg-[#424874]/20 flex items-center justify-center">
                            <Calendar className="w-5 h-5 text-[#424874] dark:text-[#A6B1E1]" />
                        </div>
                        <div>
                            <p className="text-2xl font-bold text-gray-800 dark:text-gray-100">{metrics.total_sessions}</p>
                            <p className="text-xs text-gray-500 dark:text-gray-400">Total Sessions</p>
                        </div>
                    </div>
                </div>

                <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700/60 p-4">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-lg bg-blue-100 dark:bg-blue-500/20 flex items-center justify-center">
                            <Target className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                        </div>
                        <div>
                            <p className="text-2xl font-bold text-gray-800 dark:text-gray-100">
                                {metrics.avg_score?.toFixed(1) || '-'}
                            </p>
                            <p className="text-xs text-gray-500 dark:text-gray-400">Average Score</p>
                        </div>
                    </div>
                </div>

                <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700/60 p-4">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-lg bg-purple-100 dark:bg-purple-500/20 flex items-center justify-center">
                            <Activity className="w-5 h-5 text-purple-600 dark:text-purple-400" />
                        </div>
                        <div>
                            <p className="text-2xl font-bold text-gray-800 dark:text-gray-100">
                                {metrics.opik_coverage_percent.toFixed(0)}%
                            </p>
                            <p className="text-xs text-gray-500 dark:text-gray-400">Opik Coverage</p>
                        </div>
                    </div>
                </div>

                <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700/60 p-4">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-lg bg-green-100 dark:bg-green-500/20 flex items-center justify-center">
                            {trendIcon}
                        </div>
                        <div>
                            <p className="text-2xl font-bold text-gray-800 dark:text-gray-100 capitalize">
                                {metrics.score_trend === "no_data" ? "-" : metrics.score_trend}
                            </p>
                            <p className="text-xs text-gray-500 dark:text-gray-400">Score Trend</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Stage Distribution */}
            {stages.length > 0 && (
                <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700/60 p-5">
                    <h3 className="font-semibold text-gray-800 dark:text-gray-100 mb-4 flex items-center gap-2">
                        <TrendingUp className="w-4 h-4" /> Stage Distribution
                    </h3>
                    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                        {stages.map(([stage, count]) => (
                            <div key={stage} className="flex items-center gap-2">
                                <div className="flex-1">
                                    <div className="flex items-center justify-between mb-1">
                                        <span className="text-sm font-medium text-gray-700 dark:text-gray-300 capitalize">
                                            {stage.replace('_', ' ')}
                                        </span>
                                        <span className="text-sm text-gray-500 dark:text-gray-400">{count}</span>
                                    </div>
                                    <div className="h-2 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden">
                                        <div
                                            className="h-full bg-[#424874] dark:bg-[#A6B1E1] rounded-full"
                                            style={{
                                                width: `${(count / metrics.total_sessions) * 100}%`
                                            }}
                                        />
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
