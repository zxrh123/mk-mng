import { motion } from 'framer-motion'
import { Bell, Search, User, Moon, Sun } from 'lucide-react'
import { useState } from 'react'

export default function Header() {
  const [isDark, setIsDark] = useState(true)
  
  return (
    <motion.header
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.3 }}
      className="glass-dark border-b border-white/5 px-6 py-4"
    >
      <div className="flex items-center justify-between">
        {/* Search */}
        <div className="flex-1 max-w-xl">
          <div className="relative">
            <Search className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="???? ?? ????? ????? ?? ???..."
              className="input pr-12"
            />
          </div>
        </div>
        
        {/* Actions */}
        <div className="flex items-center gap-4">
          {/* Theme Toggle */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setIsDark(!isDark)}
            className="p-3 glass rounded-lg hover:bg-white/10 transition-colors"
          >
            {isDark ? <Moon className="w-5 h-5" /> : <Sun className="w-5 h-5" />}
          </motion.button>
          
          {/* Notifications */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="relative p-3 glass rounded-lg hover:bg-white/10 transition-colors"
          >
            <Bell className="w-5 h-5" />
            <span className="absolute top-2 left-2 w-2 h-2 bg-red-500 rounded-full animate-pulse"></span>
          </motion.button>
          
          {/* User Menu */}
          <motion.div
            whileHover={{ scale: 1.05 }}
            className="flex items-center gap-3 glass rounded-lg px-4 py-2 cursor-pointer hover:bg-white/10 transition-colors"
          >
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-500 to-primary-600 flex items-center justify-center">
              <User className="w-4 h-4" />
            </div>
            <div className="text-right">
              <p className="text-sm font-semibold">???????</p>
              <p className="text-xs text-gray-400">???? ??????</p>
            </div>
          </motion.div>
        </div>
      </div>
    </motion.header>
  )
}
