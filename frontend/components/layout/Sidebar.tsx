"use client";

import { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
    LayoutDashboard,
    Layers,
    PlayCircle,
    ChevronLeft,
    Menu,
    Map,
    TrendingUp,
    BarChart3
} from "lucide-react";
import { useLanguage } from "@/contexts/LanguageContext";

interface SidebarProps {
    sidebarOpen: boolean;
    setSidebarOpen: (open: boolean) => void;
}

export default function Sidebar({ sidebarOpen, setSidebarOpen }: SidebarProps) {
    const pathname = usePathname();
    const { t } = useLanguage();
    const trigger = useRef<HTMLButtonElement>(null);
    const sidebar = useRef<HTMLDivElement>(null);

    const [sidebarExpanded, setSidebarExpanded] = useState(true);

    // Close on click outside
    useEffect(() => {
        const clickHandler = ({ target }: MouseEvent) => {
            if (!sidebar.current || !trigger.current) return;
            if (!sidebarOpen || sidebar.current.contains(target as Node) || trigger.current.contains(target as Node)) return;
            setSidebarOpen(false);
        };
        document.addEventListener("click", clickHandler);
        return () => document.removeEventListener("click", clickHandler);
    });

    // Close if the esc key is pressed
    useEffect(() => {
        const keyHandler = ({ keyCode }: KeyboardEvent) => {
            if (!sidebarOpen || keyCode !== 27) return;
            setSidebarOpen(false);
        };
        document.addEventListener("keydown", keyHandler);
        return () => document.removeEventListener("keydown", keyHandler);
    });

    useEffect(() => {
        if (sidebarExpanded) {
            document.querySelector("body")?.classList.add("sidebar-expanded");
        } else {
            document.querySelector("body")?.classList.remove("sidebar-expanded");
        }
    }, [sidebarExpanded]);

    const navItems = [
        { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
        { name: "Applications", href: "/applications", icon: Layers },
        { name: "Practice", href: "/practice", icon: PlayCircle },
        { name: "Progress", href: "/progress", icon: TrendingUp },
        { name: "Analytics", href: "/analytics", icon: BarChart3 },
        { name: "Career", href: "/career", icon: Map },
    ];

    return (
        <>
            {/* Sidebar backdrop (mobile only) */}
            <div
                className={`fixed inset-0 bg-gray-900/50 z-40 lg:hidden transition-opacity duration-200 ${sidebarOpen ? "opacity-100" : "opacity-0 pointer-events-none"
                    }`}
                aria-hidden="true"
                onClick={() => setSidebarOpen(false)}
            />

            {/* Sidebar */}
            <div
                id="sidebar"
                ref={sidebar}
                className={`flex lg:flex! flex-col absolute z-40 left-0 top-0 lg:static lg:left-auto lg:top-auto lg:translate-x-0 h-[100dvh] overflow-y-scroll lg:overflow-y-auto no-scrollbar w-64 lg:w-20 lg:sidebar-expanded:w-64 shrink-0 bg-white dark:bg-gray-800 p-4 transition-all duration-200 ease-in-out border-r border-gray-200 dark:border-gray-700/60 ${sidebarOpen ? "translate-x-0" : "-translate-x-64"
                    }`}
            >
                {/* Sidebar header */}
                <div className="flex justify-between mb-10 pr-3 sm:px-2">
                    {/* Logo */}
                    <Link href="/" className="block">
                        <div className="flex items-center gap-2">
                            <div className="w-8 h-8 bg-[#424874] rounded flex items-center justify-center text-white font-serif font-bold text-lg">
                                If
                            </div>
                            <span className="text-xl font-serif font-bold tracking-tight text-[#424874] dark:text-[#A6B1E1] lg:opacity-0 lg:sidebar-expanded:opacity-100 transition-opacity duration-200">
                                Opik Agent
                            </span>
                        </div>
                    </Link>
                    {/* Close button (mobile) */}
                    <button
                        ref={trigger}
                        className="lg:hidden text-gray-500 hover:text-gray-400"
                        onClick={() => setSidebarOpen(false)}
                        aria-controls="sidebar"
                        aria-expanded={sidebarOpen}
                    >
                        <span className="sr-only">Close sidebar</span>
                        <ChevronLeft className="w-6 h-6" />
                    </button>
                </div>

                {/* Links */}
                <div className="space-y-8">
                    <div>
                        <h3 className="text-xs uppercase text-gray-400 dark:text-gray-500 font-semibold pl-3 mb-3">
                            <span className="lg:hidden lg:sidebar-expanded:block">{t('common.menu')}</span>
                            <span className="lg:block lg:sidebar-expanded:hidden">•••</span>
                        </h3>
                        <ul className="space-y-1">
                            {navItems.map((item) => {
                                const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
                                const Icon = item.icon;
                                return (
                                    <li key={item.href}>
                                        <Link
                                            href={item.href}
                                            className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${isActive
                                                ? "bg-gray-50 dark:bg-gray-500/10 text-[#424874] dark:text-[#A6B1E1]"
                                                : "text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700/50"
                                                }`}
                                            onClick={() => setSidebarOpen(false)}
                                        >
                                            <Icon className="w-5 h-5 shrink-0" />
                                            <div className="flex flex-col items-start leading-tight lg:opacity-0 lg:sidebar-expanded:opacity-100 transition-opacity duration-200">
                                                <span className="text-sm font-medium">
                                                    {t(`common.${item.name.toLowerCase()}`)}
                                                </span>
                                                <span className="text-[10px] font-normal opacity-70">
                                                    {t(`common.${item.name.toLowerCase()}_sub`)}
                                                </span>
                                            </div>
                                        </Link>
                                    </li>
                                );
                            })}
                        </ul>
                    </div>
                </div>

                {/* Expand / collapse button */}
                <div className="pt-3 hidden lg:inline-flex mt-auto">
                    <div className="w-12 pl-4 pr-3 py-2">
                        <button
                            className="text-gray-400 hover:text-gray-500 dark:text-gray-500 dark:hover:text-gray-400"
                            onClick={() => setSidebarExpanded(!sidebarExpanded)}
                        >
                            <span className="sr-only">Expand / collapse sidebar</span>
                            <svg
                                className={`fill-current shrink-0 transition-transform duration-200 ${sidebarExpanded ? "rotate-180" : ""}`}
                                xmlns="http://www.w3.org/2000/svg"
                                width="16"
                                height="16"
                                viewBox="0 0 16 16"
                            >
                                <path d="M15 16a1 1 0 0 1-1-1V1a1 1 0 1 1 2 0v14a1 1 0 0 1-1 1ZM8.586 7H1a1 1 0 1 0 0 2h7.586l-2.793 2.793a1 1 0 1 0 1.414 1.414l4.5-4.5A.997.997 0 0 0 12 8a.997.997 0 0 0-.293-.707l-4.5-4.5a1 1 0 0 0-1.414 1.414L8.586 7Z" />
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
        </>
    );
}
