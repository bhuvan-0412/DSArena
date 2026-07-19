import Sidebar from "@/components/shared/sidebar";
import StatsBar from "@/components/shared/stats-bar";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex h-screen overflow-hidden bg-[#030303]">
      {/* Sidebar */}
      <Sidebar />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col pl-64 overflow-hidden relative">
        {/* Top Status Bar */}
        <StatsBar />

        {/* Dynamic Nested Content */}
        <main className="flex-1 overflow-y-auto p-8 container mx-auto max-w-7xl">
          {children}
        </main>
      </div>
    </div>
  );
}
