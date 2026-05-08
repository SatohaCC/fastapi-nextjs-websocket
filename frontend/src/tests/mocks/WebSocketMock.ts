/**
 * テスト用の WebSocket モッククラス。
 * global.WebSocket をこれで差し替えることで、プログラムからメッセージ送信をシミュレートできる。
 */
export class WebSocketMock extends EventTarget {
  static readonly CONNECTING = 0;
  static readonly OPEN = 1;
  static readonly CLOSING = 2;
  static readonly CLOSED = 3;

  static instances: WebSocketMock[] = [];

  url: string;
  readyState: number = WebSocketMock.CONNECTING;

  onopen: ((event: Event) => void) | null = null;
  onmessage: ((event: MessageEvent) => void) | null = null;
  onclose: ((event: Event) => void) | null = null;
  onerror: ((event: Event) => void) | null = null;

  constructor(url: string) {
    super();
    this.url = url;
    WebSocketMock.instances.push(this);

    // 非同期でオープンをエミュレート
    setTimeout(() => {
      this.readyState = WebSocketMock.OPEN;
      this.dispatchEvent(new Event("open"));
    }, 10);
  }

  override dispatchEvent(event: Event): boolean {
    const sent = super.dispatchEvent(event);
    if (event.type === "open" && this.onopen) this.onopen(event);
    if (event.type === "message" && this.onmessage)
      this.onmessage(event as MessageEvent);
    if (event.type === "close" && this.onclose) this.onclose(event);
    if (event.type === "error" && this.onerror) this.onerror(event);
    return sent;
  }

  send(data: string) {
    // 送信時の処理（必要に応じて spy できるようにする）
    this.dispatchEvent(new MessageEvent("sent", { data }));
  }

  close() {
    this.readyState = WebSocketMock.CLOSED;
    this.dispatchEvent(new Event("close"));
  }

  // テストからメッセージを「受信」させるためのヘルパー
  receive(data: unknown) {
    this.dispatchEvent(
      new MessageEvent("message", {
        data: JSON.stringify(data),
      }),
    );
  }

  static lastInstance() {
    return WebSocketMock.instances[WebSocketMock.instances.length - 1];
  }

  static clearInstances() {
    WebSocketMock.instances = [];
  }
}
