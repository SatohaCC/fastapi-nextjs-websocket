const STORAGE_KEY = "ws-chat:notification-settings";

export interface NotificationSettings {
  globalChat: boolean;
  directRequest: boolean;
  directRequestUpdated: boolean;
}

export const DEFAULT_SETTINGS: NotificationSettings = {
  globalChat: true,
  directRequest: true,
  directRequestUpdated: true,
};

const DEFAULT = DEFAULT_SETTINGS;

type Listener = (settings: NotificationSettings) => void;

function loadFromStorage(): NotificationSettings {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return { ...DEFAULT };
    return { ...DEFAULT, ...JSON.parse(raw) };
  } catch {
    return { ...DEFAULT };
  }
}

function saveToStorage(s: NotificationSettings): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(s));
  } catch {
    // ignore (SSR / private browsing)
  }
}

let current: NotificationSettings = loadFromStorage();
const listeners = new Set<Listener>();

function notify(): void {
  const snapshot = { ...current };
  for (const fn of listeners) fn(snapshot);
}

export function getSettings(): NotificationSettings {
  return { ...current };
}

export function updateSetting<K extends keyof NotificationSettings>(
  key: K,
  value: boolean,
): void {
  current = { ...current, [key]: value };
  saveToStorage(current);
  notify();
}

export function subscribe(fn: Listener): () => void {
  listeners.add(fn);
  fn({ ...current });
  return () => listeners.delete(fn);
}
