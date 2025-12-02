export interface TranscriptionResult {
  type: 'session_id' | 'partial' | 'final' | 'error';
  text?: string;
  id?: string;
  word_count?: number;
  session_complete?: boolean; // ✅ added
}

export class TranscriptionWebSocket {
  private ws: WebSocket | null = null;
  private sessionId: string | null = null;

  constructor(
    private url: string,
    private onMessage: (result: TranscriptionResult) => void,
    private onError: (error: string) => void
  ) {}

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        console.log('WebSocket connected');
        resolve();
      };

      this.ws.onmessage = (event) => {
        try {
          const data: TranscriptionResult = JSON.parse(event.data);

          if (data.type === 'session_id' && data.id) {
            this.sessionId = data.id;
          }

          this.onMessage(data);
        } catch (error) {
          console.error('Error parsing message:', error);
          this.onError('Error parsing message');
        }
      };

      this.ws.onerror = (event) => {
        console.error('WebSocket error:', event);
        this.onError('Connection error occurred');
        reject(event);
      };

      this.ws.onclose = () => {
        console.log('WebSocket disconnected');
      };
    });
  }

  sendAudio(audioData: Blob): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      audioData.arrayBuffer().then((buffer) => {
        this.ws?.send(buffer);
      });
    }
  }

  sendEndOfAudio(): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ action: "end_audio" }));
      console.log("✅ End-of-audio signal sent");
    }
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  getSessionId(): string | null {
    return this.sessionId;
  }

  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }
}
