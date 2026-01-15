/**
 * Design Tokens - Interfinity AI
 * 
 * Color Palette from ColorHunt: #F4EEFF, #DCD6F7, #A6B1E1, #424874
 * Purple/Lavender theme - Soft and professional
 */

// =============================================================================
// COLORS - Purple/Lavender Theme
// =============================================================================

export const colors = {
    // Primary (Navy - darkest, for buttons and emphasis)
    primary: {
        50: "#F4EEFF",   // Lightest lavender
        100: "#DCD6F7",  // Light lavender
        200: "#C4BDE8",
        300: "#A6B1E1",  // Medium blue-purple
        400: "#7A82C7",
        500: "#5C64AD",
        600: "#424874",  // Main navy from palette - PRIMARY
        700: "#363B5E",
        800: "#2A2E48",
        900: "#1E2132",
    },

    // Lavender (Soft backgrounds)
    lavender: {
        50: "#F4EEFF",   // Lightest - page bg
        100: "#EDE7FA",
        200: "#DCD6F7",  // Light - cards/accents
        300: "#C8C1E8",
        400: "#A6B1E1",  // Medium - icon bg
    },

    // Gray (Neutral - for text and borders)
    gray: {
        50: "#f9fafb",
        100: "#f3f4f6",
        200: "#e5e7eb",
        300: "#d1d5db",
        400: "#9ca3af",
        500: "#6b7280",
        600: "#4b5563",
        700: "#374151",
        800: "#1f2937",
        900: "#111827",
        950: "#0d1117",
    },

    // Semantic Colors (keep standard for clarity)
    success: {
        light: "#dcffe4",
        DEFAULT: "#22c55e",
        dark: "#16a34a",
    },
    warning: {
        light: "#fef3c7",
        DEFAULT: "#f59e0b",
        dark: "#d97706",
    },
    error: {
        light: "#fee2e2",
        DEFAULT: "#ef4444",
        dark: "#dc2626",
    },
    info: {
        light: "#DCD6F7",
        DEFAULT: "#A6B1E1",
        dark: "#424874",
    },
} as const;

// =============================================================================
// COMPONENT STYLES - Purple/Lavender Theme
// =============================================================================

export const styles = {
    // Cards - White with subtle borders
    card: {
        base: "bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700/60",
        hover: "hover:border-[#A6B1E1] dark:hover:border-[#A6B1E1]/50 transition-colors cursor-pointer",
        interactive: "bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700/60 hover:border-[#A6B1E1] dark:hover:border-[#A6B1E1]/50 transition-colors cursor-pointer",
    },


    // Buttons - Navy primary (high contrast on white)
    button: {
        primary: "bg-[#424874] hover:bg-[#363B5E] text-white font-medium rounded-md transition-colors cursor-pointer",
        secondary: "bg-[#DCD6F7] hover:bg-[#C8C1E8] text-[#424874] font-medium rounded-md transition-colors cursor-pointer",
        ghost: "hover:bg-[#F4EEFF] dark:hover:bg-gray-700/50 text-gray-600 dark:text-gray-400 rounded-md transition-colors cursor-pointer",
        danger: "bg-red-500 hover:bg-red-600 text-white font-medium rounded-md transition-colors cursor-pointer",
        link: "text-[#424874] hover:text-[#363B5E] dark:text-[#A6B1E1] dark:hover:text-[#DCD6F7] hover:underline cursor-pointer",
    },


    // Inputs
    input: {
        base: "w-full bg-white dark:bg-gray-900 text-gray-800 dark:text-gray-100 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-2 focus:ring-[#A6B1E1] focus:border-[#424874] outline-none transition-all",
    },

    // Text - Good contrast
    text: {
        heading: "text-gray-900 dark:text-white",
        body: "text-gray-700 dark:text-gray-200",
        muted: "text-gray-500 dark:text-gray-400",
        link: "text-[#424874] hover:text-[#363B5E] dark:text-[#A6B1E1] dark:hover:text-[#DCD6F7] hover:underline",
    },

    // Badges - Status colors
    badge: {
        success: "inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 dark:bg-green-500/20 text-green-700 dark:text-green-400",
        warning: "inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-yellow-100 dark:bg-yellow-500/20 text-yellow-700 dark:text-yellow-400",
        error: "inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 dark:bg-red-500/20 text-red-700 dark:text-red-400",
        info: "inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-[#DCD6F7] dark:bg-[#424874]/30 text-[#424874] dark:text-[#DCD6F7]",
        neutral: "inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300",
    },

    // Icons with background - Using medium purple
    iconBox: {
        default: "w-10 h-10 rounded-lg bg-[#DCD6F7] dark:bg-[#424874]/40 flex items-center justify-center",
        sm: "w-8 h-8 rounded-lg bg-[#DCD6F7] dark:bg-[#424874]/40 flex items-center justify-center",
        primary: "w-10 h-10 rounded-lg bg-[#A6B1E1]/40 dark:bg-[#424874]/40 flex items-center justify-center",
        success: "w-10 h-10 rounded-lg bg-green-100 dark:bg-green-500/20 flex items-center justify-center",
        warning: "w-10 h-10 rounded-lg bg-yellow-100 dark:bg-yellow-500/20 flex items-center justify-center",
        error: "w-10 h-10 rounded-lg bg-red-100 dark:bg-red-500/20 flex items-center justify-center",
    },

    // Icon colors - Navy for visibility
    icon: {
        default: "text-[#424874] dark:text-[#A6B1E1]",
        muted: "text-gray-400 dark:text-gray-500",
        primary: "text-[#424874] dark:text-[#DCD6F7]",
        success: "text-green-600 dark:text-green-400",
        warning: "text-yellow-600 dark:text-yellow-400",
        error: "text-red-600 dark:text-red-400",
    },

    // Page sections
    section: {
        header: "px-5 py-4 border-b border-gray-200 dark:border-gray-700/60",
        content: "p-5",
    },

    // Tables
    table: {
        header: "text-xs font-semibold uppercase text-gray-500 dark:text-gray-400 bg-gray-50 dark:bg-gray-900/50 border-b border-gray-200 dark:border-gray-700/60",
        row: "hover:bg-[#F4EEFF] dark:hover:bg-[#424874]/20 transition-colors",
        cell: "px-4 py-3",
    },

    // Modals
    modal: {
        backdrop: "fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm",
        content: "relative w-full bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700/60",
        header: "sticky top-0 z-10 flex items-center justify-between px-5 py-4 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700/60",
        footer: "px-5 py-4 border-t border-gray-200 dark:border-gray-700/60",
    },

    // List items
    listItem: {
        base: "flex items-center gap-4 px-5 py-3 hover:bg-[#F4EEFF] dark:hover:bg-[#424874]/20 transition-colors",
        interactive: "flex items-center gap-4 px-5 py-3 hover:bg-[#F4EEFF] dark:hover:bg-[#424874]/20 transition-colors cursor-pointer group",
    },
} as const;

// =============================================================================
// HELPER FUNCTIONS
// =============================================================================

export function getScoreColor(score: number): string {
    if (score >= 80) return "text-green-600 dark:text-green-400";
    if (score >= 60) return "text-yellow-600 dark:text-yellow-400";
    return "text-red-600 dark:text-red-400";
}

export function getScoreBg(score: number): string {
    if (score >= 80) return "bg-green-100 dark:bg-green-500/20";
    if (score >= 60) return "bg-yellow-100 dark:bg-yellow-500/20";
    return "bg-red-100 dark:bg-red-500/20";
}

export function getStatusStyle(status: string): string {
    switch (status.toLowerCase()) {
        case "completed":
        case "done":
        case "success":
            return styles.badge.success;
        case "failed":
        case "error":
            return styles.badge.error;
        case "in_progress":
        case "pending":
        case "active":
            return styles.badge.warning;
        default:
            return styles.badge.neutral;
    }
}

// =============================================================================
// SIZING
// =============================================================================

export const sizing = {
    button: {
        sm: "h-8 px-3 text-sm",
        md: "h-10 px-4 text-sm",
        lg: "h-12 px-6 text-base",
    },
    input: {
        sm: "h-9 px-3 text-sm",
        md: "h-11 px-3 text-sm",
        lg: "h-12 px-4 text-base",
    },
    icon: {
        sm: "w-4 h-4",
        md: "w-5 h-5",
        lg: "w-6 h-6",
    },
} as const;
