export default function FeedbackLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    // Restore padding for feedback pages (override interview layout's negative margins)
    return (
        <div className="h-full overflow-y-auto">
            <div className="px-4 sm:px-6 lg:px-8 py-8 max-w-6xl mx-auto">
                {children}
            </div>
        </div>
    );
}
