const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface Session {
  id: string;
  transcript: string;
  word_count: number;
  duration: number;
  created_at: string;
}

export class ApiService {
  static async getAllSessions(): Promise<Session[]> {
    const response = await fetch(`${API_BASE_URL}/sessions`);
    if (!response.ok) {
      throw new Error(`Failed to fetch sessions: ${response.status} ${response.statusText}`);
    }
    return response.json();
  }

  static async getSessionById(id: string): Promise<Session> {
    const response = await fetch(`${API_BASE_URL}/sessions/${id}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch session ${id}: ${response.status} ${response.statusText}`);
    }
    return response.json();
  }

  static async deleteSession(id: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/sessions/${id}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      throw new Error(`Failed to delete session ${id}: ${response.status} ${response.statusText}`);
    }
  }
}
