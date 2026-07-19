"use client";

import { useUser } from "@clerk/nextjs";
import { useState, useEffect } from "react";

export interface UserStats {
  id: number;
  clerk_id: string;
  email: string;
  username: string;
  display_name: string;
  xp: number;
  level: number;
  rank: string;
  current_streak: number;
  max_streak: number;
}

const BACKEND_URL = "http://127.0.0.1:8000/api/v1";

export function useAuthUser() {
  const isClerkConfigured = !!process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY;
  // eslint-disable-next-line react-hooks/rules-of-hooks
  const clerk = isClerkConfigured ? useUser() : null;

  const [stats, setStats] = useState<UserStats | null>(null);
  const [loading, setLoading] = useState(true);

  // Mock User for when Clerk is not configured
  const mockUser = {
    id: "mock_user_striver",
    username: "striver_ninja",
    fullName: "Take U Forward",
    primaryEmailAddress: { emailAddress: "striver@dsarena.com" },
    imageUrl: "https://api.dicebear.com/7.x/pixel-art/svg?seed=striver",
  };

  const isSignedIn = isClerkConfigured ? !!clerk?.isSignedIn : true;
  const user = isClerkConfigured ? clerk?.user : mockUser;
  const isLoaded = isClerkConfigured ? !!clerk?.isLoaded : true;

  const clerkId = user?.id || "mock_user_striver";
  const userEmail = user?.primaryEmailAddress?.emailAddress || "striver@dsarena.com";
  const userUsername = user?.username || "striver_ninja";
  const userDisplayName = user?.fullName || "Take U Forward";

  useEffect(() => {
    if (!isLoaded || !isSignedIn) {
      setLoading(false);
      return;
    }

    async function syncAndFetchUser() {
      try {
        setLoading(true);
        // 1. Sync User to Backend
        const syncResponse = await fetch(`${BACKEND_URL}/auth/sync`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            clerk_id: clerkId,
            email: userEmail,
            username: userUsername,
            display_name: userDisplayName,
          }),
        });

        if (syncResponse.ok) {
          const syncedData = await syncResponse.json();
          setStats(syncedData);
        } else {
          console.error("Backend sync failed");
          // Fallback to local mock state on sync failure
          fallbackMockState();
        }
      } catch (err) {
        console.error("Error communicating with backend:", err);
        fallbackMockState();
      } finally {
        setLoading(false);
      }
    }

    function fallbackMockState() {
      setStats({
        id: 1,
        clerk_id: clerkId,
        email: userEmail,
        username: userUsername,
        display_name: userDisplayName,
        xp: 1450, // Level 2 (1000 + 450 XP)
        level: 2,
        rank: "Bronze",
        current_streak: 5,
        max_streak: 12,
      });
    }

    syncAndFetchUser();
  }, [clerkId, userEmail, userUsername, userDisplayName, isLoaded, isSignedIn]);

  const addXp = async (amount: number, action: string) => {
    try {
      const response = await fetch(`${BACKEND_URL}/users/${clerkId}/add-xp?amount=${amount}&action=${action}`, {
        method: "POST",
      });
      if (response.ok) {
        const updatedStats = await response.json();
        setStats(updatedStats);
      } else {
        // Local state update fallback if backend fails
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
      const response = await fetch(`${BACKEND_URL}/users/${clerkId}`);
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
    user,
    isLoaded: isLoaded && !loading,
    stats,
    addXp,
    refreshStats,
  };
}
