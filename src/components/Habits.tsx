import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import type { Habit } from '../types';
import { getTodayString } from '../utils/helpers';

interface HabitsProps {
  habits: Habit[];
  onAddHabit: (name: string, description: string, frequency: 'daily' | 'weekly') => void;
  onToggleCompletion: (habitId: string, dateString: string) => void;
  onDeleteHabit: (habitId: string) => void;
}

export const Habits = ({ habits, onAddHabit, onToggleCompletion, onDeleteHabit }: HabitsProps) => {
  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [frequency, setFrequency] = useState<'daily' | 'weekly'>('daily');

  const today = getTodayString();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (name.trim()) {
      onAddHabit(name.trim(), description.trim(), frequency);
      setName('');
      setDescription('');
      setFrequency('daily');
      setShowForm(false);
    }
  };

  const getCompletionRate = (habit: Habit): number => {
    if (habit.completed.length === 0) return 0;
    const daysActive = Math.max(
      1,
      Math.ceil((Date.now() - habit.createdAt.getTime()) / (1000 * 60 * 60 * 24))
    );
    return Math.round((habit.completed.length / daysActive) * 100);
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-2xl shadow-xl overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-green-500 to-teal-600 text-white p-6">
        <h2 className="text-2xl font-bold">✅ 习惯追踪</h2>
        <p className="text-green-100 text-sm mt-1">建立好习惯，成就更好的自己</p>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        <AnimatePresence>
          {habits.length === 0 && !showForm ? (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-center text-gray-500 mt-20"
            >
              <div className="text-6xl mb-4">🎯</div>
              <p className="text-lg mb-4">还没有习惯记录</p>
              <button
                onClick={() => setShowForm(true)}
                className="px-6 py-3 bg-green-500 text-white rounded-xl hover:bg-green-600 transition-colors"
              >
                创建第一个习惯
              </button>
            </motion.div>
          ) : (
            <div className="space-y-4">
              {habits.map((habit, index) => {
                const isCompletedToday = habit.completed.includes(today);
                const completionRate = getCompletionRate(habit);

                return (
                  <motion.div
                    key={habit.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="bg-gray-50 rounded-xl p-4 border border-gray-200 hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3">
                          <button
                            onClick={() => onToggleCompletion(habit.id, today)}
                            className={`w-8 h-8 rounded-full border-2 flex items-center justify-center transition-all ${
                              isCompletedToday
                                ? 'bg-green-500 border-green-500'
                                : 'border-gray-300 hover:border-green-500'
                            }`}
                          >
                            {isCompletedToday && (
                              <motion.svg
                                initial={{ scale: 0 }}
                                animate={{ scale: 1 }}
                                className="w-5 h-5 text-white"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                              >
                                <path
                                  strokeLinecap="round"
                                  strokeLinejoin="round"
                                  strokeWidth={2}
                                  d="M5 13l4 4L19 7"
                                />
                              </motion.svg>
                            )}
                          </button>
                          <div>
                            <h3 className="font-semibold text-lg">{habit.name}</h3>
                            {habit.description && (
                              <p className="text-sm text-gray-600">{habit.description}</p>
                            )}
                          </div>
                        </div>
                        <div className="mt-3 flex items-center space-x-4 text-sm text-gray-500">
                          <span className="flex items-center">
                            <span className="mr-1">📅</span>
                            {habit.frequency === 'daily' ? '每日' : '每周'}
                          </span>
                          <span className="flex items-center">
                            <span className="mr-1">🔥</span>
                            {habit.completed.length} 次完成
                          </span>
                          <span className="flex items-center">
                            <span className="mr-1">📊</span>
                            {completionRate}% 完成率
                          </span>
                        </div>
                      </div>
                      <button
                        onClick={() => onDeleteHabit(habit.id)}
                        className="text-red-500 hover:text-red-700 transition-colors"
                      >
                        <svg
                          className="w-5 h-5"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                          />
                        </svg>
                      </button>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          )}
        </AnimatePresence>

        {/* Add Habit Form */}
        {showForm && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-6 bg-blue-50 rounded-xl p-4 border border-blue-200"
          >
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  习惯名称
                </label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="例如：每日阅读"
                  className="w-full px-4 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-green-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  描述（可选）
                </label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="描述这个习惯..."
                  className="w-full px-4 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-green-500"
                  rows={2}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  频率
                </label>
                <select
                  value={frequency}
                  onChange={(e) => setFrequency(e.target.value as 'daily' | 'weekly')}
                  className="w-full px-4 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                  <option value="daily">每日</option>
                  <option value="weekly">每周</option>
                </select>
              </div>
              <div className="flex space-x-2">
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
                >
                  添加习惯
                </button>
                <button
                  type="button"
                  onClick={() => setShowForm(false)}
                  className="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition-colors"
                >
                  取消
                </button>
              </div>
            </form>
          </motion.div>
        )}
      </div>

      {/* Footer */}
      {habits.length > 0 && !showForm && (
        <div className="p-4 bg-gray-50 border-t border-gray-200">
          <button
            onClick={() => setShowForm(true)}
            className="w-full px-4 py-3 bg-green-500 text-white rounded-xl hover:bg-green-600 transition-colors"
          >
            + 添加新习惯
          </button>
        </div>
      )}
    </div>
  );
};
