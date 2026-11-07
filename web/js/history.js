// Analysis history — an account-only feature.
//
// One rule runs through the whole feature: a guest session has no history.
// The rail item is hidden, the drawer cannot be opened, and a parsed sentence
// is never recorded — so an anonymous query stays ephemeral and never leaks
// into the next session. An account session gets all three.

const GUEST_CLASS = 'is-guest-hidden';

// Whether the current session may use the history.
let enabled = false;

// The workspace hooks: loading the entries, taking the rail highlight, and
// giving it back.
const hooks = {
  onOpen: () => {},
  onOverlay: () => {},
  onClose: () => {},
};

const historyButton = () => document.querySelector('#headerHistoryBtn');
const drawerBackdrop = () => document.querySelector('#historyDrawerBackdrop');

// Wire the feature to the workspace.
export function initHistory(options = {}) {
  Object.assign(hooks, options);
  applyVisibility();
  document.querySelector('#closeDrawerBtn')?.addEventListener('click', closeHistoryDrawer);
  drawerBackdrop()?.addEventListener('click', (e) => {
    if (e.target === drawerBackdrop()) closeHistoryDrawer();
  });
}

// The auth state changed: an account session gets the feature, a guest does
// not — and a guest who signs out mid-session drops an open drawer.
export function setHistoryEnabled(value) {
  const next = Boolean(value);
  if (next === enabled) return;
  enabled = next;
  applyVisibility();
  if (!enabled) closeHistoryDrawer();
}

// The rail item is hidden outright for a guest, so the column closes up
// without a gap or a ghost border where it used to sit.
function applyVisibility() {
  const btn = historyButton();
  if (!btn) return;
  btn.classList.toggle(GUEST_CLASS, !enabled);
  btn.hidden = !enabled;
}

// The access guard: a guest never gets the drawer, however it is reached.
export function openHistoryDrawer() {
  if (!enabled) return false;
  hooks.onOpen?.();
  drawerBackdrop()?.classList.add('active');
  hooks.onOverlay?.('history');
  return true;
}

// Close the drawer and hand the rail highlight back to the module underneath.
export function closeHistoryDrawer() {
  const wasOpen = Boolean(drawerBackdrop()?.classList.contains('active'));
  drawerBackdrop()?.classList.remove('active');
  if (wasOpen) hooks.onClose?.();
}

// The persistence gate: a guest session records nothing.
export function shouldPersistHistory({ isNavigation = false, text = '', recorded = null } = {}) {
  if (!enabled) return false;
  if (isNavigation) return false;
  if (recorded && recorded.has(text)) return false;
  return true;
}
