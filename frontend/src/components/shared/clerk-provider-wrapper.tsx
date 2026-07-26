"use client";

import React from "react";
import { ClerkProvider } from "@clerk/nextjs";

export default function ClerkProviderWrapper({ children }: { children: React.ReactNode }) {
  const publishableKey = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY || "pk_test_bW9jay1jbGVyay1rZXktZm9yLWRzYXJlbmEtZGV2LmNsa2Vya3MuZGV2JA";

  return (
    <ClerkProvider
      publishableKey={publishableKey}
      appearance={{
        variables: {
          colorPrimary: "#ff4655",
          colorBackground: "#0a0a0f",
        },
      }}
    >
      {children}
    </ClerkProvider>
  );
}
