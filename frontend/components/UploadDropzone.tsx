"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Input } from "@/components/ui/input"
import { Upload, Loader2, Sparkles, FileText, Briefcase, Layers, Globe } from "lucide-react"
import { useAuth } from "@clerk/nextjs";
import MDEditor from "@uiw/react-md-editor";
import { useLanguage } from "@/contexts/LanguageContext";
import { fetchWithAuth } from "@/lib/api";
import { ENDPOINTS } from "@/lib/endpoints";
import { Combobox } from "@/components/ui/combobox";

interface UploadDropzoneProps {
    mode?: "practice" | "application";
}

const JOB_ROLES = [
    { label: "Frontend Engineer (React/Next.js)", value: "Frontend Engineer", group: "Engineering" },
    { label: "Backend Engineer (Python/Go/Java)", value: "Backend Engineer", group: "Engineering" },
    { label: "Fullstack Developer", value: "Fullstack Developer", group: "Engineering" },
    { label: "DevOps / SRE", value: "DevOps Engineer", group: "Engineering" },
    { label: "Mobile Developer (iOS/Android)", value: "Mobile Developer", group: "Engineering" },
    { label: "Data Engineer", value: "Data Engineer", group: "Engineering" },
    { label: "Machine Learning Engineer", value: "Machine Learning Engineer", group: "Engineering" },
    { label: "Software Architect", value: "Software Architect", group: "Engineering" },
    { label: "QA / Automation Engineer", value: "QA Engineer", group: "Engineering" },
    { label: "Security Engineer", value: "Security Engineer", group: "Engineering" },
    { label: "Engineering Manager", value: "Engineering Manager", group: "Engineering" },
];

export default function UploadDropzone({ mode = "practice" }: UploadDropzoneProps) {
    const { t } = useLanguage();
    const { getToken } = useAuth();
    const [file, setFile] = useState<File | null>(null)
    const [loading, setLoading] = useState(false)
    const [generating, setGenerating] = useState(false)
    const [jobRole, setJobRole] = useState("Senior Python Developer")
    const [jobDescription, setJobDescription] = useState("")

    const router = useRouter()

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0])
        }
    }

    const handleUpload = async () => {
        if (!jobRole) {
            alert("Please select or enter a Job Role");
            return;
        }

        console.log("Submitting with language: en");

        setLoading(true)
        const formData = new FormData()
        formData.append("job_role", jobRole)
        if (file) {
            formData.append("file", file)
        }
        if (jobDescription) {
            formData.append("job_description", jobDescription)
        }
        formData.append("language", "en")

        try {
            // Distinct API paths for "The Gauntlet" (App) vs "The Sparring Ring" (Practice)
            const endpoint = mode === "application" ? ENDPOINTS.APPLICATION.LIST : ENDPOINTS.INTERVIEW.PRACTICE_CREATE;
            const res = await fetchWithAuth(endpoint, {
                method: "POST",
                body: formData,
            }, getToken)


            if (!res.ok) {
                throw new Error("Upload failed")
            }

            const data = await res.json()
            if (mode === "application") {
                router.push(`/applications/${data.application_id}`)
            } else {
                router.push(`/interview/${data.session_id}`)
            }
        } catch (error) {
            console.error(error)
            alert("Failed to start interview")
        } finally {
            setLoading(false)
        }
    }

    const handleAutoGenerate = async () => {
        if (!jobRole) {
            alert("Please select or enter a Job Role first");
            return;
        }

        setGenerating(true);
        try {
            const res = await fetchWithAuth(ENDPOINTS.RESUME.GENERATE_JD, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    job_role: jobRole,
                    language: "en"
                }),
            }, getToken);


            if (!res.ok) throw new Error("Failed to generate JD");

            const data = await res.json();
            setJobDescription(data.job_description);
        } catch (error) {
            console.error(error);
            alert("Failed to generate Job Description");
        } finally {
            setGenerating(false);
        }
    };

    return (
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700/60 shadow-sm p-6">
            <div className="grid gap-6 lg:grid-cols-10">
                {/* Left Column: Job Info & CV */}
                <div className="space-y-5 lg:col-span-4">
                    <div className="space-y-2">
                        <label className="text-sm font-medium text-gray-800 dark:text-gray-100 flex items-center gap-2">
                            <Briefcase className="w-4 h-4" /> {t('setup.jobRole')}
                        </label>

                        <Combobox
                            options={JOB_ROLES}
                            value={jobRole}
                            onChange={setJobRole}
                            placeholder={t('setup.customRolePlaceholder')}
                            searchPlaceholder="Search role..."
                            allowCustom={true}
                        />

                    </div>



                    <div className="space-y-2">
                        <label className="text-sm font-medium text-gray-800 dark:text-gray-100 flex items-center gap-2">
                            <FileText className="w-4 h-4" /> {t('setup.uploadCV')}
                            <span className="text-xs font-normal text-gray-500 dark:text-gray-400">{t('setup.optional')}</span>
                        </label>
                        <p className="text-xs text-gray-500 dark:text-gray-400">{t('setup.skipCV')}</p>
                        <Input
                            type="file"
                            accept=".pdf"
                            className="bg-white dark:bg-gray-900 text-gray-800 dark:text-gray-100 h-11 pt-2 file:mr-4 file:py-1 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-medium file:bg-[#424874] file:text-white hover:file:bg-[#363B5E] cursor-pointer border-gray-200 dark:border-gray-700/60"
                            onChange={handleFileChange}
                        />
                        {file && (
                            <div className="p-2 bg-green-50 dark:bg-green-500/10 border border-green-200 dark:border-green-500/30 rounded-lg flex items-center gap-2">
                                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                                <span className="text-xs font-medium text-green-700 dark:text-[#A6B1E1] truncate">{file.name}</span>
                            </div>
                        )}
                    </div>

                    {mode === "application" && (
                        <div className="p-4 bg-gray-50 dark:bg-gray-700/30 border border-gray-200 dark:border-gray-700/60 rounded-lg">
                            <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase mb-3">{t('setup.interviewStages')}</h3>
                            <div className="space-y-2 text-sm">
                                <div className="flex items-center gap-2">
                                    <span className="w-5 h-5 rounded-full bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400 flex items-center justify-center text-xs font-bold">1</span>
                                    <span className="text-gray-600 dark:text-gray-300">{t('setup.hrScreening')}</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <span className="w-5 h-5 rounded-full bg-gray-100 dark:bg-gray-700 text-[#424874] dark:text-[#A6B1E1] flex items-center justify-center text-xs font-bold">2</span>
                                    <span className="text-gray-600 dark:text-gray-300">{t('setup.technicalInterview')}</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <span className="w-5 h-5 rounded-full bg-[#DCD6F7] dark:bg-[#424874]/20 text-[#424874] dark:text-[#A6B1E1] flex items-center justify-center text-xs font-bold">3</span>
                                    <span className="text-gray-600 dark:text-gray-300">{t('setup.behavioralValues')}</span>
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                {/* Right Column: Job Description */}
                <div className="space-y-2 lg:col-span-6">
                    <div className="flex justify-between items-center">
                        <label className="text-sm font-medium text-gray-800 dark:text-gray-100">
                            {t('setup.jobDescription')}
                            <span className="text-xs font-normal text-gray-500 dark:text-gray-400 ml-1">{t('setup.optional')}</span>
                        </label>
                        <button
                            type="button"
                            onClick={handleAutoGenerate}
                            disabled={generating}
                            className="text-xs font-mono font-medium text-[#424874] hover:text-[#363B5E] dark:text-[#A6B1E1] dark:hover:text-[#DCD6F7] flex items-center gap-1 disabled:opacity-50 transition-colors"
                        >
                            {generating ? <Loader2 className="w-3 h-3 animate-spin" /> : <Sparkles className="w-3 h-3" />}
                            {t('setup.autoGenerate')}
                        </button>
                    </div>

                    {/* Markdown Editor with built-in toolbar and preview */}
                    <div data-color-mode="light" className="dark:hidden">
                        <MDEditor
                            value={jobDescription}
                            onChange={(val) => setJobDescription(val || "")}
                            height={304}
                            preview="edit"
                            textareaProps={{
                                placeholder: t('setup.jdPlaceholder')
                            }}
                        />
                    </div>
                    <div data-color-mode="dark" className="hidden dark:block">
                        <MDEditor
                            value={jobDescription}
                            onChange={(val) => setJobDescription(val || "")}
                            height={304}
                            preview="edit"
                            textareaProps={{
                                placeholder: t('setup.jdPlaceholder')
                            }}
                        />
                    </div>

                    <p className="text-xs text-gray-400 dark:text-gray-500">
                        {t('setup.jdHelpText')}
                    </p>
                </div>
            </div>

            {/* Submit Button */}
            <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700/60">
                <button
                    className="w-full h-12 flex items-center justify-center gap-2 bg-[#424874] hover:bg-[#363B5E] text-white rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    onClick={handleUpload}
                    disabled={loading}
                >
                    {loading ? (
                        <>
                            <Loader2 className="w-5 h-5 animate-spin" />
                            {t('setup.processing')}
                        </>
                    ) : (
                        <>
                            {mode === "application" ? <Layers className="w-5 h-5" /> : <Upload className="w-5 h-5" />}
                            {mode === "application" ? t('setup.startApplication') : t('setup.startPractice')}
                        </>
                    )}
                </button>
            </div>
        </div>
    )
}
