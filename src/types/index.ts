export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export interface Habit {
  id: string;
  name: string;
  description: string;
  frequency: 'daily' | 'weekly';
  completed: string[]; // Array of ISO date strings
  createdAt: Date;
}

export interface Reflection {
  id: string;
  date: string; // ISO date string
  content: string;
  mood: number; // 1-5 scale
  habits: string[]; // Array of habit IDs
  createdAt: Date;
}

export interface AppState {
  messages: Message[];
  habits: Habit[];
  reflections: Reflection[];
}
