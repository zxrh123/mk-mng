import { NavLink } from 'react-router-dom'
import { motion } from 'framer-motion'
import { 
  LayoutDashboard, 
  Server, 
  Activity, 
  CheckSquare,
  MessageSquare,
  Settings,
  Brain
} from 'lucide-react'

const menuItems = [
  { path: '/', icon: LayoutDashboard, label: '???? ??????' },
  { path: '/devices', icon: Server, label: '???????' },
  { path: '/monitoring', icon: Activity, label: '????????' },
  { path: '/tasks', icon: CheckSquare, label: '??????' },
  { path: '/chat', icon: MessageSquare, label: '????????' },
  { path: '/settings', icon: Settings, label: '?????????' },
]

export default function Sidebar() {
  return (
    <motion.aside
      initial={{ x: -100, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.3 }}
      className="w-64 glass-dark border-l border-white/5 flex flex-col"
    >
      {/* Logo */}
      <div className="p-6 border-b border-white/5">
        <div className="flex items-center gap-3">
          <motion.div
            animate={{
              rotate: [0, 360],
              scale: [1, 1.1, 1],
            }}
            transition={{
              duration: 3,
              repeat: Infinity,
              ease: "linear"
            }}
            className="p-3 rounded-xl bg-gradient-to-br from-cyan-500 to-primary-600 ai-brain-glow"
          >
            <Brain className="w-6 h-6" />
          </motion.div>
          <div>
            <h1 className="text-xl font-bold gradient-text">
              MikroTik AI
            </h1>
            <p className="text-xs text-gray-400">????? ????</p>
          </div>
        </div>
      </div>
      
      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {menuItems.map((item, index) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.path === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-300 ${
                isActive
                  ? 'bg-gradient-to-r from-primary-600 to-primary-700 glow text-white'
                  : 'hover:bg-white/5 text-gray-300 hover:text-white'
              }`
            }
          >
            {({ isActive }) => (
              <motion.div
                initial={{ x: -20, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: index * 0.05 }}
                className="flex items-center gap-3 w-full"
              >
                <item.icon className="w-5 h-5" />
                <span className="font-medium">{item.label}</span>
                
                {isActive && (
                  <motion.div
                    layoutId="activeIndicator"
                    className="mr-auto w-2 h-2 rounded-full bg-white"
                    transition={{ type: "spring", stiffness: 300, damping: 30 }}
                  />
                )}
              </motion.div>
            )}
          </NavLink>
        ))}
      </nav>
      
      {/* System Status */}
      <div className="p-4 border-t border-white/5">
        <motion.div 
          className="glass rounded-lg p-4"
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          <div className="flex items-center gap-3 mb-3">
            <div className="relative">
              <div className="w-3 h-3 rounded-full bg-green-500"></div>
              <div className="absolute inset-0 w-3 h-3 rounded-full bg-green-500 pulse-ring"></div>
            </div>
            <span className="text-sm font-semibold">?????? ???</span>
          </div>
          
          <div className="space-y-2 text-xs text-gray-400">
            <div className="flex justify-between">
              <span>????????:</span>
              <span className="text-green-400">????</span>
            </div>
            <div className="flex justify-between">
              <span>?????? ???????:</span>
              <span className="text-cyan-400">???</span>
            </div>
          </div>
        </motion.div>
      </div>
    </motion.aside>
  )
}
