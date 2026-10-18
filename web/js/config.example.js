export const CLERK_CONFIG = {
  // Paste your Clerk publishable key here (Clerk Dashboard -> API Keys -> Publishable key).
  // Example value (dev/test instance): 'pk_test_...'
  publishableKey: 'YOUR_CLERK_PUBLISHABLE_KEY',
};

export const SUPABASE_CONFIG = {
  url: 'YOUR_SUPABASE_URL',
  anonKey: 'YOUR_SUPABASE_ANON_KEY',
};

// Base URL of the SynTutor NLP backend (no trailing slash).
// Leave '' to call same-origin '/api/parse' (local `python3 server/app.py`).
export const API_BASE = 'https://YOUR_BACKEND_HOST';
