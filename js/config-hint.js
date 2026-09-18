// Dev-experience hook: js/config.js is git-ignored (see .gitignore), so a
// fresh checkout loads the page without it and the ES-module import of
// ./config.js fails with a cryptic link error before any module code can print
// a useful message. Warn with the concrete fix instead. Load this classic
// script on every page, before the entry <script type="module"> tag.
fetch('js/config.js', { method: 'GET' })
  .then((res) => {
    if (res.status === 404) {
      console.warn('SynTutor setup: js/config.js is missing. Copy js/config.example.js to js/config.js and add your Clerk + Supabase keys (see docs/README.md).');
    }
  })
  .catch(() => {});