import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, Bot, User, Loader, Sparkles } from 'lucide-react'
import axios from 'axios'
import toast from 'react-hot-toast'

const Chat = () => {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId] = useState(`session_${Date.now()}`)
  const messagesEndRef = useRef(null)
  const wsRef = useRef(null)

  useEffect(() => {
    // Initialize WebSocket connection
    const ws = new WebSocket('ws://localhost:8000/ws')
    wsRef.current = ws

    ws.onopen = () => {
      console.log('WebSocket connected')
      toast.success('?? ??????? ?????')
    }

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      
      if (data.type === 'chat_response') {
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: data.message,
          execution_plan: data.execution_plan,
          timestamp: new Date(),
        }])
        setIsLoading(false)
      }
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      toast.error('??? ?? ???????')
    }

    ws.onclose = () => {
      console.log('WebSocket disconnected')
    }

    return () => {
      ws.close()
    }
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    const userMessage = {
      role: 'user',
      content: input,
      timestamp: new Date(),
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      // Send via WebSocket
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({
          type: 'chat',
          message: input,
          session_id: sessionId,
          context: {},
        }))
      } else {
        // Fallback to HTTP
        const response = await axios.post('/api/v1/chat/', {
          message: input,
          session_id: sessionId,
        })

        setMessages(prev => [...prev, {
          role: 'assistant',
          content: response.data.response,
          execution_plan: response.data.execution_plan,
          timestamp: new Date(),
        }])
        setIsLoading(false)
      }
    } catch (error) {
      console.error('Error sending message:', error)
      toast.error('??? ??? ????? ????? ???????')
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2 glow-text flex items-center gap-3">
          <Sparkles className="w-8 h-8 text-accent-cyan" />
          ???????? ??????
        </h1>
        <p className="text-gray-400">???? ?? ?????? ??????? ?????? ?????</p>
      </div>

      {/* Chat Container */}
      <div className="flex-1 glass-card p-6 flex flex-col">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto space-y-4 mb-6">
          <AnimatePresence>
            {messages.length === 0 && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-center text-gray-400 py-12"
              >
                <Bot className="w-16 h-16 mx-auto mb-4 text-accent-cyan opacity-50" />
                <p>???? ???????? ?? ?????? ???????</p>
                <p className="text-sm mt-2">???? ?? ???? ??????? ?? ???? ????? ??? ????</p>
              </motion.div>
            )}

            {messages.map((message, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex gap-4 ${message.role === 'user' ? 'flex-row-reverse' : ''}`}
              >
                <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${
                  message.role === 'user' 
                    ? 'bg-accent-blue' 
                    : 'bg-accent-cyan'
                }`}>
                  {message.role === 'user' ? (
                    <User className="w-5 h-5 text-white" />
                  ) : (
                    <Bot className="w-5 h-5 text-white" />
                  )}
                </div>
                <div className={`flex-1 ${message.role === 'user' ? 'text-left' : ''}`}>
                  <div className={`inline-block p-4 rounded-2xl ${
                    message.role === 'user'
                      ? 'bg-accent-blue/20 border border-accent-blue/30'
                      : 'bg-glass-light border border-white/10'
                  }`}>
                    <p className="text-white whitespace-pre-wrap">{message.content}</p>
                    {message.execution_plan && (
                      <div className="mt-3 pt-3 border-t border-white/10">
                        <p className="text-xs text-gray-400 mb-2">??? ???????:</p>
                        <pre className="text-xs bg-black/30 p-2 rounded overflow-x-auto">
                          {JSON.stringify(message.execution_plan, null, 2)}
                        </pre>
                      </div>
                    )}
                  </div>
                  <span className="text-xs text-gray-500 mt-1 block">
                    {new Date(message.timestamp).toLocaleTimeString('ar-SA')}
                  </span>
                </div>
              </motion.div>
            ))}

            {isLoading && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex gap-4"
              >
                <div className="w-10 h-10 rounded-full bg-accent-cyan flex items-center justify-center">
                  <Bot className="w-5 h-5 text-white" />
                </div>
                <div className="flex items-center gap-2 p-4 bg-glass-light rounded-2xl">
                  <Loader className="w-4 h-4 animate-spin text-accent-cyan" />
                  <span className="text-gray-400">???? ???????...</span>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="???? ?????? ???..."
            className="flex-1 bg-glass-light border border-white/10 rounded-lg px-4 py-3 focus:outline-none focus:border-accent-cyan transition-colors"
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="px-6 py-3 bg-accent-cyan text-white rounded-lg hover:bg-accent-blue transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 glow-button"
          >
            <Send className="w-5 h-5" />
            ?????
          </button>
        </div>
      </div>
    </div>
  )
}

export default Chat
