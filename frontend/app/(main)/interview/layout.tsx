export default function InterviewLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    // Override parent padding for full-bleed interview experience
    return (
        <div className="-mx-4 sm:-mx-6 lg:-mx-8 -my-8 h-[calc(100vh-64px)]">
            {children}
        </div>
    );
}
