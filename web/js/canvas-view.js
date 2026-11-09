// Viewport for book-notation SVG trees. Never mutates syntax labels.
export function enableCanvasView(host, lessonWrap) {
  if (!host || !lessonWrap) throw new Error('Missing canonical tree container');
  const svg = lessonWrap.querySelector('svg');
  if (!svg) throw new Error('Canonical B-R SVG is missing');
  const viewport = document.createElement('div');
  viewport.className = 'canonical-viewport';
  viewport.tabIndex = 0;
  viewport.setAttribute('role', 'region');
  viewport.setAttribute('aria-label', 'Burton-Roberts syntax tree: drag to pan, wheel to zoom');
  const layer = document.createElement('div');
  layer.className = 'canonical-layer';
  layer.append(svg);
  viewport.append(layer);
  const controls = document.createElement('div');
  controls.className = 'canonical-zoom';
  viewport.append(controls);
  host.insertBefore(viewport, lessonWrap);
  const vb = svg.viewBox?.baseVal;
  const w = Number(vb?.width) || Number(svg.getAttribute('width')) || 400;
  const h = Number(vb?.height) || Number(svg.getAttribute('height')) || 200;
  let scale = 1, tx = 0, ty = 0, dragging = null, destroyed = false;
  const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
  const paint = () => {
    if (!destroyed) layer.style.transform = 'translate(' + tx + 'px, ' + ty + 'px) scale(' + scale + ')';
  };
  const fit = () => {
    if (destroyed) return;
    const rect = viewport.getBoundingClientRect();
    scale = clamp(Math.min((Math.max(rect.width, 100) - 40) / w, (Math.max(rect.height, 100) - 50) / h), .12, 3);
    tx = (rect.width - w * scale) / 2;
    ty = (rect.height - h * scale) / 2;
    paint();
  };
  const zoom = (factor, clientX, clientY) => {
    const rect = viewport.getBoundingClientRect();
    const x = clientX == null ? rect.width / 2 : clientX - rect.left;
    const y = clientY == null ? rect.height / 2 : clientY - rect.top;
    const next = clamp(scale * factor, .12, 5);
    tx = x - ((x - tx) / scale) * next;
    ty = y - ((y - ty) / scale) * next;
    scale = next;
    paint();
  };
  const makeButton = (text, label, action) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.textContent = text;
    button.setAttribute('aria-label', label);
    button.addEventListener('click', action);
    controls.append(button);
  };
  makeButton('+', 'Zoom in B-R tree', () => zoom(1.25));
  makeButton('−', 'Zoom out B-R tree', () => zoom(.8));
  makeButton('Fit', 'Fit B-R tree', fit);
  const onWheel = event => {
    event.preventDefault();
    zoom(event.deltaY < 0 ? 1.12 : 1 / 1.12, event.clientX, event.clientY);
  };
  const down = event => {
    if (event.button !== 0 || event.target.closest('button, [data-node-id], a, input')) return;
    dragging = {id:event.pointerId, x:event.clientX, y:event.clientY, tx, ty};
    viewport.classList.add('is-panning');
    viewport.setPointerCapture?.(event.pointerId);
  };
  const move = event => {
    if (!dragging || dragging.id !== event.pointerId) return;
    tx = dragging.tx + event.clientX - dragging.x;
    ty = dragging.ty + event.clientY - dragging.y;
    paint();
  };
  const up = event => {
    if (!dragging || dragging.id !== event.pointerId) return;
    dragging = null;
    viewport.classList.remove('is-panning');
    if (viewport.hasPointerCapture?.(event.pointerId)) viewport.releasePointerCapture(event.pointerId);
  };
  const keydown = event => {
    if (event.target !== viewport) return;
    const offsets = {ArrowUp:[0,30], ArrowDown:[0,-30], ArrowLeft:[30,0], ArrowRight:[-30,0]};
    if (offsets[event.key]) {
      event.preventDefault();
      tx += offsets[event.key][0]; ty += offsets[event.key][1]; paint();
    } else if (event.key === '+' || event.key === '=') {
      event.preventDefault(); zoom(1.25);
    } else if (event.key === '-') {
      event.preventDefault(); zoom(.8);
    } else if (event.key === 'Home') {
      event.preventDefault(); fit();
    }
  };
  const resize = () => { if (!dragging) fit(); };
  viewport.addEventListener('wheel', onWheel, {passive:false});
  viewport.addEventListener('pointerdown', down);
  viewport.addEventListener('pointermove', move);
  viewport.addEventListener('pointerup', up);
  viewport.addEventListener('pointercancel', up);
  viewport.addEventListener('keydown', keydown);
  window.addEventListener('resize', resize);
  const observer = typeof ResizeObserver === 'undefined' ? null : new ResizeObserver(resize);
  observer?.observe(viewport);
  requestAnimationFrame(fit);
  return {
    fit, zoom,
    destroy() {
      if (destroyed) return;
      destroyed = true;
      observer?.disconnect();
      window.removeEventListener('resize', resize);
      viewport.removeEventListener('wheel', onWheel);
      viewport.removeEventListener('pointerdown', down);
      viewport.removeEventListener('pointermove', move);
      viewport.removeEventListener('pointerup', up);
      viewport.removeEventListener('pointercancel', up);
      viewport.removeEventListener('keydown', keydown);
      if (svg.parentNode === layer) lessonWrap.insertBefore(svg, lessonWrap.firstChild);
      viewport.remove();
    },
  };
}
