"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, Compass, User, Trophy, Settings, LogOut } from "lucide-react";
import { motion } from "framer-motion";
import { useAuthUser } from "@/hooks/use-auth-user";

export default function Sidebar() {
  const pathname = usePathname();
  const { isSignedIn, userDisplayName, userEmail, userAvatarUrl, signOut } = useAuthUser();

  const menuItems = [
    { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
    { name: "Roadmap", href: "/roadmap", icon: Compass },
    { name: "Contests", href: "/contests", icon: Trophy },
    { name: "Profile & Badges", href: "/profile", icon: User },
    { name: "Settings", href: "/settings", icon: Settings },
  ];

  return (
    <aside className="w-64 border-r border-card-border bg-[#050508]/80 backdrop-blur-md flex flex-col justify-between p-6 fixed h-screen z-20">
      <div>
        {/* Logo */}
        <div className="flex items-center gap-2 mb-10">
          <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center font-black text-white text-lg shadow-lg shadow-primary/20">
            Ω
          </div>
          <span className="font-extrabold text-xl tracking-wider text-white">
            DS<span className="text-primary">ARENA</span>
          </span>
        </div>

        {/* Navigation */}
        <nav className="space-y-2">
          {menuItems.map((item) => {
            const isActive = pathname === item.href;
            const Icon = item.icon;

            return (
              <Link key={item.name} href={item.href} className="relative block">
                <div
                  className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 group ${
                    isActive
                      ? "text-white font-semibold"
                      : "text-muted-foreground hover:text-white"
                  }`}
                >
                  {/* Active background glow */}
                  {isActive && (
                    <motion.div
                      layoutId="activeNav"
                      className="absolute inset-0 bg-primary/10 border border-primary/20 rounded-xl"
                      transition={{ type: "spring", stiffness: 380, damping: 30 }}
                    />
                  )}

                  <Icon
                    className={`w-5 h-5 transition-transform duration-300 group-hover:scale-110 ${
                      isActive ? "text-primary" : "text-muted-foreground group-hover:text-white"
                    }`}
                  />
                  <span className="relative z-10">{item.name}</span>
                </div>
              </Link>
            );
          })}
        </nav>
      </div>

      {/* User Info & Logout Footer */}
      <div className="border-t border-card-border pt-4 space-y-3">
        {isSignedIn && (
          <div className="flex items-center gap-3 px-2 py-1.5 rounded-xl bg-slate-900/40 border border-slate-800/60">
            <img
              src={userAvatarUrl}
              alt={userDisplayName}
              className="w-8 h-8 rounded-full border border-primary/30 object-cover"
              onError={(e) => {
                (e.target as HTMLElement).setAttribute(
                  "src",
                  `https://api.dicebear.com/7.x/bottts/svg?seed=${userEmail}`
                );
              }}
            />
            <div className="min-w-0 flex-1">
              <p className="text-xs font-bold text-white truncate">{userDisplayName}</p>
              <p className="text-[10px] text-slate-400 truncate">{userEmail}</p>
            </div>
          </div>
        )}

        <button
          onClick={() => signOut()}
          className="flex w-full items-center gap-3 px-4 py-2.5 text-muted-foreground hover:text-destructive rounded-xl transition-colors duration-300 hover:bg-destructive/10 cursor-pointer text-xs font-semibold"
        >
          <LogOut className="w-4 h-4" />
          <span>Sign Out</span>
        </button>
      </div>
    </aside>
  );
}
