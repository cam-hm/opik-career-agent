export default function TermsOfServicePage() {
    return (
        <div className="min-h-screen bg-white">
            <div className="container mx-auto px-6 py-16 max-w-4xl">
                <h1 className="text-4xl font-serif font-bold text-[#1a1a1a] mb-8">
                    Terms of Service
                </h1>

                <div className="prose prose-lg max-w-none text-slate-700 space-y-6">
                    <p className="text-slate-500 text-sm">
                        Last updated: December 2024
                    </p>

                    <section>
                        <h2 className="text-2xl font-serif font-bold text-[#1a1a1a] mt-8 mb-4">
                            1. Acceptance of Terms
                        </h2>
                        <p>
                            By accessing and using Opik Agent, you accept and agree to be bound
                            by the terms and provisions of this agreement. If you do not agree to
                            abide by these terms, please do not use this service.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-2xl font-serif font-bold text-[#1a1a1a] mt-8 mb-4">
                            2. Description of Service
                        </h2>
                        <p>
                            Opik Agent provides an AI-powered mock interview platform that:
                        </p>
                        <ul className="list-disc pl-6 space-y-2 mt-4">
                            <li>Analyzes your resume/CV to generate relevant interview questions</li>
                            <li>Conducts real-time voice-based mock interviews using AI</li>
                            <li>Provides feedback and performance analysis after interviews</li>
                            <li>Helps you prepare for job interviews in a safe environment</li>
                        </ul>
                    </section>

                    <section>
                        <h2 className="text-2xl font-serif font-bold text-[#1a1a1a] mt-8 mb-4">
                            3. User Responsibilities
                        </h2>
                        <p>As a user of this service, you agree to:</p>
                        <ul className="list-disc pl-6 space-y-2 mt-4">
                            <li>Provide accurate information in your uploaded documents</li>
                            <li>Use the service for personal interview preparation only</li>
                            <li>Not attempt to reverse engineer or exploit the AI system</li>
                            <li>Maintain the confidentiality of your account credentials</li>
                        </ul>
                    </section>

                    <section>
                        <h2 className="text-2xl font-serif font-bold text-[#1a1a1a] mt-8 mb-4">
                            4. Intellectual Property
                        </h2>
                        <p>
                            The Opik Agent platform, including its design, features, and content,
                            is protected by intellectual property laws. You retain ownership of any
                            documents you upload, but grant us a license to process them for the
                            purpose of providing our services.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-2xl font-serif font-bold text-[#1a1a1a] mt-8 mb-4">
                            5. Disclaimer
                        </h2>
                        <p>
                            Opik Agent is provided &quot;as is&quot; without warranties of any kind.
                            We do not guarantee that using our service will result in job offers
                            or successful interviews. The AI-generated feedback is for practice
                            purposes and should not be considered professional career advice.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-2xl font-serif font-bold text-[#1a1a1a] mt-8 mb-4">
                            6. Limitation of Liability
                        </h2>
                        <p>
                            To the maximum extent permitted by law, Opik Agent shall not be
                            liable for any indirect, incidental, special, or consequential damages
                            arising from the use or inability to use our services.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-2xl font-serif font-bold text-[#1a1a1a] mt-8 mb-4">
                            7. Changes to Terms
                        </h2>
                        <p>
                            We reserve the right to modify these terms at any time. Continued use
                            of the service after changes constitutes acceptance of the new terms.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-2xl font-serif font-bold text-[#1a1a1a] mt-8 mb-4">
                            8. Contact
                        </h2>
                        <p>
                            For questions about these Terms of Service, please contact us at
                            legal@aiinterviewer.com.
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
