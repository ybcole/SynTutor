import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';
import { CLERK_CONFIG, SUPABASE_CONFIG } from './config.js';
import { levelFromXp } from './level.js';

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

// ── Shared auth state ────────────────────────────────────────────────────
// The lesson catalog, the achievements and the history all need to know
// whether the current session is an account session. This is the one place
// that answers it, and the one place the rest of the app hears about it.
let authState = { authenticated: false, user: null };
const authListeners = new Set();

export function isUserAuthenticated() {
  return Boolean(authState.authenticated);
}

export function isGuestSession() {
  return !authState.authenticated;
}

export function currentAuthUser() {
  return authState.user;
}

// Listen for auth changes: the listener runs with the new state.
export function subscribeAuthState(fn) {
  authListeners.add(fn);
  return () => authListeners.delete(fn);
}

// Publish the current session state.
export function setAuthState(next) {
  authState = { ...authState, ...next };
  for (const fn of authListeners) {
    try { fn(authState); } catch (e) { /* one listener must not break the rest */ }
  }
}

// ── Guest progress ───────────────────────────────────────────────────────
// A guest can still work through the free lessons. That progress waits in
// local storage and is moved onto the account the moment it is created.
const GUEST_XP_KEY = 'syntutor_guest_xp';
const GUEST_LESSONS_KEY = 'syntutor_guest_completed_lessons';

// Remember what a guest achieved, so it can follow them to their account.
export function recordGuestProgress({ xp = 0, lesson = null } = {}) {
  try {
    if (xp) {
      const current = Number(localStorage.getItem(GUEST_XP_KEY) || 0) || 0;
      localStorage.setItem(GUEST_XP_KEY, String(current + xp));
    }
    if (lesson) {
      const list = JSON.parse(localStorage.getItem(GUEST_LESSONS_KEY) || '[]');
      if (Array.isArray(list) && !list.includes(lesson)) {
        list.push(lesson);
        localStorage.setItem(GUEST_LESSONS_KEY, JSON.stringify(list));
      }
    }
  } catch (e) { /* storage unavailable — the progress is simply not kept */ }
}

// The guest progress waiting to be migrated.
export function guestProgress() {
  try {
    return {
      xp: Number(localStorage.getItem(GUEST_XP_KEY) || 0) || 0,
      lessons: JSON.parse(localStorage.getItem(GUEST_LESSONS_KEY) || '[]') || [],
    };
  } catch (e) {
    return { xp: 0, lessons: [] };
  }
}

// Move the guest progress onto the new account, then clear the local copy.
export async function migrateGuestProgress() {
  const { xp, lessons } = guestProgress();
  if (!xp && !lessons.length) return { xp: 0, lessons: 0 };
  const clerk = await loadClerk();
  const supabase = await createSupabaseClient();
  const userId = clerk?.user?.id;
  if (!userId || !supabase) return { xp: 0, lessons: 0 };

  // The account may already have progress of its own (a learner signing in to
  // an account they used before): the guest's work is added on top of it.
  let carriedXp = 0;
  let migratedLessons = 0;
  try {
    if (xp > 0) {
      const { data: current } = await supabase
        .from('player_stats')
        .select('xp')
        .eq('user_id', userId)
        .maybeSingle();
      const totalXp = (Number(current?.xp) || 0) + xp;
      const { level } = levelFromXp(totalXp);
      const name = clerk?.user?.firstName
        || clerk?.user?.username
        || clerk?.user?.primaryEmailAddress?.emailAddress?.split('@')[0]
        || 'Learner';
      const { error } = await supabase.from('player_stats').upsert({
        user_id: userId, display_name: name, xp: totalXp, level, updated_at: new Date().toISOString(),
      }, { onConflict: 'user_id' });
      if (error) throw new Error(error.message);
      carriedXp = totalXp;
    }
    for (const ruleId of lessons) {
      const { data: row } = await supabase
        .from('quiz_progress')
        .select('completed_count, perfect_count')
        .eq('user_id', userId)
        .eq('rule_id', ruleId)
        .maybeSingle();
      const { error } = await supabase.from('quiz_progress').upsert({
        user_id: userId,
        rule_id: ruleId,
        completed_count: (Number(row?.completed_count) || 0) + 1,
        perfect_count: Number(row?.perfect_count) || 0,
        last_completed_at: new Date().toISOString(),
      }, { onConflict: 'user_id,rule_id' });
      if (error) throw new Error(error.message);
      migratedLessons += 1;
    }
  } catch (err) {
    // A failed transfer keeps the local copy: nothing is lost, and the next
    // sign-in tries again.
    console.warn('Failed to migrate the guest progress:', err);
    return { xp: carriedXp, lessons: migratedLessons, migrated: false };
  }
  try {
    localStorage.removeItem(GUEST_XP_KEY);
    localStorage.removeItem(GUEST_LESSONS_KEY);
  } catch (e) { /* storage unavailable */ }
  return { xp: carriedXp, lessons: migratedLessons, migrated: true };
}

// ── The auth modal ───────────────────────────────────────────────────────
// One dialog for the whole app: the sidebar login and the lessons gateway
// open this very same modal. Only the framing changes — the title, the
// subtitle and the way out — and which tab is active.
const AUTH_MODAL_COPY = {
  lessons_gate: {
    title: 'Create a free account to continue',
    subtitle: 'Save your progress, unlock all phrase and clause lessons, earn XP, and compete on the leaderboard.',
    dismiss: 'Continue Browsing Free Lessons',
  },
  sidebar_profile: {
    title: 'Welcome to SynTutor',
    subtitle: 'Sign in or create an account to sync your syntax trees and track achievements.',
    dismiss: 'Continue as guest',
  },
  // A second account while already signed in: there is no guest to return to.
  add_account: {
    title: 'Welcome to SynTutor',
    subtitle: 'Sign in or create an account to sync your syntax trees and track achievements.',
    dismiss: null,
  },
};

const AUTH_MODAL_MODES = {
  signin: { cta: 'Sign In', switchLabel: 'Need an account? Create one' },
  register: { cta: 'Create Free Account', switchLabel: 'Already have an account? Sign in' },
};

let authModalMode = 'signin';
let authModalReason = 'sidebar_profile';
// Where the focus came from: it goes back there when the dialog closes.
let authModalReturnFocus = null;

function authModalEls() {
  return {
    modal: document.getElementById('authModal'),
    title: document.getElementById('authModalTitle'),
    subtitle: document.getElementById('authModalSubtitle'),
    email: document.getElementById('authEmailInput'),
    password: document.getElementById('authPasswordInput'),
    status: document.getElementById('authModalStatus'),
    submit: document.getElementById('authSubmitBtn'),
    switchBtn: document.getElementById('authSwitchModeBtn'),
    dismissBtn: document.getElementById('authDismissGuestBtn'),
    signInTab: document.getElementById('authTabSignIn'),
    registerTab: document.getElementById('authTabRegister'),
    eyeBtn: document.getElementById('authTogglePasswordBtn'),
    form: document.getElementById('authForm'),
    reqs: document.getElementById('authPasswordReqs'),
  };
}

function setAuthModalStatus(message, isError = false) {
  const { status } = authModalEls();
  if (!status) return;
  status.textContent = message || '';
  status.hidden = !message;
  status.classList.toggle('is-error', Boolean(isError));
}

// The tab drives the button and the inline switch.
function applyAuthModalMode(mode) {
  authModalMode = AUTH_MODAL_MODES[mode] ? mode : 'signin';
  const { submit, switchBtn, signInTab, registerTab, password } = authModalEls();
  const conf = AUTH_MODAL_MODES[authModalMode];
  if (submit) submit.textContent = conf.cta;
  if (switchBtn) switchBtn.textContent = conf.switchLabel;
  if (signInTab) signInTab.classList.toggle('active', authModalMode === 'signin');
  if (registerTab) registerTab.classList.toggle('active', authModalMode === 'register');
  // A new password is being typed, or an existing one.
  if (password) password.setAttribute('autocomplete', authModalMode === 'register' ? 'new-password' : 'current-password');
}

// The reason frames the dialog: the title, the subtitle and the way out.
function applyAuthModalReason(reason) {
  authModalReason = AUTH_MODAL_COPY[reason] ? reason : 'sidebar_profile';
  const { title, subtitle, dismissBtn } = authModalEls();
  const copy = AUTH_MODAL_COPY[authModalReason];
  if (title) title.textContent = copy.title;
  if (subtitle) subtitle.textContent = copy.subtitle;
  if (dismissBtn) {
    dismissBtn.textContent = copy.dismiss || '';
    dismissBtn.hidden = !copy.dismiss;
  }
}

// Wire the modal once: the tabs, the switcher, the eye, the close button and
// the form.
export function initAuthModal() {
  const { modal, signInTab, registerTab, switchBtn, dismissBtn, eyeBtn, form, password, reqs } = authModalEls();
  if (!modal) return;
  signInTab?.addEventListener('click', () => {
    applyAuthModalMode('signin');
    setAuthModalStatus('');
  });
  registerTab?.addEventListener('click', () => {
    applyAuthModalMode('register');
    setAuthModalStatus('');
  });
  switchBtn?.addEventListener('click', () => {
    applyAuthModalMode(authModalMode === 'signin' ? 'register' : 'signin');
    setAuthModalStatus('');
  });
  dismissBtn?.addEventListener('click', closeAuthModal);
  document.getElementById('authModalCloseBtn')?.addEventListener('click', closeAuthModal);
  // Clicking the backdrop is a way out too.
  modal.addEventListener('click', (e) => {
    if (e.target === modal) closeAuthModal();
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && !modal.hidden) closeAuthModal();
  });
  eyeBtn?.addEventListener('click', () => {
    if (!password) return;
    const shown = password.type === 'text';
    password.type = shown ? 'password' : 'text';
    eyeBtn.setAttribute('aria-label', shown ? 'Toggle password visibility' : 'Hide password');
  });
  password?.addEventListener('input', () => {
    renderPasswordReqs(reqs, password.value);
  });
  form?.addEventListener('submit', (e) => {
    e.preventDefault();
    submitAuthModal();
  });
  applyAuthModalMode('signin');
  applyAuthModalReason('sidebar_profile');
}

// Open the modal: the sidebar login and the lessons gateway both land here.
export function openAuthModal({ mode = 'signin', reason = 'default' } = {}) {
  const { modal, email, password, reqs } = authModalEls();
  if (!modal) return;
  authModalReturnFocus = document.activeElement;
  applyAuthModalReason(reason);
  applyAuthModalMode(mode);
  setAuthModalStatus('');
  if (password) {
    password.value = '';
    password.type = 'password';
  }
  renderPasswordReqs(reqs, '');
  modal.hidden = false;
  // The fade-in needs the dialog on screen before it brightens.
  window.setTimeout(() => {
    if (!modal.hidden) modal.classList.add('is-open');
  }, 10);
  email?.focus({ preventScroll: true });
}

// Close the modal and hand the workspace back.
export function closeAuthModal() {
  const { modal } = authModalEls();
  if (!modal) return;
  modal.classList.remove('is-open');
  setAuthModalStatus('');
  // The fade-out runs first; the dialog leaves the screen after it.
  window.setTimeout(() => {
    if (modal.classList.contains('is-open')) return;
    modal.hidden = true;
    // The focus goes back where it came from.
    const back = authModalReturnFocus;
    authModalReturnFocus = null;
    if (back && typeof back.focus === 'function' && document.contains(back)) {
      back.focus({ preventScroll: true });
    }
  }, 200);
}

// Create the account (or sign in), migrate the guest progress and hand the
// session over to the app.
async function submitAuthModal() {
  const { email, password, submit } = authModalEls();
  const address = email?.value?.trim();
  const secret = password?.value;
  if (!address || !secret) {
    setAuthModalStatus('Enter an email and a password.', true);
    return;
  }
  if (submit) submit.disabled = true;
  try {
    setAuthModalStatus(authModalMode === 'register' ? 'Creating your account…' : 'Signing in…');
    const clerk = await loadClerk();
    if (authModalMode === 'register') {
      // The same rules the login page enforces: the learner is told exactly
      // what is missing instead of getting a generic rejection.
      const missing = passwordIssues(secret);
      if (missing.length) {
        setAuthModalStatus(`Password needs: ${missing.join('; ')}.`, true);
        return;
      }
      const signUp = await clerk.client.signUp.create({ emailAddress: address, password: secret });
      if (signUp.status !== 'complete') {
        const required = new Set(signUp.requiredFields || []);
        const missingFields = new Set(signUp.missingFields || []);
        const emailVerification = signUp.verifications?.email_address;
        if (required.has('password_requirements') || missingFields.has('password_requirements')) {
          const still = passwordIssues(secret);
          setAuthModalStatus(still.length
            ? `Password needs: ${still.join('; ')}.`
            : 'The password does not meet the registration requirements.', true);
          return;
        }
        if (emailVerification && emailVerification.status === 'unverified') {
          setAuthModalStatus('Email confirmation is required to finish the registration.', true);
          return;
        }
        setAuthModalStatus(`Registration is not complete (status: ${signUp.status}).`, true);
        return;
      }
      await clerk.setActive({ session: signUp.createdSessionId });
    } else {
      const signIn = await clerk.client.signIn.create({ identifier: address, password: secret });
      if (signIn.status !== 'complete') {
        setAuthModalStatus(`Sign-in is not complete (status: ${signIn.status}).`, true);
        return;
      }
      await clerk.setActive({ session: signIn.createdSessionId });
    }
    // The account exists: the guest's progress follows them onto it.
    await migrateGuestProgress();
    closeAuthModal();
    setAuthState({ authenticated: true, user: clerk.user });
  } catch (err) {
    setAuthModalStatus(isAlreadySignedInError(err) ? ALREADY_SIGNED_IN_HELP : formatClerkError(err), true);
  } finally {
    if (submit) submit.disabled = false;
  }
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

// Is the current session an account session? A signed-out app has no session
// at all, and Clerk marks an anonymous session explicitly — neither may use
// the account-only features.
export function isAccountSession(clerkInstance) {
  const clerk = clerkInstance || window.Clerk;
  const session = clerk?.session;
  if (!session) return false;
  if (session.is_anonymous) return false;
  return Boolean(clerk?.user?.id);
}

// The signed-in learner's email address. Clerk keeps the addresses in a list
// and marks one of them primary; an account without a verified address
// simply has none.
export function currentUserEmail(clerkInstance) {
  const clerk = clerkInstance || window.Clerk;
  const user = clerk?.user;
  if (!user) return '';
  const addresses = user.emailAddresses || [];
  const primary = addresses.find((a) => a.id === user.primaryEmailAddressId) || addresses[0];
  return primary?.emailAddress || user.email || '';
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

// The password checklist, rendered live under the field: what is met, what is
// missing, and what is merely recommended.
function renderPasswordReqs(reqsEl, value) {
  if (!reqsEl) return;
  const password = value || '';
  reqsEl.innerHTML = '';
  PASSWORD_RULES.forEach((rule) => {
    const ok = rule.test(password);
    const row = document.createElement('span');
    row.className = `pw-req${ok ? ' ok' : rule.required ? ' missing' : ' soft'}`;
    row.textContent = `${ok ? '\u2713' : '\u2022'} ${rule.label}`;
    reqsEl.appendChild(row);
  });
  reqsEl.hidden = !password;
}

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
    renderPasswordReqs(document.querySelector(reqsId), passwordInput.value || '');
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

// Redirect if a session already exists
(async () => {
  try {
    const clerk = await loadClerk();
    if (clerk.session && window.location.pathname.endsWith('login.html')) {
      window.location.href = '/index.html';
    }
  } catch (err) {
    const statusMsg = document.querySelector('#authStatus');
    if (statusMsg) {
      statusMsg.className = 'msg err';
      statusMsg.textContent = formatClerkError(err);
    } else {
      setAuthModalStatus(formatClerkError(err), true);
    }
  }
})();