import { useState, useEffect } from 'react';
import type { Message, Habit, Reflection } from '../types';
import { storageService } from '../services/storage';
import { claudeService } from '../services/claude';
import { generateId } from '../utils/helpers';

export const useLifeOS = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [habits, setHabits] = useState<Habit[]>([]);
  const [reflections, setReflections] = useState<Reflection[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // Load data from localStorage on mount
  useEffect(() => {
    const data = storageService.getData();
    setMessages(data.messages);
    setHabits(data.habits);
    setReflections(data.reflections);
  }, []);

  // Save messages when they change
  useEffect(() => {
    if (messages.length > 0) {
      storageService.saveMessages(messages);
    }
  }, [messages]);

  // Save habits when they change
  useEffect(() => {
    if (habits.length > 0) {
      storageService.saveHabits(habits);
    }
  }, [habits]);

  // Save reflections when they change
  useEffect(() => {
    if (reflections.length > 0) {
      storageService.saveReflections(reflections);
    }
  }, [reflections]);

  // Send a message to Claude
  const sendMessage = async (content: string) => {
    const userMessage: Message = {
      id: generateId(),
      role: 'user',
      content,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await claudeService.sendMessage(content);
      const assistantMessage: Message = {
        id: generateId(),
        role: 'assistant',
        content: response,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Add a new habit
  const addHabit = (name: string, description: string, frequency: 'daily' | 'weekly') => {
    const newHabit: Habit = {
      id: generateId(),
      name,
      description,
      frequency,
      completed: [],
      createdAt: new Date(),
    };
    setHabits(prev => [...prev, newHabit]);
  };

  // Toggle habit completion for a date
  const toggleHabitCompletion = (habitId: string, dateString: string) => {
    setHabits(prev =>
      prev.map(habit => {
        if (habit.id === habitId) {
          const isCompleted = habit.completed.includes(dateString);
          return {
            ...habit,
            completed: isCompleted
              ? habit.completed.filter(d => d !== dateString)
              : [...habit.completed, dateString],
          };
        }
        return habit;
      })
    );
  };

  // Delete a habit
  const deleteHabit = (habitId: string) => {
    setHabits(prev => prev.filter(h => h.id !== habitId));
  };

  // Add a reflection
  const addReflection = (content: string, mood: number, habitIds: string[]) => {
    const newReflection: Reflection = {
      id: generateId(),
      date: new Date().toISOString().split('T')[0],
      content,
      mood,
      habits: habitIds,
      createdAt: new Date(),
    };
    setReflections(prev => [...prev, newReflection]);
  };

  // Delete a reflection
  const deleteReflection = (reflectionId: string) => {
    setReflections(prev => prev.filter(r => r.id !== reflectionId));
  };

  // Clear all data
  const clearAllData = () => {
    setMessages([]);
    setHabits([]);
    setReflections([]);
    storageService.clearData();
  };

  return {
    messages,
    habits,
    reflections,
    isLoading,
    sendMessage,
    addHabit,
    toggleHabitCompletion,
    deleteHabit,
    addReflection,
    deleteReflection,
    clearAllData,
  };
};
