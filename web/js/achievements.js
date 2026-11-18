// The category the achievements grid is currently showing.
let activeCategory = 'all';
// Whoever re-renders the grid when the category changes.
let filterListener = null;
let filterDelegateBound = false;

export function activeAchievementCategory() {
  return activeCategory;
}

// Compact single-row category filter bar for achievements.
// Listeners live on the document so re-renders never detach filter state.
export function initAchievementCategorySelector(onChange) {
  filterListener = typeof onChange === 'function' ? onChange : null;
  if (filterDelegateBound) return;
  filterDelegateBound = true;

  document.addEventListener('click', (e) => {
    const pill = e.target.closest('.cat-pill[data-category]');
    if (!pill || !pill.closest('#achievementsCatExpander')) return;
    const category = pill.getAttribute('data-category');
    const wrapper = pill.closest('#achievementsCatExpander');
    wrapper.querySelectorAll('.cat-pill').forEach((other) => {
      const selected = other === pill;
      other.classList.toggle('active', selected);
      other.setAttribute('aria-pressed', String(selected));
    });
    activeCategory = category;
    filterListener?.(category);
  });
}

// The badge icons, as inline SVG paths (24×24, stroke based).
export const achievementIcons = {
  tree: '<circle cx="12" cy="5" r="2.4"/><circle cx="6" cy="18" r="2.4"/><circle cx="18" cy="18" r="2.4"/><path d="M12 7.4v3.2M10.6 10.6 7.6 16M13.4 10.6l3 5.4"/>',
  target: '<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="4"/><circle cx="12" cy="12" r="1"/>',
  flame: '<path d="M12 3c3 3.6 5 5.9 5 8.8A5 5 0 0 1 7 12c0-1.7.8-3 2-4.2.3 1.3 1 2 2 2.4C10.4 7.6 11 5.4 12 3Z"/>',
  trophy: '<path d="M8 4h8v5a4 4 0 0 1-8 0V4Z"/><path d="M8 6H5.5A2.5 2.5 0 0 0 8 10.5M16 6h2.5A2.5 2.5 0 0 1 16 10.5"/><path d="M10 13h4l.5 4h-5l.5-4Z"/><path d="M8 19h8"/>',
  gem: '<path d="M6 3h12l3 6-9 12L3 9l3-6Z"/><path d="M3 9h18M9 3l-3 6 6 12 6-12-3-6"/>',
  book: '<path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v15H6.5A2.5 2.5 0 0 0 4 20.5V5.5Z"/><path d="M4 20.5A2.5 2.5 0 0 1 6.5 18H20v3H6.5A2.5 2.5 0 0 1 4 20.5Z"/>',
  bolt: '<path d="M13 2 4 14h6l-1 8 9-12h-6l1-8Z"/>',
  mountain: '<path d="m3 19 6-11 4 6 2-3 6 8H3Z"/>',
  sprout: '<path d="M12 21v-7"/><path d="M12 14C12 10 9 8 5 8c0 4 3 6 7 6Z"/><path d="M12 14c0-3 2.5-5 7-5 0 3.5-2.8 5-7 5Z"/>',
  medal: '<circle cx="12" cy="15" r="5"/><path d="m8.5 10.5-2-7h4l1.5 4 1.5-4h4l-2 7"/>',
  sparkle: '<path d="M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2.5 2.5M15.5 15.5 18 18M18 6l-2.5 2.5M8.5 15.5 6 18"/>',
  stack: '<path d="M12 3 3 8l9 5 9-5-9-5Z"/><path d="m3 13 9 5 9-5"/>',
};
