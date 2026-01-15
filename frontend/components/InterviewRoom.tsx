"use client"

import { LiveKitRoom, RoomAudioRenderer, ControlBar, useTracks, VideoTrack, GridLayout, ParticipantTile, useTrackTranscription, useRoomContext, DisconnectButton, TrackToggle, useRemoteParticipants, useConnectionState, TrackReferenceOrPlaceholder } from "@livekit/components-react"
import { Track, ConnectionState } from "livekit-client"
import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@clerk/nextjs"
import { Loader2, LogOut, Mic, Camera, X, Bot, AlertCircle, CheckCircle } from "lucide-react"
import "@livekit/components-styles"
import PreJoinScreen from "./PreJoinScreen"
import { useLanguage } from "@/contexts/LanguageContext";
import { ENDPOINTS } from "@/lib/endpoints";
import { fetchWithAuth } from "@/lib/api";

export default function InterviewRoom({ sessionId }: { sessionId: string }) {
    const { fetchWithAuth } = { fetchWithAuth: require('@/lib/api').fetchWithAuth }; // Dynamic import to avoid circular dependency issues if any, or just standard import above
    // Actually better to use standard import:
    // This file seems to use direct fetch currently. We should replace it with fetchWithAuth.
    // Wait, the original code uses direct fetch at line 32 and 40. I should add the import at the top.
    const { t } = useLanguage();
    const router = useRouter()
    const { getToken } = useAuth()
    const [token, setToken] = useState("")
    const [isJoined, setIsJoined] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const [mediaEnabled, setMediaEnabled] = useState(true)
    const [sessionDetails, setSessionDetails] = useState<{ stage_type?: string, job_role?: string } | null>(null)

    useEffect(() => {
        (async () => {
            try {
                // Use environment variable for API URL, fallback to localhost for dev
                // Fetch Token
                const resp = await fetchWithAuth(`${ENDPOINTS.INTERVIEW.TOKEN(sessionId)}?participant_name=Candidate`, {
                    method: 'POST'
                }, getToken)
                const data = await resp.json()
                setToken(data.token)

                // Fetch Session Details
                const detailsResp = await fetchWithAuth(ENDPOINTS.INTERVIEW.DETAIL(sessionId), {}, getToken)
                if (detailsResp.ok) {
                    const details = await detailsResp.json()
                    setSessionDetails(details)
                }

            } catch (e) {
                console.error(e)
            }
        })()
    }, [sessionId, getToken])

    const handleJoin = async () => {
        try {
            // Only require audio (mic), camera is optional
            await navigator.mediaDevices.getUserMedia({ audio: true });

            // Try to get video too, but don't fail if not available
            try {
                await navigator.mediaDevices.getUserMedia({ video: true });
                setMediaEnabled(true);
            } catch (videoError) {
                console.warn("Camera not available, continuing with audio only", videoError);
                setMediaEnabled(true); // Still enable media for audio
            }

            setIsJoined(true);
        } catch (e) {
            console.error(e);
            setError(t('interview.cameraError'));
        }
    }

    const handleJoinWithoutDevices = () => {
        setMediaEnabled(false);
        setIsJoined(true);
    }

    if (!token) {
        return (
            <div className="flex items-center justify-center h-full bg-gray-900 text-white">
                <Loader2 className="h-8 w-8 animate-spin text-white" />
                <span className="ml-2">{t('interview.preparing')}</span>
            </div>
        )
    }

    if (!isJoined) {
        return (
            <PreJoinScreen
                jobRole={sessionDetails?.job_role}
                stageType={sessionDetails?.stage_type}
                onJoin={handleJoin}
                onJoinWithoutDevices={handleJoinWithoutDevices}
            />
        )
    }

    return (
        <LiveKitRoom
            video={mediaEnabled}
            audio={mediaEnabled}
            token={token}
            connect={true}
            serverUrl={process.env.NEXT_PUBLIC_LIVEKIT_URL || "ws://localhost:7880"}
            data-lk-theme="default"
            style={{ height: '100%' }}
            className="bg-gray-900"
            onError={(e) => console.error("LiveKit Error:", e)}
            onDisconnected={() => {
                router.push(`/interview/${sessionId}/feedback`)
            }}
        >
            <MyVideoConference />
            <RoomAudioRenderer />
            <AgentStatusIndicator />
            <TranscriptionTile />

            {/* Stage Context Badge */}
            {sessionDetails && (
                <div className="absolute top-4 left-4 z-50 bg-black/50 backdrop-blur-md text-white px-4 py-2 rounded-lg border border-white/10">
                    <p className="text-xs text-slate-400 font-bold uppercase tracking-wider">{t('interview.currentStage')}</p>
                    <p className="font-bold text-[#ffde59] capitalize">{sessionDetails.stage_type || "General"} Interview</p>
                </div>
            )}

            <div className="lk-control-bar" style={{ display: 'flex', gap: '12px', padding: '1rem', justifyContent: 'center', position: 'absolute', bottom: '20px', left: '0', right: '0', zIndex: 50 }}>
                <TrackToggle source={Track.Source.Microphone} showIcon={true} />
                <TrackToggle source={Track.Source.Camera} showIcon={true} />
                <DisconnectButton>
                    <span className="flex items-center gap-2 font-bold">
                        <LogOut className="h-4 w-4" /> {t('interview.finish')}
                    </span>
                </DisconnectButton>
            </div>
        </LiveKitRoom>
    )
}

function MyVideoConference() {
    const tracks = useTracks(
        [
            { source: Track.Source.Camera, withPlaceholder: true },
            { source: Track.Source.ScreenShare, withPlaceholder: false },
        ],
        { onlySubscribed: false },
    );
    return (
        <GridLayout tracks={tracks} style={{ height: 'calc(100% - 80px)' }}>
            <ParticipantTile />
        </GridLayout>
    );
}

function TranscriptionTile() {
    const tracks = useTracks([Track.Source.Microphone]);

    return (
        <div className="absolute bottom-24 left-0 right-0 flex flex-col items-center pointer-events-none z-40 space-y-2">
            {tracks.map((track) => (
                <TrackTranscription key={track.publication.trackSid} trackRef={track} />
            ))}
        </div>
    );
}

function TrackTranscription({ trackRef }: { trackRef: TrackReferenceOrPlaceholder }) {
    const { segments } = useTrackTranscription(trackRef);

    if (!segments || segments.length === 0) return null;

    const lastSegment = segments[segments.length - 1];

    return (
        <div className="bg-black/70 text-white px-6 py-3 rounded-full text-lg max-w-3xl text-center backdrop-blur-sm transition-all duration-300">
            {lastSegment.text}
        </div>
    )
}

function AgentStatusIndicator() {
    const { t } = useLanguage();
    const remoteParticipants = useRemoteParticipants();
    const connectionState = useConnectionState();
    const [waitTime, setWaitTime] = useState(0);

    // Check if agent is connected (agent identity typically contains "agent")
    const agentParticipant = remoteParticipants.find(p =>
        p.identity.toLowerCase().includes('agent') ||
        p.name?.toLowerCase().includes('agent') ||
        p.identity.startsWith('livekit-agent')
    );
    const isAgentConnected = !!agentParticipant;

    // Track wait time
    useEffect(() => {
        if (connectionState === ConnectionState.Connected && !isAgentConnected) {
            const interval = setInterval(() => {
                setWaitTime(prev => prev + 1);
            }, 1000);
            return () => clearInterval(interval);
        } else {
            setWaitTime(0);
        }
    }, [connectionState, isAgentConnected]);

    // Don't show if still connecting
    if (connectionState !== ConnectionState.Connected) {
        return null;
    }

    return (
        <div className="absolute top-4 right-4 z-50">
            {isAgentConnected ? (
                <div className="flex items-center gap-2 bg-green-500/80 backdrop-blur-md text-white px-4 py-2 rounded-lg shadow-lg">
                    <CheckCircle className="w-4 h-4" />
                    <span className="text-sm font-medium">{t('interview.agentConnected')}</span>
                </div>
            ) : (
                <div className="flex flex-col gap-2">
                    <div className="flex items-center gap-2 bg-yellow-500/80 backdrop-blur-md text-white px-4 py-2 rounded-lg shadow-lg">
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <span className="text-sm font-medium">{t('interview.agentWaiting')}</span>
                    </div>
                    {waitTime > 10 && (
                        <div className="flex items-center gap-2 bg-red-500/80 backdrop-blur-md text-white px-4 py-2 rounded-lg shadow-lg">
                            <AlertCircle className="w-4 h-4" />
                            <span className="text-sm font-medium">
                                {t('interview.agentIssue')} ({waitTime}s)
                            </span>
                        </div>
                    )}
                    {waitTime > 5 && (
                        <p className="text-xs text-white/70 bg-black/40 backdrop-blur px-3 py-1 rounded text-center">
                            {t('interview.checkLogs')}: <code className="text-yellow-300">docker logs interviewer-worker</code>
                        </p>
                    )}
                </div>
            )}
        </div>
    );
}
