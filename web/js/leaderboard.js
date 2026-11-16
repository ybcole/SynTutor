const date = new Intl.DateTimeFormat(undefined, { dateStyle: 'medium', timeZone: 'UTC' });

const MEDAL_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="14" r="6"></circle><path d="m8.5 9.5-2-7h4l1.5 4 1.5-4h4l-2 7"></path></svg>';

const PODIUM_PLACES = [
  { rank: 1, place: '1st', tag: '⭐ Top Contributor' },
  { rank: 2, place: '2nd', tag: '🥈 Runner Up' },
  { rank: 3, place: '3rd', tag: '🥉 Third Place' },
];

function node(tag, className, text) {
  const el = document.createElement(tag);
  if (className) el.className = className;
  if (text !== undefined) el.textContent = text;
  return el;
}

function buildPodiumCard(item, place, isMine) {
  const card = node('article', `podium-card is-${place.rank}`);
  const top = node('div', 'podium-card-top');
  const avatar = node('span', 'podium-avatar', (item.alias || 'L').charAt(0).toUpperCase());
  avatar.appendChild(node('span', 'podium-rank', String(place.rank)));
  top.appendChild(avatar);

  const identity = node('div', 'podium-identity');
  identity.appendChild(node('span', 'podium-name', item.alias));
  identity.appendChild(node('span', 'podium-handle', isMine ? `Your alias · #${item.rank}` : `Rank #${item.rank}`));
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
  addStat(`#${item.rank}`, 'Standing');
  addStat(Number(item.xp || 0).toLocaleString(), 'Period XP');
  addStat(isMine ? 'You' : 'Opted in', 'Status');
  card.appendChild(stats);

  card.appendChild(node('span', 'podium-tag', place.tag));
  return card;
}

function buildOpenPodiumCard(place) {
  const card = node('article', 'podium-card is-open');
  const medal = node('span', 'podium-open-medal');
  medal.innerHTML = MEDAL_SVG;
  card.appendChild(medal);
  card.appendChild(node('span', 'podium-open-rank', `#${place.rank} Open Rank`));
  card.appendChild(node('span', 'podium-open-hint', `Earn verified XP to claim ${place.place} place`));
  return card;
}

export function createLeaderboardView(root, { client, account, lifetime }) {
  const byId = id => root.querySelector(`#leaderboard${id}`);
  const period = byId('Period');
  const status = byId('Status');
  const rank = byId('Rank');
  const podium = byId('Podium');
  const entries = byId('Entries');
  const standings = byId('Standings');
  const form = byId('Consent');
  const alias = byId('Alias');
  const join = byId('Join');
  const leave = byId('Leave');
  const notice = byId('PreferenceStatus');
  const privateProgress = byId('Lifetime');
  let generation = 0;
  let open = false;
  let saving = false;

  async function rpc(name, args) {
    const db = client();
    if (!db) throw Error('Unavailable');
    const { data, error } = await db.rpc(name, args).abortSignal(AbortSignal.timeout(6000));
    if (error) throw error;
    return data;
  }

  async function refresh() {
    const id = ++generation;
    const signedIn = account();
    const selected = period.value;
    status.textContent = 'Loading rankings…';
    rank.textContent = '';
    rank.hidden = true;
    privateProgress.textContent = signedIn ? 'Loading private lifetime XP…' : 'Sign in to see your private lifetime XP.';
    podium.hidden = true;
    podium.replaceChildren();
    standings.hidden = true;
    entries.replaceChildren();
    form.hidden = true;
    leave.hidden = true;
    const [board, totals] = await Promise.allSettled([
      rpc('get_leaderboard', { p_period: selected }),
      signedIn ? lifetime() : null,
    ]);
    if (!open || id !== generation || signedIn !== account()) return;
    if (signedIn) {
      const stats = totals.value;
      privateProgress.textContent = stats
        ? `Private lifetime progress · Level ${stats.level} · ${stats.xp} verified XP`
        : 'Private lifetime XP is unavailable.';
    }
    if (board.status !== 'fulfilled' || !board.value) {
      status.textContent = board.reason?.code === 'PGRST202'
        ? 'Public rankings are paused.'
        : 'Rankings are unavailable. Reopen this view to retry.';
      return;
    }
    const data = board.value;
    leave.hidden = !(signedIn && data.opted_in);
    if (!data.enabled) {
      status.textContent = 'Public rankings are paused.';
      return;
    }
    const dates = `${date.format(new Date(data.period_start))} to ${date.format(new Date(data.period_end))} (UTC, end exclusive)`;
    status.textContent = data.entries.length ? dates : `No verified XP ranked yet. ${dates}`;
    if (signedIn) {
      form.hidden = false;
      alias.value = data.my_alias || '';
      join.textContent = data.opted_in ? 'Update public alias' : 'Join public rankings';
      rank.textContent = data.my_rank ? `Your rank · #${data.my_rank}`
        : data.opted_in ? 'Your rank will appear after you earn qualifying XP.' : 'Your participation is private.';
    } else {
      rank.textContent = 'Sign in to choose whether to join.';
    }
    rank.hidden = !rank.textContent;

    if (data.entries.length) {
      podium.hidden = false;
      for (const place of PODIUM_PLACES) {
        const entry = data.entries[place.rank - 1];
        podium.appendChild(entry
          ? buildPodiumCard(entry, place, Boolean(data.my_alias && entry.alias === data.my_alias))
          : buildOpenPodiumCard(place));
      }
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
      if (isMine) meta.appendChild(node('span', 'standings-learner-handle', 'Your public alias'));
      wrap.appendChild(meta);
      learnerCell.appendChild(wrap);
      row.appendChild(learnerCell);

      row.appendChild(node('td', 'num standings-value', Number(item.xp || 0).toLocaleString()));
      entries.appendChild(row);
    }
    standings.hidden = !data.entries.length;
  }

  async function save(optIn) {
    const signedIn = account();
    if (saving || !signedIn) return;
    saving = true;
    join.disabled = leave.disabled = true;
    notice.textContent = 'Saving participation…';
    try {
      await rpc('set_my_leaderboard_preference', { p_alias: optIn ? alias.value : null, p_opt_in: optIn });
      if (open && signedIn === account()) {
        notice.textContent = optIn ? 'Public participation saved.' : 'You left public rankings.';
        await refresh();
      }
    } catch (error) {
      if (open && signedIn === account()) {
        notice.textContent = error.code === '23505' ? 'That alias is already in use.'
          : error.code === '22023' ? 'Choose a different alias using the format above.'
            : 'Could not save participation. Please try again.';
      }
    } finally {
      saving = false;
      join.disabled = leave.disabled = false;
    }
  }

  form.addEventListener('submit', event => { event.preventDefault(); save(true); });
  leave.addEventListener('click', () => save(false));
  period.addEventListener('change', refresh);
  return {
    open() { open = true; notice.textContent = ''; refresh(); },
    close() { open = false; generation += 1; },
  };
}
