"use client";

import React from "react";
import { SupabaseAuthProvider } from "@/components/auth/supabase-provider";

export default function AppAuthProvider({ children }: { children: React.ReactNode }) {
  return (
    <SupabaseAuthProvider>
      {children}
    </SupabaseAuthProvider>
  );
}
