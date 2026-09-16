import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';
import { SUPABASE_CONFIG } from './config.js';

if (!SUPABASE_CONFIG.url || !SUPABASE_CONFIG.anonKey || SUPABASE_CONFIG.anonKey.includes('YOUR_')) {
  console.error('Supabase configuration is missing or invalid. Check js/config.js.');
}

export const supabase = createClient(SUPABASE_CONFIG.url, SUPABASE_CONFIG.anonKey);

const form = document.querySelector('#loginForm');
const emailInput = document.querySelector('#email');
const passwordInput = document.querySelector('#password');
const signUpBtn = document.querySelector('#signUpBtn');
const statusMsg = document.querySelector('#authStatus');

function setStatus(text, isError = false) {
  if (!statusMsg) return;
  statusMsg.textContent = text;
  statusMsg.className = `msg ${isError ? 'err' : 'ok'}`;
}

// Redirect if session already exists
const { data: { session } } = await supabase.auth.getSession();
if (session && window.location.pathname.endsWith('login.html')) {
  window.location.href = '/index.html';
}

form?.addEventListener('submit', async (e) => {
  e.preventDefault();
  setStatus('Signing in...');

  const { error } = await supabase.auth.signInWithPassword({
    email: emailInput.value.trim(),
    password: passwordInput.value,
  });

  if (error) {
    setStatus(error.message, true);
  } else {
    window.location.href = '/index.html';
  }
});

signUpBtn?.addEventListener('click', async () => {
  const email = emailInput.value.trim();
  const password = passwordInput.value;

  if (!email || !password) {
    setStatus('Enter an email and password to register.', true);
    return;
  }

  setStatus('Registering account...');
  const { data, error } = await supabase.auth.signUp({ email, password });

  if (error) {
    setStatus(error.message, true);
  } else if (data.user && !data.session) {
    setStatus('Account registered! Check your email to confirm.', false);
  } else {
    window.location.href = '/index.html';
  }
});