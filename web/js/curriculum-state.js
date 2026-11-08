// Shared loading and recovery surface for the two reviewed content catalogs.
export function showCurriculumState(host, { title, message, retry, back }) {
  host.setAttribute('aria-busy', String(!retry));
  if (!retry) {
    const status = document.createElement('p');
    status.setAttribute('role', 'status');
    status.textContent = message;
    host.replaceChildren(status);
    return;
  }
  const heading = document.createElement('h1');
  heading.textContent = title;
  heading.tabIndex = -1;
  const description = document.createElement('p');
  description.textContent = message;
  const controls = document.createElement('div');
  controls.className = 'curriculum-recovery-actions';
  for (const [label, action] of [['Try again', retry], ['Back to Syntax Generator', back]]) {
    if (!action) continue;
    const button = document.createElement('button');
    button.type = 'button';
    button.textContent = label;
    button.addEventListener('click', action);
    controls.append(button);
  }
  host.replaceChildren(heading, description, controls);
  heading.focus({ preventScroll: true });
}
