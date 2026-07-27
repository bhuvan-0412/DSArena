import { NextResponse } from "next/server";
import { createClient } from "@/lib/supabase/server";

export async function GET(request: Request) {
  const { searchParams, origin } = new URL(request.url);
  const code = searchParams.get("code");
  const next = searchParams.get("next") ?? "/dashboard";
  const error = searchParams.get("error");
  const errorDescription = searchParams.get("error_description");

  if (error) {
    console.error("Auth callback error parameter:", error, errorDescription);
    return NextResponse.redirect(`${origin}/sign-in?error=${encodeURIComponent(errorDescription || error)}`);
  }

  if (code) {
    const supabase = await createClient();
    const { data, error: exchangeError } = await supabase.auth.exchangeCodeForSession(code);

    if (!exchangeError && data.session?.user) {
      const user = data.session.user;

      // Sync user profile to backend
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";
      try {
        await fetch(`${backendUrl}/auth/sync`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${data.session.access_token}`,
          },
          body: JSON.stringify({
            clerk_id: user.id,
            email: user.email,
            username: user.user_metadata?.username || user.email?.split("@")[0] || "gladiator",
            display_name: user.user_metadata?.full_name || user.user_metadata?.name || user.email?.split("@")[0] || "Gladiator",
            avatar_url: user.user_metadata?.avatar_url || user.user_metadata?.picture || "",
          }),
        });
      } catch (syncErr) {
        console.error("Failed to sync user profile during auth callback:", syncErr);
      }

      const forwardedHost = request.headers.get("x-forwarded-host");
      const isLocalEnv = process.env.NODE_ENV === "development";
      if (isLocalEnv) {
        return NextResponse.redirect(`${origin}${next}`);
      } else if (forwardedHost) {
        return NextResponse.redirect(`https://${forwardedHost}${next}`);
      } else {
        return NextResponse.redirect(`${origin}${next}`);
      }
    } else if (exchangeError) {
      console.error("Exchange code for session failed:", exchangeError.message);
      return NextResponse.redirect(`${origin}/sign-in?error=${encodeURIComponent(exchangeError.message)}`);
    }
  }

  return NextResponse.redirect(`${origin}/sign-in?error=NoAuthCodeProvided`);
}
