"use client";

import { Menu, ChevronDown } from "lucide-react";
import ThemeToggle from "./ThemeToggle";
import { UserButton } from "@clerk/nextjs";


interface HeaderProps {
    sidebarOpen: boolean;
    setSidebarOpen: (open: boolean) => void;
}

export default function Header({ sidebarOpen, setSidebarOpen }: HeaderProps) {

    return (
        <header className="sticky top-0 before:absolute before:inset-0 before:backdrop-blur-md before:bg-white/90 dark:before:bg-gray-900/90 before:-z-10 z-30 shadow-sm border-b border-gray-200 dark:border-gray-700/60">
            <div className="px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between h-16">
                    {/* Header: Left side */}
                    <div className="flex items-center">
                        {/* Hamburger button */}
                        <button
                            className="text-gray-500 hover:text-gray-600 dark:hover:text-gray-400 lg:hidden"
                            aria-controls="sidebar"
                            aria-expanded={sidebarOpen}
                            onClick={(e) => {
                                e.stopPropagation();
                                setSidebarOpen(!sidebarOpen);
                            }}
                        >
                            <span className="sr-only">Open sidebar</span>
                            <Menu className="w-6 h-6" />
                        </button>
                    </div>

                    {/* Header: Right side */}
                    <div className="flex items-center gap-3">

                        <ThemeToggle />
                        {/* Divider */}
                        <hr className="w-px h-6 bg-gray-200 dark:bg-gray-700/60 border-none" />
                        {/* User Menu */}
                        <UserButton
                            afterSignOutUrl="/"
                            appearance={{
                                elements: {
                                    avatarBox: "w-8 h-8"
                                }
                            }}
                        />
                    </div>
                </div>
            </div>
        </header>
    );
}
