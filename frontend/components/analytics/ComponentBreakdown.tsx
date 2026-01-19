import { Cpu, Zap, MessageSquare, Info } from "lucide-react";

interface ComponentMetrics {
    total_sessions_analyzed: number;
    total_turns: number;
    estimated_llm_calls: number;
    components_used: string[];
    note: string;
}

interface ComponentBreakdownProps {
    metrics: ComponentMetrics;
}

const componentIcons: Record<string, React.ReactNode> = {
    scoring_engine: <Zap className="w-4 h-4" />,
    candidate_profile: <Cpu className="w-4 h-4" />,
    feedback_generation: <MessageSquare className="w-4 h-4" />,
};

const componentLabels: Record<string, string> = {
    scoring_engine: "Answer Scoring Engine",
    candidate_profile: "Candidate Profiling",
    feedback_generation: "Feedback Generation",
};

export default function ComponentBreakdown({ metrics }: ComponentBreakdownProps) {
    return (
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700/60 p-5">
            <h3 className="font-semibold text-gray-800 dark:text-gray-100 mb-4 flex items-center gap-2">
                <Cpu className="w-4 h-4" /> Component Metrics
            </h3>

            {/* Metrics Grid */}
            <div className="grid grid-cols-3 gap-4 mb-6">
                <div className="text-center p-4 bg-gray-50 dark:bg-gray-700/30 rounded-lg">
                    <p className="text-2xl font-bold text-gray-800 dark:text-gray-100">
                        {metrics.total_sessions_analyzed}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Sessions Analyzed</p>
                </div>
                <div className="text-center p-4 bg-gray-50 dark:bg-gray-700/30 rounded-lg">
                    <p className="text-2xl font-bold text-gray-800 dark:text-gray-100">
                        {metrics.total_turns}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Total Turns</p>
                </div>
                <div className="text-center p-4 bg-gray-50 dark:bg-gray-700/30 rounded-lg">
                    <p className="text-2xl font-bold text-gray-800 dark:text-gray-100">
                        ~{metrics.estimated_llm_calls}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Est. LLM Calls</p>
                </div>
            </div>

            {/* Components Used */}
            <div className="space-y-2 mb-4">
                <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                    Active Components
                </h4>
                <div className="flex flex-wrap gap-2">
                    {metrics.components_used.map((component) => (
                        <div
                            key={component}
                            className="flex items-center gap-2 px-3 py-2 bg-[#DCD6F7] dark:bg-[#424874]/20 text-[#424874] dark:text-[#A6B1E1] rounded-lg text-sm font-medium"
                        >
                            {componentIcons[component] || <Cpu className="w-4 h-4" />}
                            {componentLabels[component] || component}
                        </div>
                    ))}
                </div>
            </div>

            {/* Note */}
            <div className="flex items-start gap-2 p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
                <Info className="w-4 h-4 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" />
                <p className="text-sm text-blue-700 dark:text-blue-300">
                    {metrics.note}
                </p>
            </div>
        </div>
    );
}
