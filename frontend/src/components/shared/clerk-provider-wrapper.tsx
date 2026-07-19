"use client";

import React from "react";
import { ClerkProvider } from "@clerk/nextjs";

export default function ClerkProviderWrapper({ children }: { children: React.ReactNode }) {
  const publishableKey = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY;

  if (!publishableKey) {
    // If Clerk is not configured, pass children directly.
    // This allows the app to run in mock mode without throwing Clerk initialization errors.
    return <>{children}</>;
  }

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
