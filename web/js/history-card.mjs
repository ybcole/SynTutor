import { forDisplay } from './history-status.mjs';

export function createHistoryCard(
  entry,
  { onOpen = () => {}, onDelete = () => {} } = {}
) {
  if (!entry || typeof entry.sentence !== 'string') {
    throw new TypeError('Invalid history entry');
  }

  const display = forDisplay(entry);

  const card = document.createElement('div');
  card.className =
    `history-item is-${display.status.replaceAll('_', '-')}`;

  card.setAttribute('role', 'button');
  card.setAttribute('tabindex', '0');
  card.title = entry.sentence;
  card.setAttribute(
    'aria-label',
    `${entry.sentence} — ${display.label}`
  );

  const title = document.createElement('p');
  title.className = 'hist-title hist-sentence';
  title.textContent = entry.sentence;

  const status = document.createElement('p');
  status.className = 'hist-status';
  status.textContent = display.label;

  const textBlock = document.createElement('div');
  textBlock.className = 'hist-head';
  textBlock.append(title, status);

  const deleteButton = document.createElement('button');
  deleteButton.type = 'button';
  deleteButton.title = 'Delete entry';
  deleteButton.className = 'hist-delete-btn';
  deleteButton.setAttribute('aria-label', 'Delete history entry');

  deleteButton.innerHTML = `
    <svg viewBox="0 0 24 24" width="15" height="15"
         fill="none" stroke="currentColor" stroke-width="2"
         stroke-linecap="round" stroke-linejoin="round">
      <polyline points="3 6 5 6 21 6"></polyline>
      <path d="M19 6v14a2 2 0 0 2 2H7a2 2 0 0 1-2-2V6
               m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
    </svg>
  `;

  card.append(textBlock, deleteButton);

  card.addEventListener('click', () => onOpen(entry));

  card.addEventListener('keydown', (event) => {
    if (event.target !== card) return;

    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      onOpen(entry);
    }
  });

  deleteButton.addEventListener('click', (event) => {
    event.stopPropagation();
    onDelete(entry, deleteButton);
  });

  return card;
}
