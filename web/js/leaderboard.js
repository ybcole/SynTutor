const MEDAL_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="14" r="6"></circle><path d="m8.5 9.5-2-7h4l1.5 4 1.5-4h4l-2 7"></path></svg>';

const PODIUM_PLACES = [
  { rank: 1, tag: 'Top Learner' },
  { rank: 2, tag: 'Second Place' },
  { rank: 3, tag: 'Third Place' },
];

function node(tag, className, text) {
  const el = document.createElement(tag);
  if (className) el.className = className;
  if (text !== undefined) el.textContent = text;
  return el;
}

function buildPodiumCard(item, place) {
  const card = node('article', `podium-card is-${place.rank}`);
  const top = node('div', 'podium-card-top');
  const avatar = node('span', 'podium-avatar', (item.alias || 'L').charAt(0).toUpperCase());
  avatar.appendChild(node('span', 'podium-rank', String(place.rank)));
  top.appendChild(avatar);

  const identity = node('div', 'podium-identity');
  identity.appendChild(node('span', 'podium-name', item.alias));
  identity.appendChild(node('span', 'podium-handle', `Rank #${item.rank}`));
  top.appendChild(identity);

  const medal = node('span', 'podium-medal');
  medal.innerHTML = MEDAL_SVG;
  top.appendChild(medal);
  card.appendChild(top);

  const stats = node('div', 'podium-stats');
  const addStat = (value, label) => {
    const box = node('div', 'podium-stat');
    box.appendChild(node('span', 'podium-stat-value', value));
    box.appendChild(node('span', 'podium-stat-label', label));
    stats.appendChild(box);
  };
  addStat(Number(item.lessons_completed || 0).toLocaleString(), 'Lessons');
  addStat(Number(item.quizzes_completed || 0).toLocaleString(), 'Quizzes');
  addStat(Number(item.xp || 0).toLocaleString(), 'Period XP');
  card.appendChild(stats);

  card.appendChild(node('span', 'podium-tag', place.tag));
  return card;
}

function buildOpenPodiumCard(place) {
  const card = node('article', 'podium-card is-open');
  const medal = node('span', 'podium-open-medal');
  medal.innerHTML = MEDAL_SVG;
  card.appendChild(medal);
  card.appendChild(node('span', 'podium-open-rank', `#${place.rank} Open`));
  card.appendChild(node('span', 'podium-open-hint', 'Open rank'));
  return card;
}

function randomHexSuffix(bytesCount = 3) {
  const bytes = new Uint8Array(bytesCount);
  globalThis.crypto?.getRandomValues?.(bytes);
  return Array.from(bytes, b => b.toString(16).padStart(2, '0')).join('').toUpperCase()
    || String(Math.floor(100000 + Math.random() * 900000)).slice(0, bytesCount * 2);
}

function randomNickname() {
  return `Learner_${randomHexSuffix(3)}`;
}

function isGeneratedFallbackAlias(value) {
  return /^Learner_[A-F0-9]{6}$/.test(value || '');
}

function withShortSuffix(base) {
  const trimmed = String(base || '').replace(/[_-]+$/, '').slice(0, 19);
  return `${trimmed}_${randomHexSuffix(2)}`;
}

export function createLeaderboardView(root, {
  settingsRoot = null,
  client,
  account,
  beforeLoad = null,
  suggestedAlias = null,
}) {
  const byId = id => root.querySelector(`#leaderboard${id}`);
  const settingsEl = id => (settingsRoot || document).querySelector(`#leaderboard${id}`);
  const period = byId('Period');
  const statusRow = byId('StatusRow');
  const status = byId('Status');
  const retry = byId('Retry');
  const podium = byId('Podium');
  const entries = byId('Entries');
  const standings = byId('Standings');

  const form = settingsEl('Consent');
  const alias = settingsEl('Alias');
  const randomBtn = settingsEl('RandomAlias');
  const suggestionBox = settingsEl('AliasSuggestion');
  const suggestionCopy = settingsEl('AliasSuggestionCopy');
  const adoptBtn = settingsEl('AdoptEmailAlias');
  const join = settingsEl('Join');
  const leave = settingsEl('Leave');
  const notice = settingsEl('PreferenceStatus');
  const privacyCopy = settingsEl('PrivacyCopy');
  const closeBtn = settingsEl('SettingsCloseBtn');

  let currentSuggested = null;

  let generation = 0;
  let open = false;
  let settingsOpen = false;
  let saving = false;
  let returnFocus = null;

  async function rpc(name, args) {
    const db = client();
    if (!db) throw Error('Unavailable');
    const { data, error } = await db.rpc(name, args).abortSignal(AbortSignal.timeout(6000));
    if (error) throw error;
    return data;
  }

  function applySettingsData(data) {
    if (!form || !alias || !join || !leave) return;
    alias.value = data.my_alias || '';
    const active = Boolean(data.opted_in);
    leave.hidden = !active;
    join.textContent = active ? 'Save public alias' : 'Resume public rankings';
    if (privacyCopy) {
      privacyCopy.textContent = active
        ? 'Your public alias (initially suggested from the part of your email before @ or generated safely) is visible on the Leaderboard. Full emails are never shown.'
        : 'You opted out of public rankings. Your verified progress stays private, and you can choose any public nickname to resume.';
    }
    const candidate = typeof suggestedAlias === 'function' ? suggestedAlias() : null;
    const canAdopt = Boolean(candidate && isGeneratedFallbackAlias(data.my_alias) && candidate !== data.my_alias);
    currentSuggested = canAdopt ? candidate : null;
    if (suggestionBox && suggestionCopy && adoptBtn) {
      suggestionBox.hidden = !canAdopt;
      if (canAdopt) {
        suggestionCopy.textContent = `Adopt "${candidate}" (from your verified email before @)? Adopting this will publish "${candidate}" on rankings instead of "${data.my_alias}". Full emails and domains remain private.`;
        adoptBtn.textContent = `Adopt "${candidate}"`;
      }
    }
  }

  async function loadSettings() {
    const signedIn = account();
    if (!signedIn || !settingsRoot) return;
    if (notice) notice.textContent = '';
    try {
      await beforeLoad?.();
      const data = await rpc('get_leaderboard', { p_period: period?.value || 'weekly' });
      if (settingsOpen && signedIn === account() && data) applySettingsData(data);
    } catch {
      if (notice && settingsOpen) notice.textContent = 'Could not load current Leaderboard settings.';
    }
  }

  function openSettings() {
    if (!settingsRoot || !account()) return;
    returnFocus = document.activeElement;
    settingsOpen = true;
    settingsRoot.hidden = false;
    window.setTimeout(() => {
      if (!settingsRoot.hidden) settingsRoot.classList.add('is-open');
    }, 10);
    alias?.focus({ preventScroll: true });
    loadSettings();
  }

  function closeSettings() {
    if (!settingsRoot || settingsRoot.hidden) return;
    settingsOpen = false;
    settingsRoot.classList.remove('is-open');
    if (notice) notice.textContent = '';
    window.setTimeout(() => {
      if (settingsRoot.classList.contains('is-open')) return;
      settingsRoot.hidden = true;
      const back = returnFocus;
      returnFocus = null;
      if (back && typeof back.focus === 'function' && document.contains(back)) {
        back.focus({ preventScroll: true });
      }
    }, 180);
  }

  async function refresh() {
    const id = ++generation;
    const signedIn = account();
    const selected = period.value;
    if (statusRow) statusRow.hidden = false;
    if (status) status.textContent = 'Loading rankings…';
    if (retry) retry.hidden = true;
    podium.hidden = true;
    podium.replaceChildren();
    standings.hidden = true;
    entries.replaceChildren();
    let data = null;
    try {
      if (signedIn) await beforeLoad?.();
      data = await rpc('get_leaderboard', { p_period: selected });
    } catch (error) {
      if (!open || id !== generation || signedIn !== account()) return;
      if (statusRow) statusRow.hidden = false;
      if (status) {
        status.textContent = error?.code === 'PGRST202'
          ? 'Public rankings are paused.'
          : 'Rankings are currently unavailable.';
      }
      if (retry) retry.hidden = false;
      return;
    }
    if (!open || id !== generation || signedIn !== account()) return;
    if (!data || !data.enabled) {
      if (statusRow) statusRow.hidden = false;
      if (status) status.textContent = 'Public rankings are paused.';
      return;
    }

    if (signedIn && settingsOpen) applySettingsData(data);

    if (!data.entries.length) {
      if (statusRow) statusRow.hidden = false;
      if (status) status.textContent = 'No learners ranked yet.';
      return;
    }

    if (statusRow) statusRow.hidden = true;
    podium.hidden = false;
    for (const place of PODIUM_PLACES) {
      const entry = data.entries[place.rank - 1];
      podium.appendChild(entry ? buildPodiumCard(entry, place) : buildOpenPodiumCard(place));
    }

    for (const item of data.entries) {
      const isMine = Boolean(data.my_alias && item.alias === data.my_alias);
      const row = node('tr', isMine ? 'current-user' : '');
      row.appendChild(node('td', 'standings-rank', `#${item.rank}`));

      const learnerCell = document.createElement('td');
      const wrap = node('div', 'standings-learner');
      wrap.appendChild(node('span', 'standings-avatar', (item.alias || 'L').charAt(0).toUpperCase()));
      const meta = node('div', 'standings-learner-meta');
      meta.appendChild(node('span', 'standings-learner-name', item.alias));
      wrap.appendChild(meta);
      learnerCell.appendChild(wrap);
      row.appendChild(learnerCell);

      row.appendChild(node('td', 'num standings-value', Number(item.lessons_completed || 0).toLocaleString()));
      row.appendChild(node('td', 'num standings-value', Number(item.quizzes_completed || 0).toLocaleString()));
      row.appendChild(node('td', 'num standings-value', Number(item.xp || 0).toLocaleString()));
      entries.appendChild(row);
    }
    standings.hidden = false;
  }

  async function save(optIn, { allowSuffixFallback = false } = {}) {
    const signedIn = account();
    if (saving || !signedIn || !join || !leave || !alias || !notice) return;
    saving = true;
    join.disabled = leave.disabled = true;
    if (adoptBtn) adoptBtn.disabled = true;
    notice.textContent = 'Saving…';
    try {
      const requested = optIn ? alias.value : null;
      let chosen = requested;
      for (let attempt = 0; attempt < (allowSuffixFallback ? 5 : 1); attempt += 1) {
        try {
          await rpc('set_my_leaderboard_preference', { p_alias: chosen, p_opt_in: optIn });
          break;
        } catch (err) {
          if (err?.code === '23505' && optIn && allowSuffixFallback && attempt < 4) {
            chosen = withShortSuffix(requested);
            alias.value = chosen;
            continue;
          }
          throw err;
        }
      }
      if (signedIn === account()) {
        notice.textContent = optIn ? 'Public participation and alias saved.' : 'You opted out of public rankings.';
        const data = await rpc('get_leaderboard', { p_period: period?.value || 'weekly' });
        if (data && settingsOpen) applySettingsData(data);
        if (open) await refresh();
      }
    } catch (error) {
      if (signedIn === account()) {
        notice.textContent = error.code === '23505' ? 'That alias is already in use.'
          : error.code === '22023' ? 'Choose a different alias using the format above.'
            : 'Could not save settings. Please try again.';
      }
    } finally {
      saving = false;
      join.disabled = leave.disabled = false;
      if (adoptBtn) adoptBtn.disabled = false;
    }
  }

  form?.addEventListener('submit', event => { event.preventDefault(); save(true); });
  adoptBtn?.addEventListener('click', () => {
    if (!alias || !currentSuggested) return;
    alias.value = currentSuggested;
    save(true, { allowSuffixFallback: true });
  });
  randomBtn?.addEventListener('click', () => {
    if (!alias) return;
    alias.value = randomNickname();
    alias.focus();
  });
  leave?.addEventListener('click', () => save(false));
  closeBtn?.addEventListener('click', closeSettings);
  settingsRoot?.addEventListener('click', event => {
    if (event.target === settingsRoot) closeSettings();
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && settingsRoot && !settingsRoot.hidden) {
      event.stopImmediatePropagation();
      closeSettings();
    }
  });
  period?.addEventListener('change', refresh);
  retry?.addEventListener('click', refresh);
  return {
    open() { open = true; refresh(); },
    close() { open = false; generation += 1; },
    openSettings,
    closeSettings,
  };
}
