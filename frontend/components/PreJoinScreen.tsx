"use client";

import { useEffect, useRef, useState } from "react";
import { Mic, MicOff, Video, VideoOff, Loader2, CheckCircle, AlertCircle, ArrowRight } from "lucide-react";
import { useLanguage } from "@/contexts/LanguageContext";

interface PreJoinScreenProps {
    jobRole?: string;
    stageType?: string;
    onJoin: () => void;
    onJoinWithoutDevices: () => void;
}

export default function PreJoinScreen({ jobRole, stageType, onJoin, onJoinWithoutDevices }: PreJoinScreenProps) {
    const { t } = useLanguage();
    const videoRef = useRef<HTMLVideoElement>(null);
    const [hasMicPermission, setHasMicPermission] = useState<boolean | null>(null);
    const [hasCameraPermission, setHasCameraPermission] = useState<boolean | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        let stream: MediaStream | null = null;

        const checkPermissions = async () => {
            // Check microphone first (REQUIRED)
            try {
                const audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
                setHasMicPermission(true);
                audioStream.getTracks().forEach(track => track.stop());
            } catch (err) {
                console.error("Microphone permission denied", err);
                setHasMicPermission(false);
                setError(t('preJoin.micRequired'));
                setIsLoading(false);
                return; // Stop if no mic
            }

            // Check camera (OPTIONAL)
            try {
                stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
                if (videoRef.current) {
                    videoRef.current.srcObject = stream;
                }
                setHasCameraPermission(true);
            } catch (err) {
                console.warn("Camera permission denied, continuing with audio only", err);
                setHasCameraPermission(false);
                // Try to get audio-only stream for the session
                try {
                    stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                } catch (audioErr) {
                    console.error("Audio fallback failed", audioErr);
                }
            }

            setError(null);
            setIsLoading(false);
        };

        checkPermissions();

        return () => {
            if (stream) {
                stream.getTracks().forEach(track => track.stop());
            }
        };
    }, [t]);

    return (
        <div className="h-full bg-gray-900 flex items-center justify-center p-4 overflow-y-auto">
            <div className="w-full max-w-5xl grid md:grid-cols-2 gap-8">

                {/* Left: Camera Preview */}
                <div className="space-y-6">
                    <div className="relative aspect-video bg-gray-950 rounded-2xl border border-gray-700/60 overflow-hidden shadow-2xl">
                        {isLoading ? (
                            <div className="absolute inset-0 flex items-center justify-center text-gray-400">
                                <Loader2 className="h-8 w-8 animate-spin mr-2 text-[#424874]" />
                                <span>{t('preJoin.settingUp')}</span>
                            </div>
                        ) : hasCameraPermission ? (
                            <video
                                ref={videoRef}
                                autoPlay
                                playsInline
                                muted
                                className="w-full h-full object-cover transform scale-x-[-1]"
                            />
                        ) : hasMicPermission ? (
                            <div className="absolute inset-0 flex flex-col items-center justify-center text-gray-400 p-6 text-center bg-gray-950">
                                <Mic className="h-16 w-16 mb-4 text-green-500 animate-pulse" />
                                <p className="font-medium text-white">{t('preJoin.audioOnly')}</p>
                                <p className="text-sm mt-2 text-gray-500">{t('preJoin.cameraOptional')}</p>
                            </div>
                        ) : (
                            <div className="absolute inset-0 flex flex-col items-center justify-center text-gray-400 p-6 text-center">
                                <VideoOff className="h-12 w-12 mb-4 text-red-500" />
                                <p className="font-medium text-white">{t('preJoin.cameraBlocked')}</p>
                                <p className="text-sm mt-2">{t('preJoin.enablePerms')}</p>
                            </div>
                        )}

                        {/* Status Badge */}
                        <div className="absolute bottom-4 left-4 flex items-center gap-2">
                            {hasMicPermission ? (
                                <span className="bg-green-500/20 text-green-400 px-3 py-1 rounded-full text-xs font-medium flex items-center border border-green-500/50">
                                    <Mic className="h-3 w-3 mr-1" /> {t('preJoin.micReady')}
                                </span>
                            ) : (
                                <span className="bg-red-500/20 text-red-400 px-3 py-1 rounded-full text-xs font-medium flex items-center border border-red-500/50">
                                    <MicOff className="h-3 w-3 mr-1" /> {t('preJoin.micRequired')}
                                </span>
                            )}
                            {hasCameraPermission && (
                                <span className="bg-green-500/20 text-green-400 px-3 py-1 rounded-full text-xs font-medium flex items-center border border-green-500/50">
                                    <Video className="h-3 w-3 mr-1" /> {t('preJoin.cameraReady')}
                                </span>
                            )}
                        </div>
                    </div>

                    <div className="text-center">
                        <p className="text-gray-500 text-sm">
                            {t('preJoin.checkLighting')}
                        </p>
                    </div>
                </div>

                {/* Right: Context & Actions */}
                <div className="flex flex-col justify-center space-y-8">
                    <div>
                        <h1 className="text-3xl md:text-4xl font-serif font-bold text-white mb-2">{t('preJoin.readyToJoin')}</h1>
                        <p className="text-gray-400 text-lg">{t('preJoin.enterRoom')}</p>
                    </div>

                    <div className="bg-gray-800 border border-gray-700/60 p-6 rounded-xl">
                        <div className="space-y-4">
                            <div>
                                <p className="text-xs font-mono font-medium text-gray-500 uppercase tracking-wider mb-1">{t('preJoin.role')}</p>
                                <p className="text-xl font-semibold text-white">{jobRole || "Agent"}</p>
                            </div>
                            <div className="h-px bg-gray-700" />
                            <div>
                                <p className="text-xs font-mono font-medium text-gray-500 uppercase tracking-wider mb-1">{t('preJoin.stage')}</p>
                                <p className="text-xl font-semibold text-green-400 capitalize">{stageType || "General"} Engagement</p>
                            </div>
                            <div className="h-px bg-gray-700" />
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <p className="text-xs font-mono font-medium text-gray-500 uppercase tracking-wider mb-1">{t('preJoin.duration')}</p>
                                    <p className="text-white font-medium">~15 Minutes</p>
                                </div>
                                <div>
                                    <p className="text-xs font-mono font-medium text-gray-500 uppercase tracking-wider mb-1">{t('preJoin.questions')}</p>
                                    <p className="text-white font-medium">3-5 Scenarios</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    <button
                        onClick={onJoin}
                        disabled={!hasMicPermission}
                        className="w-full bg-[#424874] hover:bg-[#363B5E] text-white text-lg h-14 font-medium rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                    >
                        {hasMicPermission ? (
                            <>{t('preJoin.joinButton')} <ArrowRight className="w-5 h-5" /></>
                        ) : (
                            <>{t('preJoin.enableMic')} <MicOff className="w-5 h-5" /></>
                        )}
                    </button>

                    {!hasMicPermission && !isLoading && (
                        <p className="text-center text-red-400 text-sm">
                            {t('preJoin.micRequiredMessage')}
                        </p>
                    )}
                </div>
            </div>
        </div>
    );
}
