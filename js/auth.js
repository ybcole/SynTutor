import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';
import { CLERK_CONFIG, SUPABASE_CONFIG } from './config.js';

if (!CLERK_CONFIG.publishableKey || CLERK_CONFIG.publishableKey.includes('YOUR_')) {
  console.error('Clerk configuration is missing or invalid. Paste your publishable key into js/config.js.');
}
if (!SUPABASE_CONFIG.url || !SUPABASE_CONFIG.anonKey || SUPABASE_CONFIG.anonKey.includes('YOUR_')) {
  console.error('Supabase configuration is missing or invalid. Check js/config.js.');
}

// ── Clerk bootstrap ──
// Requires the clerk.browser.js script tag to be present in the host page.
let clerkPromise = null;

export function loadClerk() {
  if (!clerkPromise) {
    clerkPromise = (async () => {
      if (!window.Clerk) {
        throw new Error('ClerkJS is not loaded. Add the clerk.browser.js script tag before this module.');
      }
      await window.Clerk.load({ publishableKey: CLERK_CONFIG.publishableKey });
      return window.Clerk;
    })();
  }
  return clerkPromise;
}

// ── Supabase client authenticated with the Clerk session token ──
// Clerk is configured as a third-party auth provider in Supabase, so the
// Clerk session token is accepted as a Supabase bearer token.
let supabasePromise = null;

export function createSupabaseClient() {
  if (!supabasePromise) {
    supabasePromise = (async () => {
      const clerk = await loadClerk();
      return createClient(SUPABASE_CONFIG.url, SUPABASE_CONFIG.anonKey, {
        auth: {
          persistSession: false,
          autoRefreshToken: false,
          detectSessionInUrl: false,
        },
        accessToken: async () => (clerk.session ? await clerk.session.getToken() : null),
      });
    })();
  }
  return supabasePromise;
}

// ── Custom sign-in / sign-up form (Clerk) ──
const form = document.querySelector('#loginForm');
const emailInput = document.querySelector('#email');
const passwordInput = document.querySelector('#password');
const codeInput = document.querySelector('#verificationCode');
const signUpBtn = document.querySelector('#signUpBtn');
const signInBtn = document.querySelector('#signInBtn');
const statusMsg = document.querySelector('#authStatus');

let activeSignIn = null;
let activeSignUp = null;
let pendingCodeAction = null;

function setStatus(text, isError = false) {
  if (!statusMsg) return;
  statusMsg.textContent = text;
  statusMsg.className = `msg ${isError ? 'err' : 'ok'}`;
}

function formatClerkError(err) {
  const errs = err?.errors;
  if (Array.isArray(errs) && errs[0]) {
    return errs[0].longMessage || errs[0].message || 'Authentication failed.';
  }
  return err?.message || 'An authentication error occurred.';
}

function showCodeStep(message) {
  document.querySelectorAll('.step-auth').forEach((el) => { el.style.display = 'none'; });
  if (signUpBtn) signUpBtn.style.display = 'none';
  const codeField = codeInput?.closest('.code-field');
  if (codeField) codeField.style.display = 'block';
  if (signInBtn) signInBtn.textContent = 'Verify Code';
  if (emailInput) emailInput.removeAttribute('required');
  if (passwordInput) passwordInput.removeAttribute('required');
  setStatus(message, false);
  codeInput?.focus();
}

function resetCodeStep() {
  document.querySelectorAll('.step-auth').forEach((el) => { el.style.display = ''; });
  const codeField = codeInput?.closest('.code-field');
  if (codeField) codeField.style.display = 'none';
  if (signUpBtn) signUpBtn.style.display = '';
  if (signInBtn) signInBtn.textContent = 'Sign In';
  if (codeInput) codeInput.value = '';
  if (emailInput) emailInput.setAttribute('required', '');
  if (passwordInput) passwordInput.setAttribute('required', '');
  pendingCodeAction = null;
  activeSignIn = null;
  activeSignUp = null;
}

async function completeSignIn(clerk, createdSessionId) {
  await clerk.setActive({ session: createdSessionId });
  window.location.href = '/index.html';
}

form?.addEventListener('submit', async (e) => {
  e.preventDefault();

  try {
    if (pendingCodeAction && codeInput?.value) {
      const clerk = await loadClerk();
      setStatus('Verifying code...');
      let createdSessionId = null;

      if (pendingCodeAction === 'second_factor' && activeSignIn) {
        const attempt = await activeSignIn.attemptSecondFactor({
          strategy: 'email_code',
          code: codeInput.value,
        });
        if (attempt.status === 'complete') {
          createdSessionId = attempt.createdSessionId;
        } else {
          setStatus('Verification failed. Check the code and try again.', true);
          return;
        }
      }

      if (pendingCodeAction === 'signup_verification' && activeSignUp) {
        const attempt = await activeSignUp.attemptVerification({
          strategy: 'email_code',
          code: codeInput.value,
        });
        if (attempt.status === 'complete') {
          createdSessionId = attempt.createdSessionId;
        } else {
          setStatus('Verification failed. Check the code and try again.', true);
          return;
        }
      }

      resetCodeStep();
      if (createdSessionId) await completeSignIn(clerk, createdSessionId);
      return;
    }

    setStatus('Signing in...');
    const clerk = await loadClerk();
    const signIn = await clerk.client.signIn.create({
      identifier: emailInput?.value?.trim(),
      password: passwordInput?.value,
    });

    if (signIn.status === 'complete') {
      resetCodeStep();
      await completeSignIn(clerk, signIn.createdSessionId);
      return;
    }
    if (signIn.status === 'needs_second_factor') {
      const emailCode = (signIn.supportedSecondFactors || []).find((f) => f.strategy === 'email_code');
      if (emailCode) {
        await signIn.prepareSecondFactor({
          strategy: 'email_code',
          emailAddressId: emailCode.emailAddressId,
        });
        activeSignIn = signIn;
        pendingCodeAction = 'second_factor';
        showCodeStep('A verification code was sent to your email.');
        return;
      }
      setStatus('Additional verification is required, but unsupported on this form.', true);
      return;
    }
    setStatus(`Sign-in is not complete (status: ${signIn.status}).`, true);
  } catch (err) {
    resetCodeStep();
    setStatus(formatClerkError(err), true);
  }
});

signUpBtn?.addEventListener('click', async () => {
  const email = emailInput?.value?.trim();
  const password = passwordInput?.value;

  if (!email || !password) {
    setStatus('Enter an email and password to register.', true);
    return;
  }

  try {
    setStatus('Registering account...');
    const clerk = await loadClerk();
    const signUp = await clerk.client.signUp.create({ emailAddress: email, password });

    if (signUp.status === 'complete') {
      resetCodeStep();
      await completeSignIn(clerk, signUp.createdSessionId);
      return;
    }

    const emailVerification = signUp.verifications?.email_address;
    if (signUp.status === 'missing_requirements' && emailVerification && emailVerification.status === 'unverified') {
      await signUp.prepareVerification({ strategy: 'email_code' });
      activeSignUp = signUp;
      pendingCodeAction = 'signup_verification';
      showCodeStep('A verification code was sent to your email.');
      return;
    }

    setStatus(`Registration is not complete (status: ${signUp.status}).`, true);
  } catch (err) {
    resetCodeStep();
    setStatus(formatClerkError(err), true);
  }
});

// Redirect if a session already exists
(async () => {
  try {
    const clerk = await loadClerk();
    console.log('[auth] loaded:', clerk.loaded, '| session:', clerk.session?.id ?? null, '| client sessions:', clerk.client?.sessions?.length ?? 'n/a');
    if (clerk.session && window.location.pathname.endsWith('login.html')) {
      console.log('[auth] redirect -> /index.html');
      window.location.href = '/index.html';
    }
  } catch (err) {
    resetCodeStep();
    setStatus(formatClerkError(err), true);
  }
})();