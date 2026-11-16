// Derive a safe, readable public alias from the portion before '@' across any
// email domain, stripping accents/punctuation and never exposing the domain.
export function deriveLeaderboardAlias(email) {
  if (typeof email !== 'string') return null;
  const trimmed = email.trim();
  const at = trimmed.indexOf('@');
  if (at <= 0 || at === trimmed.length - 1 || !trimmed.slice(at + 1).includes('.')) return null;
  let local = trimmed.slice(0, at)
    .normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^A-Za-z0-9_-]+/g, '_')
    .replace(/_+/g, '_')
    .replace(/^[^A-Za-z]+/, '')
    .replace(/[_-]+$/, '');
  local = local.slice(0, 24).replace(/[_-]+$/, '');
  if (local.length < 3 || !/^[A-Za-z][A-Za-z0-9_-]{2,23}$/.test(local)) return null;
  if (/^(user|sess|org|client|clerk)[_-]/i.test(local)) return null;
  return local;
}
