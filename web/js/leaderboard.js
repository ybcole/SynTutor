const date = new Intl.DateTimeFormat(undefined, { dateStyle: 'medium', timeZone: 'UTC' });

export function createLeaderboardView(root, { client, account, lifetime }) {
  const byId = id => root.querySelector(`#leaderboard${id}`);
  const period = byId('Period');
  const status = byId('Status');
  const rank = byId('Rank');
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
    privateProgress.textContent = signedIn ? 'Loading private lifetime XP…' : 'Sign in to see your private lifetime XP.';
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
    for (const item of data.entries) {
      const row = document.createElement('tr');
      for (const value of [`#${item.rank}`, item.alias, item.xp]) {
        const cell = document.createElement('td');
        cell.textContent = value;
        row.appendChild(cell);
      }
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
