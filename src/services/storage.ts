import type { AppState, Message, Habit, Reflection } from '../types';

const STORAGE_KEY = 'lifeos-data';

const defaultState: AppState = {
  messages: [],
  habits: [],
  reflections: [],
};

export const storageService = {
  // Get all data from localStorage
  getData(): AppState {
    try {
      const data = localStorage.getItem(STORAGE_KEY);
      if (!data) return defaultState;
      
      const parsed = JSON.parse(data);
      // Convert ISO strings back to Date objects
      return {
        messages: parsed.messages.map((m: { id: string; role: 'user' | 'assistant'; content: string; timestamp: string }) => ({
          ...m,
          timestamp: new Date(m.timestamp),
        })),
        habits: parsed.habits.map((h: { id: string; name: string; description: string; frequency: 'daily' | 'weekly'; completed: string[]; createdAt: string }) => ({
          ...h,
          createdAt: new Date(h.createdAt),
        })),
        reflections: parsed.reflections.map((r: { id: string; date: string; content: string; mood: number; habits: string[]; createdAt: string }) => ({
          ...r,
          createdAt: new Date(r.createdAt),
        })),
      };
    } catch (error) {
      console.error('Error loading data from localStorage:', error);
      return defaultState;
    }
  },

  // Save all data to localStorage
  saveData(state: AppState): void {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch (error) {
      console.error('Error saving data to localStorage:', error);
    }
  },

  // Save messages
  saveMessages(messages: Message[]): void {
    const state = this.getData();
    state.messages = messages;
    this.saveData(state);
  },

  // Save habits
  saveHabits(habits: Habit[]): void {
    const state = this.getData();
    state.habits = habits;
    this.saveData(state);
  },

  // Save reflections
  saveReflections(reflections: Reflection[]): void {
    const state = this.getData();
    state.reflections = reflections;
    this.saveData(state);
  },

  // Clear all data
  clearData(): void {
    localStorage.removeItem(STORAGE_KEY);
  },
};
