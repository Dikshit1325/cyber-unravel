// Mock Supabase client for development/demo purposes
// This serves as a fallback when the real Supabase client fails

const mockUsers: Record<string, any> = {};
const mockAuthState = {
  session: null as any,
};

// Demo users for testing
const DEMO_USERS: Record<string, string> = {
  "user@example.com": "password123",
  "investigator@sentinel.gov": "SecurePass123",
};

export const mockSupabaseClient = {
  auth: {
    getSession: async () => {
      console.log("[Mock] getSession");
      return {
        data: { session: mockAuthState.session },
        error: null,
      };
    },
    signUp: async (credentials: any) => {
      console.log("[Mock] signUp:", credentials.email);
      const user = {
        id: `user_${Math.random().toString(36).substr(2, 9)}`,
        email: credentials.email,
        user_metadata: credentials.options?.data || {},
      };
      mockUsers[credentials.email] = user;
      
      // Don't auto-confirm in signup - require email confirmation
      return {
        data: { session: null, user },
        error: null,
      };
    },
    signInWithPassword: async (credentials: any) => {
      console.log("[Mock] signInWithPassword:", credentials.email);
      
      // Check demo users
      if (DEMO_USERS[credentials.email] === credentials.password) {
        mockAuthState.session = {
          user: {
            id: `demo_${credentials.email}`,
            email: credentials.email,
            aud: "authenticated",
          },
          access_token: `mock_token_${Date.now()}`,
          expires_in: 3600,
          expires_at: Date.now() + 3600000,
        };
        return {
          data: { session: mockAuthState.session },
          error: null,
        };
      }
      
      // Check registered users
      if (mockUsers[credentials.email]) {
        mockAuthState.session = {
          user: {
            id: mockUsers[credentials.email].id,
            email: credentials.email,
            aud: "authenticated",
          },
          access_token: `mock_token_${Date.now()}`,
          expires_in: 3600,
          expires_at: Date.now() + 3600000,
        };
        return {
          data: { session: mockAuthState.session },
          error: null,
        };
      }
      
      return {
        data: { session: null },
        error: {
          message: "Invalid email or password",
          status: 400,
        },
      };
    },
    signInWithOAuth: async (provider: string, options: any) => {
      console.log("[Mock] signInWithOAuth:", provider);
      // Simulate OAuth by creating a mock session
      mockAuthState.session = {
        user: {
          id: `oauth_${provider}_${Math.random().toString(36).substr(2, 9)}`,
          email: `${provider}user@example.com`,
          aud: "authenticated",
        },
        access_token: `mock_oauth_token_${Date.now()}`,
        expires_in: 3600,
        expires_at: Date.now() + 3600000,
      };
      return {
        data: { url: null },
        error: null,
      };
    },
    onAuthStateChange: (callback: any) => {
      // Call with current state
      callback(null, mockAuthState.session);
      
      return {
        data: {
          subscription: {
            unsubscribe: () => {},
          },
        },
      };
    },
    signOut: async () => {
      console.log("[Mock] signOut");
      mockAuthState.session = null;
      return { error: null };
    },
  },
};

