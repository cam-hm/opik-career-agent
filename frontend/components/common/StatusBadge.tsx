import { CheckCircle, XCircle, Clock } from "lucide-react";

interface StatusBadgeProps {
    status: string;
    t: (key: string) => string;
}

export function StatusBadge({ status, t }: StatusBadgeProps) {
    if (status === "completed") {
        return (
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-[#DCD6F7] dark:bg-[#424874]/20 text-green-700 dark:text-[#A6B1E1]">
                <CheckCircle className="w-3 h-3" /> {t('status.done')}
            </span>
        );
    }
    if (status === "failed") {
        return (
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 dark:bg-red-500/20 text-red-700 dark:text-red-400">
                <XCircle className="w-3 h-3" /> Failed
            </span>
        );
    }
    return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-yellow-100 dark:bg-yellow-500/20 text-yellow-700 dark:text-yellow-400">
            <Clock className="w-3 h-3" /> {t(`status.${status}`) || status}
        </span>
    );
}
