// Account-bound requests may outlive a workspace or a token refresh.
export function accountUserId(clerk) {
  return clerk?.session?.id && !clerk.session.is_anonymous ? clerk.user?.id || null : null;
}

export function bindSessionToken(clerk) {
  const userId = accountUserId(clerk);
  if (!userId) return async () => null;
  const sessionId = clerk.session.id;
  const assertCurrent = () => {
    if (accountUserId(clerk) !== userId || clerk.session.id !== sessionId) {
      throw new Error('The account session changed. Reopen this view to sync.');
    }
  };
  return async () => {
    assertCurrent();
    const token = await clerk.session.getToken();
    assertCurrent();
    if (!token) throw new Error('The account token is unavailable.');
    return token;
  };
}
