"use client";

import { useState, useEffect } from "react";
import { useSupabaseAuth } from "@/components/auth/supabase-provider";
import { BACKEND_URL } from "@/lib/api-config";

export interface UserStats {
  id: number;
  clerk_id: string;
  email: string;
  username: string;
  display_name: string;
  avatar_url?: string;
  xp: number;
  level: number;
  rank: string;
  current_streak: number;
  max_streak: number;
}



export function useAuthUser() {
  const { user: supabaseUser, session, isLoading: isSupabaseLoading, signOut, signInWithGoogle } = useSupabaseAuth();
  
  const [stats, setStats] = useState<UserStats | null>(null);
  const [loading, setLoading] = useState(true);

  // Mock User Fallback for local demo mode when not logged in with Supabase
  const mockUser = {
    id: "mock_user_striver",
    email: "striver@dsarena.com",
    user_metadata: {
      full_name: "Take U Forward",
      username: "striver_ninja",
      avatar_url: "https://api.dicebear.com/7.x/pixel-art/svg?seed=striver",
    },
  };

  const activeUser = supabaseUser || mockUser;
  const isSignedIn = !!supabaseUser;
  const isLoaded = !isSupabaseLoading;

  const userId = activeUser.id || "mock_user_striver";
  const userEmail = activeUser.email || "striver@dsarena.com";
  const metadata = (activeUser as Record<string, unknown>)?.user_metadata as Record<string, string> | undefined || {};
  const userUsername = metadata.username || userEmail.split("@")[0] || "striver_ninja";
  const userDisplayName = metadata.full_name || metadata.name || userEmail.split("@")[0] || "Take U Forward";
  const userAvatarUrl = metadata.avatar_url || metadata.picture || `https://api.dicebear.com/7.x/bottts/svg?seed=${userEmail}`;

  useEffect(() => {
    if (isSupabaseLoading) return;

    async function syncAndFetchUser() {
      try {
        setLoading(true);
        const headers: Record<string, string> = { "Content-Type": "application/json" };
        if (session?.access_token) {
          headers["Authorization"] = `Bearer ${session.access_token}`;
        }

        // Sync User with Backend
        const syncResponse = await fetch(`${BACKEND_URL}/auth/sync`, {
          method: "POST",
          headers,
          body: JSON.stringify({
            clerk_id: userId,
            email: userEmail,
            username: userUsername,
            display_name: userDisplayName,
            avatar_url: userAvatarUrl,
          }),
        });

        if (syncResponse.ok) {
          const syncedData = await syncResponse.json();
          setStats(syncedData);
        } else {
          fallbackState();
        }
      } catch (err) {
        console.error("Error communicating with backend auth:", err);
        fallbackState();
      } finally {
        setLoading(false);
      }
    }

    function fallbackState() {
      setStats({
        id: 1,
        clerk_id: userId,
        email: userEmail,
        username: userUsername,
        display_name: userDisplayName,
        avatar_url: userAvatarUrl,
        xp: 1500,
        level: 2,
        rank: "Bronze",
        current_streak: 7,
        max_streak: 14,
      });
    }

    syncAndFetchUser();
  }, [userId, userEmail, userUsername, userDisplayName, userAvatarUrl, session?.access_token, isSupabaseLoading]);

  const addXp = async (amount: number, action: string) => {
    try {
      const headers: Record<string, string> = {};
      if (session?.access_token) {
        headers["Authorization"] = `Bearer ${session.access_token}`;
      }

      const response = await fetch(`${BACKEND_URL}/users/${userId}/add-xp?amount=${amount}&action=${action}`, {
        method: "POST",
        headers,
      });
      if (response.ok) {
        const updatedStats = await response.json();
        setStats(updatedStats);
      } else {
        setStats((prev) => {
          if (!prev) return null;
          const nextXp = prev.xp + amount;
          const nextLevel = 1 + Math.floor(nextXp / 1000);
          return {
            ...prev,
            xp: nextXp,
            level: nextLevel,
            rank: nextLevel >= 2 ? "Bronze" : "Unranked",
          };
        });
      }
    } catch (err) {
      console.error("Error adding XP:", err);
    }
  };

  const refreshStats = async () => {
    try {
      const headers: Record<string, string> = {};
      if (session?.access_token) {
        headers["Authorization"] = `Bearer ${session.access_token}`;
      }

      const response = await fetch(`${BACKEND_URL}/users/${userId}`, { headers });
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (err) {
      console.error("Error refreshing stats:", err);
    }
  };

  return {
    isSignedIn,
    user: activeUser,
    clerkId: userId,
    userId,
    userEmail,
    userDisplayName,
    userUsername,
    userAvatarUrl,
    session,
    isLoaded: isLoaded && !loading,
    stats,
    addXp,
    signInWithGoogle,
    signOut,
    refreshStats,
  };
}
