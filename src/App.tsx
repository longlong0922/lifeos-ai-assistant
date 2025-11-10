import { useState } from 'react';
import { motion } from 'framer-motion';
import { Chat } from './components/Chat';
import { Habits } from './components/Habits';
import { Reflections } from './components/Reflections';
import { useLifeOS } from './hooks/useLifeOS';

type TabType = 'chat' | 'habits' | 'reflections';

function App() {
  const [activeTab, setActiveTab] = useState<TabType>('chat');
  const {
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
  } = useLifeOS();

  const tabs = [
    { id: 'chat' as TabType, label: '对话', icon: '💬' },
    { id: 'habits' as TabType, label: '习惯', icon: '✅' },
    { id: 'reflections' as TabType, label: '反思', icon: '📔' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.header
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6"
        >
          <div className="text-center">
            <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-2">
              LifeOS
            </h1>
            <p className="text-gray-600">你的 AI 原生个人成长助理</p>
          </div>
        </motion.header>

        {/* Tabs */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="flex justify-center mb-6"
        >
          <div className="bg-white rounded-2xl shadow-lg p-2 flex space-x-2">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-6 py-3 rounded-xl transition-all font-medium ${
                  activeTab === tab.id
                    ? 'bg-gradient-to-r from-blue-500 to-indigo-600 text-white shadow-md'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </div>
        </motion.div>

        {/* Content */}
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          className="h-[calc(100vh-240px)]"
        >
          {activeTab === 'chat' && (
            <Chat
              messages={messages}
              isLoading={isLoading}
              onSendMessage={sendMessage}
            />
          )}
          {activeTab === 'habits' && (
            <Habits
              habits={habits}
              onAddHabit={addHabit}
              onToggleCompletion={toggleHabitCompletion}
              onDeleteHabit={deleteHabit}
            />
          )}
          {activeTab === 'reflections' && (
            <Reflections
              reflections={reflections}
              habits={habits}
              onAddReflection={addReflection}
              onDeleteReflection={deleteReflection}
            />
          )}
        </motion.div>

        {/* Footer */}
        <motion.footer
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="mt-6 text-center text-gray-500 text-sm"
        >
          <p>数据保存在本地浏览器，完全私密 🔒</p>
        </motion.footer>
      </div>
    </div>
  );
}

export default App;
