'use client'

import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { apiClient } from '@/lib/api';
import Button from '@/components/ui/Button';
import { useRouter } from 'next/navigation';

interface Message {
  id: number;
  role: 'user' | 'assistant';
  content: string;
  createdAt: string;
}

interface Conversation {
  id: number;
  userId: string;
  createdAt: string;
  updatedAt: string;
}

export default function ChatPage() {
  const router = useRouter();
  const [messages, setMessages] = useState<Message[]>([]);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<number | null>(null);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Check authentication
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      router.push('/login');
    } else {
      loadConversations();
    }
  }, [router]);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadConversations = async () => {
    const response = await apiClient.getConversations();
    if (response.success && response.data) {
      setConversations(response.data);
    }
  };

  const loadConversationMessages = async (conversationId: number) => {
    const response = await apiClient.getConversationMessages(conversationId);
    if (response.success && response.data) {
      setMessages(response.data.map(msg => ({
        id: msg.id,
        role: msg.role as 'user' | 'assistant',
        content: msg.content,
        createdAt: msg.createdAt
      })));
      setCurrentConversationId(conversationId);
    }
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = inputMessage.trim();
    setInputMessage('');
    setIsLoading(true);

    // Add user message to UI immediately
    const tempUserMessage: Message = {
      id: Date.now(),
      role: 'user',
      content: userMessage,
      createdAt: new Date().toISOString()
    };
    setMessages(prev => [...prev, tempUserMessage]);

    try {
      const response = await apiClient.sendChatMessage(userMessage, currentConversationId || undefined);

      if (response.success && response.data) {
        // Add assistant response
        const assistantMessage: Message = {
          id: Date.now() + 1,
          role: 'assistant',
          content: response.data.message,
          createdAt: new Date().toISOString()
        };
        setMessages(prev => [...prev, assistantMessage]);

        // Update conversation ID if new conversation
        if (!currentConversationId) {
          setCurrentConversationId(response.data.conversationId);
          loadConversations();
        }
      } else {
        // Show error message
        const errorMessage: Message = {
          id: Date.now() + 1,
          role: 'assistant',
          content: `Sorry, I encountered an error: ${response.error || 'Unknown error'}`,
          createdAt: new Date().toISOString()
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        id: Date.now() + 1,
        role: 'assistant',
        content: 'Sorry, I encountered a network error. Please try again.',
        createdAt: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewChat = () => {
    setMessages([]);
    setCurrentConversationId(null);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="min-h-screen flex bg-[rgb(var(--background))]">
      {/* Sidebar */}
      <AnimatePresence>
        {isSidebarOpen && (
          <motion.aside
            initial={{ x: -300 }}
            animate={{ x: 0 }}
            exit={{ x: -300 }}
            transition={{ duration: 0.3 }}
            className="w-64 bg-[rgb(var(--card))] border-r border-[rgb(var(--border))] flex flex-col"
          >
            <div className="p-4 border-b border-[rgb(var(--border))]">
              <Button
                onClick={handleNewChat}
                variant="primary"
                className="w-full"
              >
                + New Chat
              </Button>
            </div>

            <div className="flex-1 overflow-y-auto p-4">
              <h3 className="text-sm font-semibold text-[rgb(var(--muted-foreground))] mb-2">
                Recent Conversations
              </h3>
              {conversations.length === 0 ? (
                <p className="text-sm text-[rgb(var(--muted-foreground))]">
                  No conversations yet
                </p>
              ) : (
                <div className="space-y-2">
                  {conversations.map((conv) => (
                    <button
                      key={conv.id}
                      onClick={() => loadConversationMessages(conv.id)}
                      className={`w-full text-left p-3 rounded-lg transition-colors ${
                        currentConversationId === conv.id
                          ? 'bg-[rgb(var(--primary))] text-white'
                          : 'bg-[rgb(var(--muted))] hover:bg-[rgb(var(--muted))]/80'
                      }`}
                    >
                      <p className="text-sm font-medium truncate">
                        Conversation {conv.id}
                      </p>
                      <p className="text-xs opacity-70">
                        {new Date(conv.updatedAt).toLocaleDateString()}
                      </p>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </motion.aside>
        )}
      </AnimatePresence>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="bg-[rgb(var(--card))] border-b border-[rgb(var(--border))] p-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="text-[rgb(var(--foreground))] hover:text-[rgb(var(--primary))]"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            <h1 className="text-xl font-bold text-[rgb(var(--foreground))]">
              TalkTodo AI Assistant
            </h1>
          </div>
          <Button
            onClick={() => router.push('/dashboard')}
            variant="outline"
          >
            Back to Tasks
          </Button>
        </header>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center max-w-md">
                <div className="text-6xl mb-4">💬</div>
                <h2 className="text-2xl font-bold text-[rgb(var(--foreground))] mb-2">
                  Welcome to TalkTodo!
                </h2>
                <p className="text-[rgb(var(--muted-foreground))] mb-4">
                  I'm your AI assistant for managing tasks. You can chat with me in English, Urdu, or Roman Urdu.
                </p>
                <div className="text-left bg-[rgb(var(--muted))] rounded-lg p-4 space-y-2">
                  <p className="text-sm font-semibold text-[rgb(var(--foreground))]">Try asking me:</p>
                  <ul className="text-sm text-[rgb(var(--muted-foreground))] space-y-1">
                    <li>• "Add a task to buy groceries tomorrow"</li>
                    <li>• "Show me all my pending tasks"</li>
                    <li>• "Mark task 5 as complete"</li>
                    <li>• "Delete the grocery task"</li>
                  </ul>
                </div>
              </div>
            </div>
          ) : (
            <>
              {messages.map((message) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[70%] rounded-lg p-4 ${
                      message.role === 'user'
                        ? 'bg-[rgb(var(--primary))] text-white'
                        : 'bg-[rgb(var(--card))] text-[rgb(var(--foreground))] border border-[rgb(var(--border))]'
                    }`}
                  >
                    <p className="whitespace-pre-wrap">{message.content}</p>
                    <p className={`text-xs mt-2 ${
                      message.role === 'user' ? 'text-white/70' : 'text-[rgb(var(--muted-foreground))]'
                    }`}>
                      {new Date(message.createdAt).toLocaleTimeString()}
                    </p>
                  </div>
                </motion.div>
              ))}
              {isLoading && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex justify-start"
                >
                  <div className="bg-[rgb(var(--card))] border border-[rgb(var(--border))] rounded-lg p-4">
                    <div className="flex space-x-2">
                      <div className="w-2 h-2 bg-[rgb(var(--primary))] rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                      <div className="w-2 h-2 bg-[rgb(var(--primary))] rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                      <div className="w-2 h-2 bg-[rgb(var(--primary))] rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                    </div>
                  </div>
                </motion.div>
              )}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Input Area */}
        <div className="bg-[rgb(var(--card))] border-t border-[rgb(var(--border))] p-4">
          <div className="max-w-4xl mx-auto flex gap-2">
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message... (Press Enter to send)"
              disabled={isLoading}
              className="flex-1 resize-none rounded-lg border border-[rgb(var(--border))] bg-[rgb(var(--background))] p-3 text-[rgb(var(--foreground))] placeholder:text-[rgb(var(--muted-foreground))] focus:outline-none focus:ring-2 focus:ring-[rgb(var(--primary))] disabled:opacity-50"
              rows={1}
              style={{ minHeight: '44px', maxHeight: '120px' }}
            />
            <Button
              onClick={handleSendMessage}
              disabled={!inputMessage.trim() || isLoading}
              variant="primary"
              className="px-6"
            >
              {isLoading ? 'Sending...' : 'Send'}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
