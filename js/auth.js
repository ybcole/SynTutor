import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';

const SUPABASE_URL = 'https://bgjzmnqqeqfcttjpotwg.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJnanptbnFxZXFmY3R0anBvdHdnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODk1MTMyODAsImV4cCI6MjEwNTA4OTI4MH0.d_fE0I28hvc5C9ZkJAAdzXzsMTXmQGSthYuiCoYj_rc';

export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

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

// Redirect if already logged in
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
    setStatus('Account registered! Check your email inbox to confirm.', false);
  } else {
    window.location.href = '/index.html';
  }
});