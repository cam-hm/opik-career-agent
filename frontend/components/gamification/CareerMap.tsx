"use client";

import { motion } from 'framer-motion';
import { CareerNode, UserNodeStatus } from '@/lib/api/gamification';
import { useRef, useEffect, useState } from 'react';
import { useLanguage } from '@/contexts/LanguageContext';

interface CareerMapProps {
    nodes: CareerNode[];
    userNodes: Record<string, UserNodeStatus>;
    onNodeClick?: (nodeId: string, status: string) => void;
    className?: string;
}

interface LayoutNode extends CareerNode {
    computedX: number;
    computedY: number;
}

// Duolingo-style snake path layout algorithm
function computeSnakePath(nodes: CareerNode[]): LayoutNode[] {
    // Sort by order, fallback to position.y if order not available
    const sorted = [...nodes].sort((a, b) => {
        if (a.order !== undefined && b.order !== undefined) {
            return a.order - b.order;
        }
        return (a.position?.y || 0) - (b.position?.y || 0);
    });

    // X positions for zigzag pattern
    const xPositions = [50, 30, 50, 70]; // Left-center-right pattern

    const ROW_HEIGHT = 130;
    const START_Y = 60;

    return sorted.map((node, index) => {
        const xIndex = index % xPositions.length;
        return {
            ...node,
            computedX: xPositions[xIndex],
            computedY: START_Y + (index * ROW_HEIGHT),
        };
    });
}

// Get icon based on node type
function getNodeIcon(node: CareerNode, isCompleted: boolean): string {
    if (node.icon) return node.icon;
    if (isCompleted) return '✓';

    switch (node.type) {
        case 'milestone': return '🎯';
        case 'interview': return '💬';
        case 'interview_gate': return '🚀';
        case 'challenge': return '⚔️';
        case 'side_quest': return '🧩';
        case 'boss_fight': return '👹';
        case 'offer': return '🎉';
        default: return '📍';
    }
}

export function CareerMap({ nodes, userNodes, onNodeClick, className }: CareerMapProps) {
    const { getLocalized } = useLanguage();
    const containerRef = useRef<HTMLDivElement>(null);
    const [containerWidth, setContainerWidth] = useState(600);

    useEffect(() => {
        if (containerRef.current) {
            setContainerWidth(containerRef.current.offsetWidth);
        }
        const handleResize = () => {
            if (containerRef.current) {
                setContainerWidth(containerRef.current.offsetWidth);
            }
        };
        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }, []);

    const layoutNodes = computeSnakePath(nodes);

    const handleNodeClick = (nodeId: string, status: string) => {
        if (onNodeClick && status !== 'locked') {
            onNodeClick(nodeId, status);
        }
    };

    const totalHeight = Math.max(...layoutNodes.map(n => n.computedY), 400) + 180;

    // Calculate actual pixel positions for SVG
    const getPixelX = (percent: number) => (percent / 100) * containerWidth;

    return (
        <div
            ref={containerRef}
            className={`relative w-full overflow-y-auto overflow-x-hidden rounded-xl border border-border bg-gradient-to-b from-background via-card to-muted/20 ${className}`}
            style={{ height: `${Math.min(totalHeight, 700)}px` }}
        >
            {/* Content container with padding */}
            <div className="relative" style={{ height: `${totalHeight}px`, minHeight: '100%' }}>

                {/* SVG Connections - Now using correct pixel calculations */}
                <svg
                    className="absolute inset-0 w-full pointer-events-none"
                    style={{ height: `${totalHeight}px` }}
                    preserveAspectRatio="none"
                >
                    <defs>
                        <linearGradient id="pathGradientActive" x1="0%" y1="0%" x2="0%" y2="100%">
                            <stop offset="0%" stopColor="#22c55e" stopOpacity="0.8" />
                            <stop offset="100%" stopColor="#22c55e" stopOpacity="0.3" />
                        </linearGradient>
                        <linearGradient id="pathGradientLocked" x1="0%" y1="0%" x2="0%" y2="100%">
                            <stop offset="0%" stopColor="#9ca3af" stopOpacity="0.4" />
                            <stop offset="100%" stopColor="#9ca3af" stopOpacity="0.1" />
                        </linearGradient>
                    </defs>

                    {layoutNodes.map((node, index) => {
                        if (index === 0) return null;
                        const prev = layoutNodes[index - 1];

                        const x1 = getPixelX(prev.computedX);
                        const y1 = prev.computedY + 35; // bottom of node
                        const x2 = getPixelX(node.computedX);
                        const y2 = node.computedY - 5; // top of node

                        const midY = (y1 + y2) / 2;
                        const pathD = `M ${x1} ${y1} C ${x1} ${midY}, ${x2} ${midY}, ${x2} ${y2}`;

                        const nodeStatus = userNodes[node.id]?.status || 'locked';
                        const isActive = nodeStatus !== 'locked';

                        return (
                            <g key={`conn-${node.id}`}>
                                {/* Background glow for active paths */}
                                {isActive && (
                                    <path
                                        d={pathD}
                                        fill="none"
                                        stroke="url(#pathGradientActive)"
                                        strokeWidth="8"
                                        strokeLinecap="round"
                                        opacity="0.4"
                                    />
                                )}
                                {/* Main path */}
                                <path
                                    d={pathD}
                                    fill="none"
                                    stroke={isActive ? "#22c55e" : "#d1d5db"}
                                    strokeWidth="3"
                                    strokeLinecap="round"
                                    strokeDasharray={isActive ? "0" : "6 4"}
                                    className={isActive ? "" : "opacity-50"}
                                />
                            </g>
                        );
                    })}
                </svg>

                {/* Nodes */}
                {layoutNodes.map((node, index) => {
                    const nodeStatus = userNodes[node.id]?.status || (index === 0 ? 'unlocked' : 'locked');
                    const isCompleted = nodeStatus === 'completed';
                    const isUnlocked = nodeStatus === 'unlocked' || isCompleted;
                    const isCurrent = nodeStatus === 'unlocked';
                    const isBoss = node.type === 'boss_fight';
                    const isOffer = node.type === 'offer';
                    const isGate = node.type === 'interview_gate';

                    // Node size
                    const size = isBoss || isGate ? 72 : isOffer ? 64 : 56;

                    // Colors based on state
                    let bgColor = 'bg-gray-200 dark:bg-gray-700';
                    let borderColor = 'border-gray-300 dark:border-gray-600';
                    let textColor = 'text-gray-500';

                    if (isCompleted) {
                        bgColor = 'bg-gradient-to-br from-green-400 to-green-600';
                        borderColor = 'border-green-300';
                        textColor = 'text-white';
                    } else if (isCurrent) {
                        bgColor = 'bg-gradient-to-br from-indigo-400 to-indigo-600';
                        borderColor = 'border-indigo-300';
                        textColor = 'text-white';
                    } else if (isBoss && isUnlocked) {
                        bgColor = 'bg-gradient-to-br from-red-400 to-red-600';
                        borderColor = 'border-red-300';
                        textColor = 'text-white';
                    }

                    return (
                        <motion.div
                            key={node.id}
                            className="absolute flex flex-col items-center"
                            style={{
                                left: `${node.computedX}%`,
                                top: node.computedY,
                                transform: 'translate(-50%, 0)',
                                zIndex: isCurrent ? 20 : 10,
                            }}
                            initial={{ opacity: 0, scale: 0.5 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ delay: index * 0.05, type: 'spring', stiffness: 200 }}
                        >
                            {/* Pulse ring for current node */}
                            {isCurrent && (
                                <div
                                    className="absolute rounded-full animate-ping"
                                    style={{
                                        width: size + 16,
                                        height: size + 16,
                                        top: -8,
                                        left: '50%',
                                        transform: 'translateX(-50%)',
                                        backgroundColor: 'rgba(99, 102, 241, 0.3)',
                                    }}
                                />
                            )}

                            {/* Node Button */}
                            <motion.button
                                className={`
                                    relative rounded-full flex items-center justify-center
                                    border-4 ${borderColor} ${bgColor} ${textColor}
                                    shadow-lg transition-all duration-200
                                    ${!isUnlocked ? 'opacity-50 grayscale cursor-not-allowed' : 'cursor-pointer hover:scale-110'}
                                    ${isCurrent ? 'ring-4 ring-indigo-200 dark:ring-indigo-800' : ''}
                                `}
                                style={{
                                    width: size,
                                    height: size,
                                    boxShadow: isUnlocked
                                        ? '0 4px 14px rgba(0,0,0,0.15), inset 0 2px 0 rgba(255,255,255,0.2)'
                                        : '0 2px 4px rgba(0,0,0,0.1)'
                                }}
                                whileHover={isUnlocked ? { scale: 1.15, y: -2 } : {}}
                                whileTap={isUnlocked ? { scale: 0.95 } : {}}
                                onClick={() => handleNodeClick(node.id, nodeStatus)}
                            >
                                <span className={`${isBoss ? 'text-2xl' : 'text-xl'} drop-shadow`}>
                                    {getNodeIcon(node, isCompleted)}
                                </span>
                            </motion.button>

                            {/* Label */}
                            <div className={`mt-2 text-center max-w-[120px] ${!isUnlocked ? 'opacity-40' : ''}`}>
                                <div className="text-xs font-medium leading-tight">
                                    {getLocalized(node.title)}
                                </div >
                                {/* Score badge for completed */}
                                {
                                    isCompleted && userNodes[node.id]?.high_score !== undefined && (
                                        <div className="mt-1 inline-flex items-center gap-1 text-[10px] bg-green-100 text-green-700 px-1.5 py-0.5 rounded-full">
                                            ★ {userNodes[node.id].high_score}
                                        </div>
                                    )
                                }
                            </div >
                        </motion.div >
                    );
                })}
            </div >
        </div >
    );
}
