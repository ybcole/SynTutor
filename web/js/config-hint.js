// Warn before the app module imports a missing environment configuration.
fetch('js/config.js', { method: 'GET' })
  .then((res) => {
    if (res.status === 404) {
      console.warn('SynTutor setup: js/config.js is missing. Copy js/config.example.js to js/config.js and add your Clerk + Supabase keys (see docs/README.md).');
    }
  })
  .catch(() => {});
