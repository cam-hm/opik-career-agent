export default function PrivacyPolicyPage() {
    return (
        <div className="min-h-screen bg-white">
            <div className="container mx-auto px-6 py-16 max-w-4xl">
                <h1 className="text-4xl font-serif font-bold text-[#1a1a1a] mb-8">
                    Privacy Policy
                </h1>

                <div className="prose prose-lg max-w-none text-slate-700 space-y-6">
                    <p className="text-slate-500 text-sm">
                        Last updated: December 2024
                    </p>

                    <section>
                        <h2 className="text-2xl font-serif font-bold text-[#1a1a1a] mt-8 mb-4">
                            1. Information We Collect
                        </h2>
                        <p>
                            We collect information you provide directly to us, including:
                        </p>
                        <ul className="list-disc pl-6 space-y-2 mt-4">
                            <li>Resume/CV content when you upload documents</li>
                            <li>Audio and video data during interview sessions</li>
                            <li>Account information (email, name) through authentication</li>
                            <li>Interview transcripts and AI-generated feedback</li>
                        </ul>
                    </section>

                    <section>
                        <h2 className="text-2xl font-serif font-bold text-[#1a1a1a] mt-8 mb-4">
                            2. How We Use Your Information
                        </h2>
                        <p>
                            We use the information we collect to:
                        </p>
                        <ul className="list-disc pl-6 space-y-2 mt-4">
                            <li>Provide and improve our AI interview services</li>
                            <li>Generate personalized interview questions based on your resume</li>
                            <li>Create feedback and performance analysis</li>
                            <li>Communicate with you about your account</li>
                        </ul>
                    </section>

                    <section>
                        <h2 className="text-2xl font-serif font-bold text-[#1a1a1a] mt-8 mb-4">
                            3. Data Security
                        </h2>
                        <p>
                            We implement appropriate security measures to protect your personal
                            information. Your interview data is encrypted in transit and at rest.
                            We do not sell your personal information to third parties.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-2xl font-serif font-bold text-[#1a1a1a] mt-8 mb-4">
                            4. Third-Party Services
                        </h2>
                        <p>
                            We use the following third-party services to provide our platform:
                        </p>
                        <ul className="list-disc pl-6 space-y-2 mt-4">
                            <li><strong>LiveKit</strong> - Real-time video/audio infrastructure</li>
                            <li><strong>Google Gemini</strong> - AI conversation processing</li>
                            <li><strong>Deepgram</strong> - Speech recognition and synthesis</li>
                            <li><strong>Clerk</strong> - Authentication services</li>
                        </ul>
                    </section>

                    <section>
                        <h2 className="text-2xl font-serif font-bold text-[#1a1a1a] mt-8 mb-4">
                            5. Contact Us
                        </h2>
                        <p>
                            If you have any questions about this Privacy Policy, please contact us
                            at privacy@aiinterviewer.com.
                        </p>
                    </section>
                </div>

                <div className="mt-12 pt-8 border-t border-slate-200">
                    <a
                        href="/"
                        className="text-[#1a1a1a] hover:underline font-medium"
                    >
                        ← Back to Home
                    </a>
                </div>
            </div>
        </div>
    );
}
