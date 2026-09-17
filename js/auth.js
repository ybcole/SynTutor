import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';
import { SUPABASE_CONFIG } from './config.js';

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

if (form) {
  const { data: { session } } = await supabase.auth.getSession();
  if (session && window.location.pathname.endsWith('login.html')) window.location.href = '/index.html';

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    setStatus('Signing in...');
    const { error } = await supabase.auth.signInWithPassword({
      email: emailInput.value.trim(), password: passwordInput.value,
    });
    if (error) setStatus(error.message, true);
    else window.location.href = '/index.html';
  });

  signUpBtn?.addEventListener('click', async () => {
    setStatus('Registering account...');
    const { data, error } = await supabase.auth.signUp({
      email: emailInput.value.trim(), password: passwordInput.value,
    });
    if (error) setStatus(error.message, true);
    else if (data.user && !data.session) setStatus('Account registered! Check your email to confirm.');
    else window.location.href = '/index.html';
  });
}
