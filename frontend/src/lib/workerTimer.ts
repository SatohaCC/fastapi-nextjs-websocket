"use client";

class WorkerTimer {
  private worker: Worker | null = null;
  private callbacks = new Map<number, () => void>();
  private nextId = 1;

  constructor() {
    if (typeof window === "undefined") return;

    const workerCode = `
      const timers = new Map();
      self.onmessage = function(e) {
        const { action, id, delay } = e.data;
        if (action === 'setTimeout') {
          const timerId = setTimeout(() => {
            self.postMessage({ type: 'timeout', id });
            timers.delete(id);
          }, delay);
          timers.set(id, timerId);
        } else if (action === 'clearTimeout') {
          const timerId = timers.get(id);
          if (timerId) {
            clearTimeout(timerId);
            timers.delete(id);
          }
        }
      };
    `;

    try {
      const blob = new Blob([workerCode], { type: "application/javascript" });
      const url = URL.createObjectURL(blob);
      this.worker = new Worker(url);

      this.worker.onmessage = (e) => {
        if (e.data.type === "timeout") {
          const id = e.data.id;
          const cb = this.callbacks.get(id);
          if (cb) {
            cb();
            this.callbacks.delete(id);
          }
        }
      };
    } catch (err) {
      // biome-ignore lint/suspicious/noConsole: fallback timer warning
      console.warn(
        "Failed to initialize Web Worker timer. Falling back to window.setTimeout.",
        err,
      );
    }
  }

  setTimeout(callback: () => void, delay: number): number {
    if (!this.worker) {
      return window.setTimeout(callback, delay) as unknown as number;
    }
    const id = this.nextId++;
    this.callbacks.set(id, callback);
    this.worker.postMessage({ action: "setTimeout", id, delay });
    return id;
  }

  clearTimeout(id: number | null | undefined): void {
    if (id == null) return;
    if (!this.worker) {
      window.clearTimeout(id);
      return;
    }
    this.callbacks.delete(id);
    this.worker.postMessage({ action: "clearTimeout", id });
  }

  terminate(): void {
    this.worker?.terminate();
    this.worker = null;
    this.callbacks.clear();
  }
}

export const workerTimer = new WorkerTimer();
