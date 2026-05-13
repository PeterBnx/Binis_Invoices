import fs from 'fs';
import path from 'path';
import { BrowserWindow } from 'electron';
import { pathToFileURL, fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const IPC_HANDLERS_DIR = path.join(__dirname);


const ext = '.js';

function getAllHandlerFiles(dir: string, ext: string): string[] {
  let results: string[] = [];
  const list = fs.readdirSync(dir);
  for (const file of list) {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);
    if (stat && stat.isDirectory()) {
      results = results.concat(getAllHandlerFiles(filePath, ext));
    } else if (
      file !== `index${ext}` &&
      file.endsWith('Handler' + ext)
    ) {
      results.push(filePath);
    }
  }
  return results;
}

export async function registerAllIpcHandlers(mainWindow: BrowserWindow) {
  let files: string[] = [];
  try {
    files = getAllHandlerFiles(IPC_HANDLERS_DIR, ext);
  } catch (err) {
    console.error('[IPC] Failed to read IPC handlers directory:', err);
    return;
  }

  console.log('[IPC] IPC handler files found:', files.map(f => path.relative(IPC_HANDLERS_DIR, f)));

  for (const file of files) {
    try {
      const moduleUrl = pathToFileURL(file).href;
      const module = await import(moduleUrl);
      const baseName = path.basename(file, ext);

      const register =
        module.default ?? module[`register${capitalize(baseName)}Handlers`];
      if (typeof register === 'function') {
        register(mainWindow);
      } else {
        console.warn(`[IPC] Skipped ${file}: No export function found`);
      }
    } catch (err) {
      console.error(`[IPC] Failed to load ${file}:`, err);
    }
  }
}

function capitalize(str: string) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}