"use client";

import { useState, useRef } from "react";
import { Loader2, Play, Volume2, Globe } from "lucide-react";
import { apiRequest } from "@/lib/api";
import { ENDPOINTS } from "@/lib/endpoints";

export default function TTSDebugPage() {
    const [text, setText] = useState("Hello, this is a test of Cartesia Text to Speech.");
    const [voice, setVoice] = useState("e07c00bc-4134-4eae-9ea4-1a55fb45746b");
    const [language, setLanguage] = useState("en");
    const [modelId, setModelId] = useState("");
    const [gender, setGender] = useState("female");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [audioUrl, setAudioUrl] = useState<string | null>(null);
    const audioRef = useRef<HTMLAudioElement>(null);



    const languages = [
        { code: "en", name: "English" },
        { code: "vi", name: "Vietnamese" },
        { code: "es", name: "Spanish" },
        { code: "fr", name: "French" },
        { code: "de", name: "German" },
        { code: "ja", name: "Japanese" },
        { code: "zh", name: "Chinese" },
    ];

    const models = [
        { id: "", name: "Auto (Default)" },
        { id: "sonic-english", name: "Sonic English" },
        { id: "sonic-multilingual", name: "Sonic Multilingual" },
        { id: "sonic-3", name: "Sonic 3.0 (Experimental)" },
    ];

    const voices = [
        // Cartesia English Voices - using actual UUIDs
        { name: "e07c00bc-4134-4eae-9ea4-1a55fb45746b", label: "Brooke - Big Sister ⭐", gender: "female" },
        // Vietnamese Voices (Sonic 3.0)
        { name: "935a9060-373c-49e4-b078-f4ea6326987a", label: "Linh - Vietnamese Female ⭐", gender: "female" },
        { name: "0e58d60a-2f1a-4252-81bd-3db6af45fb41", label: "Minh - Vietnamese Male ⭐", gender: "male" },
        // ... keep existing voices ...
        // ... (rest of voices)
        // Add Multilingual Voices if known
        { name: "694f9389-1262-4977-96fa-f12bbc891632", label: "Sarah - Multilingual ⭐", gender: "female" },
        { name: "f786b574-daa5-4673-aa0c-cbe3e8534c02", label: "Katie - Friendly Fixer", gender: "female" },
        { name: "9626c31c-bec5-4cca-baa8-f8ba9e84c8bc", label: "Jacqueline - Reassuring Agent", gender: "female" },
        { name: "a167e0f3-df7e-4d52-a9c3-f949145efdab", label: "Blake - Helpful Agent ⭐", gender: "male" },
        { name: "5ee9feff-1265-424a-9d7f-8e4d431a12c7", label: "Ronald - Thinker", gender: "male" },
        { name: "79f8b5fb-2cc8-479a-80df-29f7a7cf1a3e", label: "Theo - Modern Narrator", gender: "male" },
        { name: "f9836c6e-a0bd-460e-9d3c-f7299fa60f94", label: "Caroline - Southern Guide", gender: "female" },
        { name: "87286a8d-7ea7-4235-a41a-dd9fa6630feb", label: "Henry - Plainspoken Guy", gender: "male" },
        { name: "248be419-c632-4f23-adf1-5324ed7dbf1d", label: "Elizabeth - Manager", gender: "female" },
        { name: "0418348a-0ca2-4e90-9986-800fb8b3bbc0", label: "Antoine - Stern Man", gender: "male" },
    ];

    const handleTest = async () => {
        setLoading(true);
        setError(null);
        setAudioUrl(null);

        try {
            const response = await apiRequest(
                `${ENDPOINTS.DEBUG.TEST_TTS}?text=${encodeURIComponent(text)}&voice=${encodeURIComponent(voice)}&language=${encodeURIComponent(language)}&model_id=${encodeURIComponent(modelId)}`,
                { method: "POST" }
            );

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || "TTS request failed");
            }

            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            setAudioUrl(url);

            // Auto-play
            if (audioRef.current) {
                audioRef.current.src = url;
                audioRef.current.play();
            }
        } catch (e: unknown) {
            const message = e instanceof Error ? e.message : String(e);
            setError(message);
        } finally {
            setLoading(false);
        }
    };

    const handleVoiceChange = (voiceName: string) => {
        setVoice(voiceName);
        const selected = voices.find(v => v.name === voiceName);
        if (selected) {
            setGender(selected.gender);
        }
    };

    return (
        <div className="min-h-screen bg-gray-900 text-white p-8">
            <div className="max-w-2xl mx-auto">
                <h1 className="text-3xl font-bold mb-2 flex items-center gap-3">
                    <Volume2 className="w-8 h-8 text-green-400" />
                    TTS Debug Tool
                </h1>
                <p className="text-gray-400 mb-8">Test Cartesia Text-to-Speech API directly</p>

                <div className="grid grid-cols-2 gap-4 mb-6">
                    {/* Language Selector */}
                    <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">
                            <Globe className="w-4 h-4 inline mr-2" />
                            Language
                        </label>
                        <select
                            value={language}
                            onChange={(e) => setLanguage(e.target.value)}
                            className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white focus:ring-2 focus:ring-green-500 focus:border-transparent"
                        >
                            {languages.map((l) => (
                                <option key={l.code} value={l.code}>
                                    {l.name}
                                </option>
                            ))}
                        </select>
                    </div>

                    {/* Model Selector */}
                    <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">
                            <Globe className="w-4 h-4 inline mr-2" />
                            Model
                        </label>
                        <select
                            value={modelId}
                            onChange={(e) => setModelId(e.target.value)}
                            className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white focus:ring-2 focus:ring-green-500 focus:border-transparent"
                        >
                            {models.map((m) => (
                                <option key={m.id} value={m.id}>
                                    {m.name}
                                </option>
                            ))}
                        </select>
                    </div>
                </div>

                {/* Voice Selector */}
                <div className="mb-6">
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                        <Volume2 className="w-4 h-4 inline mr-2" />
                        Voice Selection
                    </label>
                    <select
                        value={voice}
                        onChange={(e) => handleVoiceChange(e.target.value)}
                        className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    >
                        {voices.map((v) => (
                            <option key={v.name} value={v.name}>
                                {v.label}
                            </option>
                        ))}
                    </select>
                    <p className="text-xs text-gray-500 mt-1">Gender: {gender}</p>
                </div>

                {/* Text Input */}
                <div className="mb-6">
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                        Text to Speak
                    </label>
                    <textarea
                        value={text}
                        onChange={(e) => setText(e.target.value)}
                        placeholder="Enter text to convert to speech..."
                        rows={4}
                        className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder:text-gray-500 focus:ring-2 focus:ring-green-500 focus:border-transparent resize-none"
                    />
                    <p className="text-xs text-gray-500 mt-1">{text.length} characters</p>
                </div>

                {/* Generate Button */}
                <button
                    onClick={handleTest}
                    disabled={loading || !text.trim()}
                    className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white font-semibold py-4 px-6 rounded-lg flex items-center justify-center gap-2 transition-colors"
                >
                    {loading ? (
                        <>
                            <Loader2 className="w-5 h-5 animate-spin" />
                            Generating Audio...
                        </>
                    ) : (
                        <>
                            <Play className="w-5 h-5" />
                            Generate & Play
                        </>
                    )}
                </button>

                {/* Error Display */}
                {error && (
                    <div className="mt-4 p-4 bg-red-900/50 border border-red-700 rounded-lg text-red-300">
                        <strong>Error:</strong> {error}
                    </div>
                )}

                {/* Audio Player */}
                {audioUrl && (
                    <div className="mt-6 p-4 bg-gray-800 rounded-lg">
                        <p className="text-sm text-gray-400 mb-2">Generated Audio:</p>
                        <audio
                            ref={audioRef}
                            controls
                            className="w-full"
                            src={audioUrl}
                        />
                    </div>
                )}

                {/* API Info */}
                <div className="mt-8 p-4 bg-gray-800/50 rounded-lg border border-gray-700">
                    <h3 className="text-sm font-semibold text-gray-300 mb-2">API Endpoint</h3>
                    <code className="text-xs text-green-400 break-all">
                        POST /api/v1/debug/test-tts
                    </code>
                </div>
            </div>
        </div>
    );
}
