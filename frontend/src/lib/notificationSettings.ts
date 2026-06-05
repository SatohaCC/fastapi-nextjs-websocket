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

type Listener = (settings: NotificationSettings) => void;

let isInitialized = false;
const modifiedKeys = new Set<keyof NotificationSettings>();
let current: NotificationSettings = { ...DEFAULT_SETTINGS };
const listeners = new Set<Listener>();

function notify(): void {
  const snapshot = { ...current };
  for (const fn of listeners) fn(snapshot);
}

export function initSettings(s: NotificationSettings): void {
  if (isInitialized) return;

  // サーバーの設定を適用するが、初期化完了前にユーザーが手動操作した設定は維持する
  const nextSettings = { ...s };
  for (const key of modifiedKeys) {
    nextSettings[key] = current[key];
  }

  current = nextSettings;
  isInitialized = true;
  notify();
}

export function getSettings(): NotificationSettings {
  return { ...current };
}

export function updateSetting<K extends keyof NotificationSettings>(
  key: K,
  value: boolean,
): void {
  current = { ...current, [key]: value };
  modifiedKeys.add(key);
  notify();
}

export function subscribe(fn: Listener): () => void {
  listeners.add(fn);
  fn({ ...current });
  return () => listeners.delete(fn);
}
