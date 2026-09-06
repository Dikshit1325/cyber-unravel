import { supabase } from "../supabase/client";

export const lovable = {
  auth: {
    signInWithOAuth: async (
      provider: "google" | "github",
      options: { redirect_uri: string }
    ) => {
      try {
        if (!supabase) {
          throw new Error("Supabase client not initialized");
        }

        const { data, error } = await supabase.auth.signInWithOAuth({
          provider,
          options: {
            redirectTo: options.redirect_uri,
          },
        });

        if (error) {
          console.error(`OAuth error for ${provider}:`, error);
          return {
            error: error.message || `${provider} sign-in failed`,
            redirected: false,
            url: undefined,
          };
        }

        if (!data) {
          return {
            error: `No data returned from ${provider} OAuth`,
            redirected: false,
            url: undefined,
          };
        }

        return {
          error: null,
          redirected: !!data.url,
          url: data.url,
        };
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : `${provider} sign-in failed`;
        console.error("OAuth exception:", errorMessage);
        return {
          error: errorMessage,
          redirected: false,
          url: undefined,
        };
      }
    },
  },
};

export default lovable;
