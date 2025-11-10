// Mock Claude API responses
const mockResponses = [
  "很高兴能陪伴你的成长之旅！让我们一起探索你的目标和习惯。",
  "太棒了！保持这种积极的状态。记住，每一天的小进步都会累积成巨大的改变。",
  "我理解你现在的感受。成长的道路上有起伏是很正常的。让我们一起找到适合你的方法。",
  "这是一个很好的反思。你已经在自我认知的道路上迈出了重要的一步。",
  "建议你今天专注于一个小目标，完成它会给你带来成就感。你想从哪个习惯开始？",
  "你的坚持让我印象深刻！持续追踪你的习惯会帮助你更好地了解自己的模式。",
];

// Simulate API delay
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

export const claudeService = {
  async sendMessage(userMessage: string): Promise<string> {
    // Simulate API call delay
    await delay(500 + Math.random() * 1000);

    // Simple keyword-based responses for more natural interaction
    const lowerMessage = userMessage.toLowerCase();

    if (lowerMessage.includes('你好') || lowerMessage.includes('hello') || lowerMessage.includes('hi')) {
      return "你好！我是 LifeOS，你的个人成长助理。我可以帮你追踪习惯、记录反思，陪伴你的成长之旅。今天想聊些什么？";
    }

    if (lowerMessage.includes('习惯') || lowerMessage.includes('habit')) {
      return "建立好习惯是个人成长的关键。你可以使用习惯追踪功能来记录和管理你的日常习惯。想要创建一个新习惯吗？";
    }

    if (lowerMessage.includes('反思') || lowerMessage.includes('reflection') || lowerMessage.includes('日记')) {
      return "反思是自我成长的重要一步。通过定期记录你的想法、感受和经历，你会更了解自己。今天有什么想要记录的吗？";
    }

    if (lowerMessage.includes('帮助') || lowerMessage.includes('help') || lowerMessage.includes('怎么用')) {
      return "我可以帮助你：\n1. 💬 对话交流 - 随时与我聊聊你的想法\n2. ✅ 习惯追踪 - 创建和管理你的日常习惯\n3. 📔 每日反思 - 记录你的心情和成长\n\n所有数据都保存在你的浏览器本地，完全私密安全。";
    }

    if (lowerMessage.includes('谢谢') || lowerMessage.includes('感谢') || lowerMessage.includes('thank')) {
      return "不客气！很高兴能帮到你。记住，我随时在这里陪伴你的成长之旅。💙";
    }

    // Return a random response for other messages
    return mockResponses[Math.floor(Math.random() * mockResponses.length)];
  },

  // Generate a habit recommendation
  async getHabitRecommendation(): Promise<string> {
    await delay(300);
    const recommendations = [
      "每天冥想 10 分钟 - 帮助你培养专注力和内心平静",
      "阅读 30 分钟 - 持续学习，拓展视野",
      "运动 30 分钟 - 保持身心健康",
      "写作/反思 15 分钟 - 记录想法，促进自我认知",
      "学习新技能 1 小时 - 投资自己，持续成长",
    ];
    return recommendations[Math.floor(Math.random() * recommendations.length)];
  },
};
