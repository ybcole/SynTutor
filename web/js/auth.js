import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';
import { CLERK_CONFIG, SUPABASE_CONFIG } from './config.js';

// js/config.js is git-ignored (see .gitignore); a fresh checkout boots without
// it, so point developers at the template when the values are still placeholders.
// The case where js/config.js is entirely absent is caught earlier by the
// preflight hook in js/config-hint.js (loaded by index.html / login.html before
// the entry module), because a missing module fails at link time before
// anything in this file can run.
const CONFIG_HELP = 'Missing js/config.js? Copy js/config.example.js to js/config.js '
  + 'and add your Clerk + Supabase keys (see docs/README.md).';

if (!CLERK_CONFIG.publishableKey || CLERK_CONFIG.publishableKey.includes('YOUR_')) {
  console.error(`Clerk configuration is missing or invalid. Paste your publishable key into js/config.js. ${CONFIG_HELP}`);
}
if (!SUPABASE_CONFIG.url || !SUPABASE_CONFIG.anonKey || SUPABASE_CONFIG.anonKey.includes('YOUR_')) {
  console.error(`Supabase configuration is missing or invalid. ${CONFIG_HELP}`);
}

// ── Clerk bootstrap ──
// The clerk.browser.js bundle only reacts to the publishable key when the key
// reaches it via a `data-clerk-publishable-key` script attribute (or the
// window.__clerk_publishable_key global). A bare script tag throws
// "Missing publishableKey" at load time and never creates window.Clerk, which
// kills any module that awaits loadClerk() and leaves the page unresponsive.
// So the bundle is injected on demand with the key from js/config.js, and the
// Clerk Frontend API domain is derived from that same key.
// Deferred-promise singleton: every caller awaits the same boot, so Clerk loads
// exactly once no matter how many modules call loadClerk().
let clerkPromise = null;

function clerkScriptSrc() {
  const encoded = CLERK_CONFIG.publishableKey.split('_')[2];
  const frontendApi = atob(encoded).slice(0, -1);
  return `https://${frontendApi}/npm/@clerk/clerk-js@5/dist/clerk.browser.js`;
}

function loadClerkScript() {
  return new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.src = clerkScriptSrc();
    script.async = false;
    script.crossOrigin = 'anonymous';
    script.dataset.clerkPublishableKey = CLERK_CONFIG.publishableKey;
    script.onload = () => resolve(window.Clerk);
    script.onerror = () => reject(new Error('Failed to load clerk.browser.js'));
    document.head.appendChild(script);
  });
}

export function loadClerk() {
  if (!clerkPromise) {
    clerkPromise = (async () => {
      if (!window.Clerk) {
        await loadClerkScript();
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
// The same self-contained auth flow is wired for two surfaces:
//   login.html  — standalone form; successful sign-in redirects to /index.html.
//   index.html  — in-app login modal; successful sign-in reloads the current
//                 page so the boot flow picks the session up as "authenticated".
// In-flight email-code verification state is shared across surfaces because
// only one form exists on a given page. Email codes are now only used for
// second-factor sign-in on existing accounts — registration never sends one.
let activeSignIn = null;
let activeSignUp = null;
let pendingCodeAction = null;

function formatClerkError(err) {
  const errs = err?.errors;
  if (Array.isArray(errs) && errs[0]) {
    return errs[0].longMessage || errs[0].message || 'Authentication failed.';
  }
  return err?.message || 'An authentication error occurred.';
}

// Clerk rejects signIn.create()/signUp.create() while a session is active
// unless the application allows multiple sessions ("You're already signed
// in."). Detect that case so the UI can explain the actual fix instead of
// echoing the raw error.
function isAlreadySignedInError(err) {
  const match = (s) => typeof s === 'string' && /already signed in/i.test(s);
  if (match(err?.message)) return true;
  const errs = err?.errors;
  return Array.isArray(errs) && errs.some((e) =>
    e?.code === 'already_signed_in' || match(e?.message) || match(e?.longMessage));
}

const ALREADY_SIGNED_IN_HELP = 'Already signed in. To add another account, turn on '
  + 'multi-session in the Clerk Dashboard (Sessions → Multi-session handling). '
  + 'To use a different account instead, log out first.';

// Password requirements checked live on the registration form so the learner
// is told exactly what is missing instead of getting a generic rejection (or
// an email code) back from the backend. The Clerk instance requires 15+
// characters; the character-class tips are advisory only.
const PASSWORD_RULES = [
  { key: 'length', required: true, test: (p) => p.length >= 15, label: 'At least 15 characters' },
  { key: 'upper', required: false, test: (p) => /[A-Z]/.test(p), label: 'An uppercase letter (recommended)' },
  { key: 'lower', required: false, test: (p) => /[a-z]/.test(p), label: 'A lowercase letter (recommended)' },
  { key: 'number', required: false, test: (p) => /[0-9]/.test(p), label: 'A number (recommended)' },
  { key: 'symbol', required: false, test: (p) => /[!@#$%^&*()_+\-=[\]{};':"\\|,<>/?~]/.test(p), label: 'A symbol (recommended)' },
];

function passwordIssues(password) {
  return PASSWORD_RULES
    .filter((rule) => rule.required && !rule.test(password))
    .map((rule) => rule.label);
}
function wireAuthForm(ctx) {
  const {
    form,
    emailInput,
    passwordInput,
    codeInput,
    signUpBtn,
    signInBtn,
    statusMsg,
    finishRedirect,
    reqsId,
  } = ctx;

  if (!form) return;

  function setStatus(text, isError = false) {
    if (!statusMsg) return;
    statusMsg.textContent = text;
    statusMsg.className = `msg ${isError ? 'err' : 'ok'}`;
  }

  function syncPasswordReqs() {
    if (!reqsId || !passwordInput) return;
    const reqsEl = document.querySelector(reqsId);
    if (!reqsEl) return;
    const value = passwordInput.value || '';
    reqsEl.innerHTML = '';
    PASSWORD_RULES.forEach((rule) => {
      const ok = rule.test(value);
      const row = document.createElement('span');
      row.className = `pw-req${ok ? ' ok' : rule.required ? ' missing' : ' soft'}`;
      row.textContent = `${ok ? '\u2713' : '\u2022'} ${rule.label}`;
      reqsEl.appendChild(row);
    });
    reqsEl.hidden = !value;
  }
  if (passwordInput && reqsId) {
    passwordInput.addEventListener('input', syncPasswordReqs);
    passwordInput.addEventListener('focus', () => {
      if (passwordInput.value) syncPasswordReqs();
    });
    passwordInput.addEventListener('blur', () => {
      const reqsEl = document.querySelector(reqsId);
      if (reqsEl && !passwordInput.value) reqsEl.hidden = true;
    });
  }

  const pwToggle = form.querySelector('.password-toggle');
  if (pwToggle && passwordInput) {
    pwToggle.addEventListener('click', () => {
      const show = passwordInput.type === 'password';
      passwordInput.type = show ? 'text' : 'password';
      pwToggle.classList.toggle('shown', show);
      pwToggle.setAttribute('aria-pressed', String(show));
      pwToggle.setAttribute('aria-label', show ? 'Hide password' : 'Show password');
      passwordInput.focus();
    });
  }

  function showCodeStep(message) {
    form.querySelectorAll('.step-auth').forEach((el) => { el.style.display = 'none'; });
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
    form.querySelectorAll('.step-auth').forEach((el) => { el.style.display = ''; });
    const codeField = codeInput?.closest('.code-field');
    if (codeField) codeField.style.display = 'none';
    if (signUpBtn) signUpBtn.style.display = '';
    if (signInBtn) signInBtn.textContent = 'Sign In';
    if (codeInput) codeInput.value = '';
    if (emailInput) emailInput.setAttribute('required', '');
    if (passwordInput) passwordInput.setAttribute('required', '');
    if (passwordInput) passwordInput.setAttribute('autocomplete', 'current-password');
    pendingCodeAction = null;
    activeSignIn = null;
    activeSignUp = null;
  }

  async function completeSignIn(clerk, createdSessionId) {
    await clerk.setActive({ session: createdSessionId });
    if (finishRedirect) {
      window.location.href = '/index.html';
    } else {
      window.location.reload();
    }
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    try {
      // Resuming an in-flight verification: email/password are already consumed,
      // so this submit only carries the emailed one-time code. If the code field
      // is empty, re-prompt instead of falling through to a fresh sign-in.
      if (pendingCodeAction) {
        if (!codeInput?.value) {
          setStatus('Enter the verification code from your email.', true);
          codeInput?.focus();
          return;
        }
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
      setStatus(isAlreadySignedInError(err) ? ALREADY_SIGNED_IN_HELP : formatClerkError(err), true);
    }
  });

  signUpBtn?.addEventListener('click', async () => {
    const email = emailInput?.value?.trim();
    const password = passwordInput?.value;

    if (!email || !password) {
      setStatus('Enter an email and password to register.', true);
      return;
    }
    const missing = passwordIssues(password);
    if (missing.length) {
      setStatus(`Password needs: ${missing.join('; ')}.`, true);
      passwordInput?.focus();
      return;
    }
    // Register path collects a new credential, not an existing one.
    passwordInput?.setAttribute('autocomplete', 'new-password');

    try {
      setStatus('Registering account...');
      const clerk = await loadClerk();
      const signUp = await clerk.client.signUp.create({ emailAddress: email, password });

      if (signUp.status === 'complete') {
        resetCodeStep();
        await completeSignIn(clerk, signUp.createdSessionId);
        return;
      }

      // Registration no longer sends a verification code. If Clerk still has
      // something to collect, report exactly what is missing (normally a
      // failed password requirement) so the learner can fix it and retry.
      const required = new Set(signUp.requiredFields || []);
      const missingFields = new Set(signUp.missingFields || []);
      const emailVerification = signUp.verifications?.email_address;

      if (required.has('password_requirements') || missingFields.has('password_requirements')) {
        const still = passwordIssues(password);
        setStatus(still.length
          ? `Password needs: ${still.join('; ')}.`
          : 'The password does not meet the registration requirements.', true);
        return;
      }
      if (emailVerification && emailVerification.status === 'unverified') {
        setStatus(
          'Email confirmation is required, but verification emails are disabled here. '
          + 'Enable \u201cskip email verification\u201d in your Clerk dashboard to register without a code.',
          true,
        );
        return;
      }

      setStatus(`Registration is not complete (status: ${signUp.status}).`, true);
    } catch (err) {
      resetCodeStep();
      setStatus(isAlreadySignedInError(err) ? ALREADY_SIGNED_IN_HELP : formatClerkError(err), true);
    }
  });
}

wireAuthForm({
  form: document.querySelector('#loginForm'),
  emailInput: document.querySelector('#email'),
  passwordInput: document.querySelector('#password'),
  codeInput: document.querySelector('#verificationCode'),
  signUpBtn: document.querySelector('#signUpBtn'),
  signInBtn: document.querySelector('#signInBtn'),
  statusMsg: document.querySelector('#authStatus'),
  reqsId: '#passwordReqs',
  finishRedirect: true,
});

wireAuthForm({
  form: document.querySelector('#authModalForm'),
  emailInput: document.querySelector('#authEmail'),
  passwordInput: document.querySelector('#authPassword'),
  codeInput: document.querySelector('#authCode'),
  signUpBtn: document.querySelector('#authSignUpBtn'),
  signInBtn: document.querySelector('#authSignInBtn'),
  statusMsg: document.querySelector('#authModalStatus'),
  reqsId: '#authPasswordReqs',
  finishRedirect: false,
});

// Redirect if a session already exists
(async () => {
  try {
    const clerk = await loadClerk();
    if (clerk.session && window.location.pathname.endsWith('login.html')) {
      window.location.href = '/index.html';
    }
  } catch (err) {
    const statusMsg = document.querySelector('#authStatus') || document.querySelector('#authModalStatus');
    if (statusMsg) {
      statusMsg.className = 'msg err';
      statusMsg.textContent = formatClerkError(err);
    }
  }
})();