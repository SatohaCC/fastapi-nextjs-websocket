const AUTO_DISMISS_MS = 4000;
const LEAVE_ANIMATION_MS = 250;

export interface ToastItem {
  id: string;
  title: string;
  description?: string;
  leaving: boolean;
}

type Listener = (toasts: ToastItem[]) => void;

let toasts: ToastItem[] = [];
const listeners = new Set<Listener>();

function notify(): void {
  const snapshot = [...toasts];
  for (const fn of listeners) fn(snapshot);
}

function dismiss(id: string): void {
  const target = toasts.find((t) => t.id === id);
  if (!target || target.leaving) return;
  toasts = toasts.map((t) => (t.id === id ? { ...t, leaving: true } : t));
  notify();
  setTimeout(() => {
    toasts = toasts.filter((t) => t.id !== id);
    notify();
  }, LEAVE_ANIMATION_MS);
}

export const toast = {
  message(title: string, opts?: { description?: string }): void {
    const id = Math.random().toString(36).slice(2);
    toasts = [
      ...toasts,
      { id, title, description: opts?.description, leaving: false },
    ];
    notify();
    setTimeout(() => dismiss(id), AUTO_DISMISS_MS);
  },

  dismiss,

  subscribe(fn: Listener): () => void {
    listeners.add(fn);
    fn([...toasts]);
    return () => listeners.delete(fn);
  },
};
