"use client";

import React, { createContext, useContext, useEffect, useState, useRef } from "react";
import { User, Session, SupabaseClient } from "@supabase/supabase-js";
import { createClient } from "@/lib/supabase/client";

interface SupabaseAuthContextType {
  currentUser: User | null;
  user: User | null;
  session: Session | null;
  loading: boolean;
  isLoading: boolean;
  error: string | null;
  signIn: () => Promise<void>;
  signInWithGoogle: () => Promise<void>;
  signOut: () => Promise<void>;
  clearError: () => void;
}



const SupabaseAuthContext = createContext<SupabaseAuthContextType>({
  currentUser: null,
  user: null,
  session: null,
  loading: true,
  isLoading: true,
  error: null,
  signIn: async () => {},
  signInWithGoogle: async () => {},
  signOut: async () => {},
  clearError: () => {},
});

export function SupabaseAuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Lazy ref — only created in the browser, never at module/SSR evaluation time
  const supabaseRef = useRef<SupabaseClient | null>(null);
  function getSupabase(): SupabaseClient {
    if (!supabaseRef.current) {
      supabaseRef.current = createClient();
    }
    return supabaseRef.current;
  }

  useEffect(() => {
    const supabase = getSupabase();
    // 1. Get Initial Session
    supabase.auth.getSession().then(({ data: { session }, error: sessionError }) => {
      if (sessionError) {
        console.error("Error fetching initial session:", sessionError.message);
        setError(sessionError.message);
      }
      setSession(session);
      setUser(session?.user ?? null);
      setLoading(false);
    }).catch((err) => {
      console.error("Session retrieval error:", err);
      setLoading(false);
    });

    // 2. Listen to Auth Changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
      setUser(session?.user ?? null);
      setLoading(false);
    });

    return () => {
      subscription.unsubscribe();
    };
  }, []);

  const signInWithGoogle = async () => {
    setError(null);
    try {
      const supabase = getSupabase();
      const origin = typeof window !== "undefined" ? window.location.origin : "http://localhost:3000";
      const { error: oauthError } = await supabase.auth.signInWithOAuth({
        provider: "google",
        options: {
          redirectTo: `${origin}/auth/callback?next=/dashboard`,
          queryParams: {
            access_type: "offline",
            prompt: "consent",
          },
        },
      });

      if (oauthError) {
        setError(oauthError.message);
        throw oauthError;
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to initiate Google Authentication";
      console.error("Error signing in with Google:", msg);
      setError(msg);
      throw new Error(msg);
    }
  };

  const signOut = async () => {
    try {
      setLoading(true);
      const { error: signOutError } = await getSupabase().auth.signOut();
      if (signOutError) console.error("Supabase signOut error:", signOutError.message);
    } catch (err) {
      console.error("Unexpected signOut error:", err);
    } finally {
      setUser(null);
      setSession(null);
      setLoading(false);
      if (typeof window !== "undefined") {
        window.location.href = "/sign-in";
      }
    }
  };

  const clearError = () => setError(null);

  return (
    <SupabaseAuthContext.Provider
      value={{
        currentUser: user,
        user,
        session,
        loading,
        isLoading: loading,
        error,
        signIn: signInWithGoogle,
        signInWithGoogle,
        signOut,
        clearError,
      }}
    >
      {children}
    </SupabaseAuthContext.Provider>
  );
}

export const useSupabaseAuth = () => useContext(SupabaseAuthContext);
export const useAuth = () => useContext(SupabaseAuthContext);
