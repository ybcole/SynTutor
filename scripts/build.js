import { cpSync, existsSync, mkdirSync, rmSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const out = join(root, 'dist');

const ENTRIES = ['index.html', 'login.html', 'css', 'js'];

rmSync(out, { recursive: true, force: true });
mkdirSync(out, { recursive: true });

for (const entry of ENTRIES) {
  const src = join(root, entry);
  if (!existsSync(src)) {
    console.warn(`[build] skipping missing ${entry}`);
    continue;
  }
  cpSync(src, join(out, entry), { recursive: true });
  console.log(`[build] ${entry} -> dist/${entry}`);
}

console.log('[build] static site written to dist/');
