import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import type { Reflection, Habit } from '../types';
import { formatDate } from '../utils/helpers';

interface ReflectionsProps {
  reflections: Reflection[];
  habits: Habit[];
  onAddReflection: (content: string, mood: number, habitIds: string[]) => void;
  onDeleteReflection: (reflectionId: string) => void;
}

export const Reflections = ({
  reflections,
  habits,
  onAddReflection,
  onDeleteReflection,
}: ReflectionsProps) => {
  const [showForm, setShowForm] = useState(false);
  const [content, setContent] = useState('');
  const [mood, setMood] = useState(3);
  const [selectedHabits, setSelectedHabits] = useState<string[]>([]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (content.trim()) {
      onAddReflection(content.trim(), mood, selectedHabits);
      setContent('');
      setMood(3);
      setSelectedHabits([]);
      setShowForm(false);
    }
  };

  const moodEmojis = ['😢', '😕', '😐', '🙂', '😊'];
  const moodLabels = ['很差', '不好', '一般', '不错', '很好'];

  const sortedReflections = [...reflections].sort(
    (a, b) => new Date(b.date).getTime() - new Date(a.date).getTime()
  );

  return (
    <div className="flex flex-col h-full bg-white rounded-2xl shadow-xl overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-500 to-pink-600 text-white p-6">
        <h2 className="text-2xl font-bold">📔 每日反思</h2>
        <p className="text-purple-100 text-sm mt-1">记录你的想法和成长</p>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        <AnimatePresence>
          {sortedReflections.length === 0 && !showForm ? (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-center text-gray-500 mt-20"
            >
              <div className="text-6xl mb-4">✍️</div>
              <p className="text-lg mb-4">开始你的第一篇反思</p>
              <button
                onClick={() => setShowForm(true)}
                className="px-6 py-3 bg-purple-500 text-white rounded-xl hover:bg-purple-600 transition-colors"
              >
                写下今天的想法
              </button>
            </motion.div>
          ) : (
            <div className="space-y-4">
              {sortedReflections.map((reflection, index) => {
                const reflectionHabits = habits.filter(h =>
                  reflection.habits.includes(h.id)
                );

                return (
                  <motion.div
                    key={reflection.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="bg-gray-50 rounded-xl p-5 border border-gray-200 hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center space-x-3">
                        <span className="text-3xl">{moodEmojis[reflection.mood - 1]}</span>
                        <div>
                          <p className="text-sm text-gray-600">
                            {formatDate(new Date(reflection.date))}
                          </p>
                          <p className="text-xs text-gray-500">
                            心情：{moodLabels[reflection.mood - 1]}
                          </p>
                        </div>
                      </div>
                      <button
                        onClick={() => onDeleteReflection(reflection.id)}
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
                    <p className="text-gray-800 whitespace-pre-wrap mb-3">{reflection.content}</p>
                    {reflectionHabits.length > 0 && (
                      <div className="flex flex-wrap gap-2">
                        {reflectionHabits.map(habit => (
                          <span
                            key={habit.id}
                            className="px-3 py-1 bg-blue-100 text-blue-700 text-xs rounded-full"
                          >
                            ✓ {habit.name}
                          </span>
                        ))}
                      </div>
                    )}
                  </motion.div>
                );
              })}
            </div>
          )}
        </AnimatePresence>

        {/* Add Reflection Form */}
        {showForm && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-6 bg-purple-50 rounded-xl p-4 border border-purple-200"
          >
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  今天的想法
                </label>
                <textarea
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  placeholder="写下你今天的想法、感受和收获..."
                  className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-purple-500"
                  rows={4}
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  今天的心情
                </label>
                <div className="flex items-center justify-between">
                  {moodEmojis.map((emoji, index) => (
                    <button
                      key={index}
                      type="button"
                      onClick={() => setMood(index + 1)}
                      className={`flex flex-col items-center p-2 rounded-lg transition-all ${
                        mood === index + 1
                          ? 'bg-purple-100 scale-110'
                          : 'hover:bg-gray-100'
                      }`}
                    >
                      <span className="text-3xl">{emoji}</span>
                      <span className="text-xs text-gray-600 mt-1">{moodLabels[index]}</span>
                    </button>
                  ))}
                </div>
              </div>
              {habits.length > 0 && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    相关习惯（可选）
                  </label>
                  <div className="space-y-2">
                    {habits.map(habit => (
                      <label key={habit.id} className="flex items-center space-x-2 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={selectedHabits.includes(habit.id)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setSelectedHabits([...selectedHabits, habit.id]);
                            } else {
                              setSelectedHabits(selectedHabits.filter(id => id !== habit.id));
                            }
                          }}
                          className="w-4 h-4 text-purple-500 rounded focus:ring-purple-500"
                        />
                        <span className="text-sm text-gray-700">{habit.name}</span>
                      </label>
                    ))}
                  </div>
                </div>
              )}
              <div className="flex space-x-2">
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition-colors"
                >
                  保存反思
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
      {!showForm && (
        <div className="p-4 bg-gray-50 border-t border-gray-200">
          <button
            onClick={() => setShowForm(true)}
            className="w-full px-4 py-3 bg-purple-500 text-white rounded-xl hover:bg-purple-600 transition-colors"
          >
            + 写下今天的想法
          </button>
        </div>
      )}
    </div>
  );
};
