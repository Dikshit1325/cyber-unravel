import { createFileRoute, useNavigate, Link } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { z } from "zod";
import { Loader2, ShieldAlert } from "lucide-react";
import { toast } from "sonner";
import { supabase } from "@/integrations/supabase/client";
import { lovable } from "@/integrations/lovable/index";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { CyberGlobe } from "@/components/landing/CyberGlobe";

export const Route = createFileRoute("/auth")({
  head: () => ({
    meta: [
      { title: "Investigator Access — SENTINEL" },
      {
        name: "description",
        content:
          "Sign in or register for authorized access to the SENTINEL digital investigation intelligence workspace.",
      },
      { property: "og:title", content: "Investigator Access — SENTINEL" },
      {
        property: "og:description",
        content: "Authorized investigator sign-in for cross-domain digital investigation analytics.",
      },
    ],
  }),
  component: AuthPage,
});

const credentials = z.object({
  email: z.string().trim().email({ message: "Enter a valid email address" }).max(255),
  password: z.string().min(8, { message: "Password must be at least 8 characters" }).max(128),
});

function AuthPage() {
  const navigate = useNavigate();
  const [mode, setMode] = useState<"signin" | "signup">("signin");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [badge, setBadge] = useState("");
  const [busy, setBusy] = useState(false);
  const [pendingConfirm, setPendingConfirm] = useState(false);

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (session) navigate({ to: "/dashboard", replace: true });
    });
    const { data } = supabase.auth.onAuthStateChange((_e, session) => {
      if (session) navigate({ to: "/dashboard", replace: true });
    });
    return () => data.subscription.unsubscribe();
  }, [navigate]);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    const parsed = credentials.safeParse({ email, password });
    if (!parsed.success) {
      toast.error(parsed.error.issues[0]?.message ?? "Invalid credentials");
      return;
    }
    setBusy(true);
    try {
      if (mode === "signup") {
        const { data, error } = await supabase.auth.signUp({
          email: parsed.data.email,
          password: parsed.data.password,
          options: {
            emailRedirectTo: window.location.origin,
            data: { full_name: fullName.trim().slice(0, 100), badge_number: badge.trim().slice(0, 40) },
          },
        });
        if (error) throw error;
        if (!data.session) {
          setPendingConfirm(true);
          toast.success("Check your email to confirm your account");
          return;
        }
      } else {
        const { error } = await supabase.auth.signInWithPassword({
          email: parsed.data.email,
          password: parsed.data.password,
        });
        if (error) throw error;
      }
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Authentication failed");
    } finally {
      setBusy(false);
    }
  };

  const google = async () => {
    setBusy(true);
    const result = await lovable.auth.signInWithOAuth("google", {
      redirect_uri: window.location.origin,
    });
    if (result.error) {
      setBusy(false);
      toast.error("Google sign-in failed");
      return;
    }
    if (result.redirected) return;
    navigate({ to: "/dashboard", replace: true });
  };

  return (
    <div className="relative grid min-h-screen lg:grid-cols-2">
      <div className="relative hidden overflow-hidden border-r border-border bg-background lg:block">
        <div className="grid-bg absolute inset-0 opacity-70" />
        <CyberGlobe className="absolute inset-0 size-full" />
        <div className="absolute bottom-8 left-8 max-w-sm">
          <p className="label-xs">Secure workspace</p>
          <p className="mt-2 text-lg font-semibold text-foreground">
            From scattered data to actionable intelligence.
          </p>
          <p className="mt-2 text-xs text-muted-foreground">
            Access is logged in the audit trail. Only authorized, lawfully obtained datasets may be
            analysed in this workspace.
          </p>
        </div>
      </div>

      <div className="flex items-center justify-center px-5 py-12">
        <div className="w-full max-w-sm">
          <Link to="/" className="flex items-center gap-2.5">
            <span className="grid size-9 place-items-center rounded-sm border border-primary/40 bg-primary/12 text-primary">
              <ShieldAlert className="size-4" aria-hidden />
            </span>
            <span className="text-sm font-semibold tracking-widest text-foreground uppercase">
              Sentinel
            </span>
          </Link>

          <h1 className="mt-7 text-2xl font-semibold tracking-tight text-foreground">
            {mode === "signin" ? "Investigator sign in" : "Request investigator access"}
          </h1>
          <p className="mt-1.5 text-sm text-muted-foreground">
            {mode === "signin"
              ? "Use your authorized credentials to open the command center."
              : "Register with your official email and badge number."}
          </p>

          {pendingConfirm ? (
            <div className="panel mt-6 p-4">
              <p className="text-sm text-foreground">Confirm your email</p>
              <p className="mt-1.5 text-xs text-muted-foreground">
                We sent a confirmation link to <span className="text-primary">{email}</span>. Open it
                to activate the account, then sign in.
              </p>
              <Button
                variant="outline"
                className="mt-4 w-full"
                onClick={() => {
                  setPendingConfirm(false);
                  setMode("signin");
                }}
              >
                Back to sign in
              </Button>
            </div>
          ) : (
            <>
              <form onSubmit={submit} className="mt-6 space-y-3.5">
                {mode === "signup" && (
                  <>
                    <div className="space-y-1.5">
                      <Label htmlFor="fullName">Full name</Label>
                      <Input
                        id="fullName"
                        value={fullName}
                        maxLength={100}
                        onChange={(e) => setFullName(e.target.value)}
                        placeholder="Inspector A. Rao"
                      />
                    </div>
                    <div className="space-y-1.5">
                      <Label htmlFor="badge">Badge number</Label>
                      <Input
                        id="badge"
                        value={badge}
                        maxLength={40}
                        onChange={(e) => setBadge(e.target.value)}
                        placeholder="TN-4471"
                      />
                    </div>
                  </>
                )}
                <div className="space-y-1.5">
                  <Label htmlFor="email">Official email</Label>
                  <Input
                    id="email"
                    type="email"
                    autoComplete="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="investigator@agency.gov"
                    required
                  />
                </div>
                <div className="space-y-1.5">
                  <Label htmlFor="password">Password</Label>
                  <Input
                    id="password"
                    type="password"
                    autoComplete={mode === "signin" ? "current-password" : "new-password"}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    required
                  />
                </div>
                <Button type="submit" className="w-full" disabled={busy}>
                  {busy && <Loader2 className="size-4 animate-spin" />}
                  {mode === "signin" ? "Sign in" : "Create account"}
                </Button>
              </form>

              <div className="my-4 flex items-center gap-3">
                <span className="h-px flex-1 bg-border" />
                <span className="label-xs">or</span>
                <span className="h-px flex-1 bg-border" />
              </div>

              <Button variant="outline" className="w-full" onClick={google} disabled={busy}>
                Continue with Google
              </Button>

              <p className="mt-5 text-center text-xs text-muted-foreground">
                {mode === "signin" ? "No account yet?" : "Already registered?"}{" "}
                <button
                  type="button"
                  className="text-primary hover:underline"
                  onClick={() => setMode(mode === "signin" ? "signup" : "signin")}
                >
                  {mode === "signin" ? "Request access" : "Sign in"}
                </button>
              </p>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
