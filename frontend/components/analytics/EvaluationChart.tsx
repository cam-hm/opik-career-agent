import { Award, BarChart3, ExternalLink } from "lucide-react";
import Link from "next/link";
import { getOpikTraceUrl } from "@/lib/opik";
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    PieChart,
    Pie,
    Cell,
    Legend
} from "recharts";

interface SessionSummary {
    session_id: string;
    job_role: string | null;
    stage_type: string | null;
    overall_score: number | null;
    created_at: string | null;
    opik_trace_id: string | null;
}

interface EvaluationMetrics {
    avg_scores_by_stage: Record<string, number>;
    competency_breakdown: Record<string, number>;
    score_distribution: Record<string, number>;
    recent_sessions: SessionSummary[];
}

interface EvaluationChartProps {
    metrics: EvaluationMetrics;
}

const COLORS = ['#424874', '#A6B1E1', '#F4EEFF', '#DCD6F7'];
const SCORE_COLORS = {
    "0-49": "#ef4444",
    "50-69": "#f59e0b",
    "70-89": "#3b82f6",
    "90-100": "#10b981"
};

export default function EvaluationChart({ metrics }: EvaluationChartProps) {
    // Prepare data for charts
    const stageData = Object.entries(metrics.avg_scores_by_stage).map(([stage, score]) => ({
        stage: stage.replace('_', ' ').toUpperCase(),
        score: Math.round(score)
    }));

    const competencyData = Object.entries(metrics.competency_breakdown).map(([comp, score]) => ({
        name: comp.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
        value: Math.round(score)
    }));

    const distributionData = Object.entries(metrics.score_distribution)
        .filter(([, count]) => count > 0)
        .map(([range, count]) => ({
            range,
            count,
            fill: SCORE_COLORS[range as keyof typeof SCORE_COLORS]
        }));

    return (
        <div className="space-y-6">
            {/* Score by Stage */}
            {stageData.length > 0 && (
                <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700/60 p-5">
                    <h3 className="font-semibold text-gray-800 dark:text-gray-100 mb-4 flex items-center gap-2">
                        <BarChart3 className="w-4 h-4" /> Average Score by Stage
                    </h3>
                    <div className="h-[250px]">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={stageData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                                <XAxis
                                    dataKey="stage"
                                    tick={{ fontSize: 12, fill: '#6b7280' }}
                                    axisLine={{ stroke: '#e5e7eb' }}
                                />
                                <YAxis
                                    domain={[0, 100]}
                                    tick={{ fontSize: 12, fill: '#6b7280' }}
                                    axisLine={{ stroke: '#e5e7eb' }}
                                />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: 'white',
                                        border: '1px solid #e5e7eb',
                                        borderRadius: '8px',
                                        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                                    }}
                                    formatter={(value) => [`${value} points`, 'Score']}
                                />
                                <Bar dataKey="score" fill="#424874" radius={[8, 8, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            )}

            {/* Two-column layout for Competency & Distribution */}
            <div className="grid lg:grid-cols-2 gap-6">
                {/* Competency Breakdown */}
                {competencyData.length > 0 && (
                    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700/60 p-5">
                        <h3 className="font-semibold text-gray-800 dark:text-gray-100 mb-4 flex items-center gap-2">
                            <Award className="w-4 h-4" /> Competency Scores
                        </h3>
                        <div className="space-y-3">
                            {competencyData.map((item, index) => (
                                <div key={item.name}>
                                    <div className="flex items-center justify-between mb-1">
                                        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                                            {item.name}
                                        </span>
                                        <span className="text-sm font-bold text-gray-800 dark:text-gray-100">
                                            {item.value}/100
                                        </span>
                                    </div>
                                    <div className="h-2 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden">
                                        <div
                                            className="h-full rounded-full transition-all duration-300"
                                            style={{
                                                width: `${item.value}%`,
                                                backgroundColor: COLORS[index % COLORS.length]
                                            }}
                                        />
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Score Distribution */}
                {distributionData.length > 0 && (
                    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700/60 p-5">
                        <h3 className="font-semibold text-gray-800 dark:text-gray-100 mb-4">
                            Score Distribution
                        </h3>
                        <div className="h-[200px]">
                            <ResponsiveContainer width="100%" height="100%">
                                <PieChart>
                                    <Pie
                                        data={distributionData}
                                        cx="50%"
                                        cy="50%"
                                        labelLine={false}
                                        label={(entry: any) => `${entry.range}: ${entry.count}`}
                                        outerRadius={80}
                                        fill="#8884d8"
                                        dataKey="count"
                                    >
                                        {distributionData.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={entry.fill} />
                                        ))}
                                    </Pie>
                                    <Tooltip />
                                </PieChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                )}
            </div>

            {/* Recent Sessions Table */}
            {metrics.recent_sessions.length > 0 && (
                <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700/60 overflow-hidden">
                    <div className="px-5 py-4 border-b border-gray-200 dark:border-gray-700/60">
                        <h3 className="font-semibold text-gray-800 dark:text-gray-100">Recent Sessions</h3>
                    </div>
                    <div className="divide-y divide-gray-100 dark:divide-gray-700/60 max-h-[400px] overflow-y-auto">
                        {metrics.recent_sessions.slice(0, 10).map((session) => (
                            <div
                                key={session.session_id}
                                className="flex items-center gap-4 px-5 py-3 hover:bg-gray-50 dark:hover:bg-gray-700/30 transition-colors"
                            >
                                <div className="flex-1 min-w-0">
                                    <p className="font-medium text-gray-800 dark:text-gray-100 truncate">
                                        {session.job_role || "Unknown Role"}
                                    </p>
                                    <p className="text-xs text-gray-500 dark:text-gray-400">
                                        {session.created_at
                                            ? new Date(session.created_at).toLocaleDateString('en-US', {
                                                month: 'short',
                                                day: 'numeric',
                                                hour: '2-digit',
                                                minute: '2-digit'
                                            })
                                            : "N/A"}
                                        {session.stage_type && (
                                            <span className="ml-2 px-1.5 py-0.5 bg-gray-100 dark:bg-gray-700 rounded text-[10px] uppercase">
                                                {session.stage_type}
                                            </span>
                                        )}
                                    </p>
                                </div>
                                <div className={`text-lg font-bold ${getScoreColor(session.overall_score || 0)}`}>
                                    {session.overall_score || '-'}
                                </div>
                                <div className="flex gap-2">
                                    <Link
                                        href={`/interview/${session.session_id}/feedback`}
                                        className="px-3 py-1.5 text-xs text-[#424874] dark:text-[#A6B1E1] border border-[#424874]/30 dark:border-[#A6B1E1]/30 rounded hover:bg-[#424874]/5 dark:hover:bg-[#A6B1E1]/5 transition-colors"
                                    >
                                        View
                                    </Link>
                                    {session.opik_trace_id && (
                                        <a
                                            href={getOpikTraceUrl(session.opik_trace_id)}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="flex items-center gap-1 px-2 py-1.5 text-xs text-gray-500 dark:text-gray-400 border border-gray-200 dark:border-gray-600 rounded hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                                            title="View AI Trace on Opik"
                                        >
                                            <ExternalLink className="w-3 h-3" />
                                            Trace
                                        </a>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}

function getScoreColor(score: number) {
    if (score >= 80) return "text-green-600 dark:text-green-400";
    if (score >= 60) return "text-yellow-600 dark:text-yellow-400";
    return "text-red-600 dark:text-red-400";
}
