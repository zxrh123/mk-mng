import { motion } from 'framer-motion'
import { 
  Server, 
  Activity, 
  Users, 
  Zap,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  Clock
} from 'lucide-react'
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

// Sample data
const performanceData = [
  { time: '00:00', cpu: 45, memory: 60, bandwidth: 120 },
  { time: '04:00', cpu: 35, memory: 55, bandwidth: 90 },
  { time: '08:00', cpu: 75, memory: 70, bandwidth: 200 },
  { time: '12:00', cpu: 85, memory: 75, bandwidth: 250 },
  { time: '16:00', cpu: 70, memory: 68, bandwidth: 180 },
  { time: '20:00', cpu: 60, memory: 65, bandwidth: 150 },
]

const stats = [
  {
    title: '??????? ??????',
    value: '12',
    change: '+2',
    icon: Server,
    color: 'from-cyan-500 to-cyan-600',
    glow: 'glow-cyan'
  },
  {
    title: '?????????? ????????',
    value: '1,234',
    change: '+156',
    icon: Users,
    color: 'from-primary-500 to-primary-600',
    glow: 'glow'
  },
  {
    title: '??? ??????',
    value: '2.4 GB/s',
    change: '+12%',
    icon: Activity,
    color: 'from-fuchsia-500 to-fuchsia-600',
    glow: 'glow-fuchsia'
  },
  {
    title: '??? ???????',
    value: '99.9%',
    change: '?????',
    icon: Zap,
    color: 'from-green-500 to-green-600',
    glow: 'glow'
  },
]

const recentAlerts = [
  { id: 1, type: 'warning', message: '??????? CPU ????? ?? ?????? RT-01', time: '5 ?????' },
  { id: 2, type: 'success', message: '?? ?? ????? ??????? ?? ?????? RT-03', time: '15 ?????' },
  { id: 3, type: 'info', message: '????? RouterOS ???? ?????? RT-05', time: '1 ????' },
]

const recentTasks = [
  { id: 1, title: '????? Firewall ?????? RT-01', status: 'completed', time: '10 ?????' },
  { id: 2, title: '????? ??? ?????? ?????? RT-02', status: 'running', time: '???? ???????' },
  { id: 3, title: '??? ??????? ????? ???????', status: 'pending', time: '??? ????????' },
]

export default function Dashboard() {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-3xl font-bold gradient-text mb-2">
            ???? ?????? ????????
          </h1>
          <p className="text-gray-400">
            ???? ????? ??? ???? ?????? ????? ???????
          </p>
        </div>
        
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="btn-primary"
        >
          <TrendingUp className="w-5 h-5" />
          ????? ????
        </motion.button>
      </motion.div>
      
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <motion.div
            key={stat.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className={`card ${stat.glow} hover:scale-105`}
          >
            <div className="flex items-center justify-between mb-4">
              <div className={`p-3 rounded-xl bg-gradient-to-br ${stat.color}`}>
                <stat.icon className="w-6 h-6" />
              </div>
              <span className="badge badge-success">{stat.change}</span>
            </div>
            
            <h3 className="text-2xl font-bold mb-1">{stat.value}</h3>
            <p className="text-gray-400 text-sm">{stat.title}</p>
          </motion.div>
        ))}
      </div>
      
      {/* Charts Section */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        {/* Performance Chart */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="card"
        >
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold">???? ??????</h2>
            <div className="flex gap-2">
              <span className="badge badge-info">CPU</span>
              <span className="badge badge-success">???????</span>
            </div>
          </div>
          
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={performanceData}>
              <defs>
                <linearGradient id="colorCpu" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="colorMemory" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#22d3ee" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#22d3ee" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis dataKey="time" stroke="#666" />
              <YAxis stroke="#666" />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1a1a1a',
                  border: '1px solid #333',
                  borderRadius: '8px'
                }}
              />
              <Area 
                type="monotone" 
                dataKey="cpu" 
                stroke="#3b82f6" 
                fillOpacity={1} 
                fill="url(#colorCpu)" 
              />
              <Area 
                type="monotone" 
                dataKey="memory" 
                stroke="#22d3ee" 
                fillOpacity={1} 
                fill="url(#colorMemory)" 
              />
            </AreaChart>
          </ResponsiveContainer>
        </motion.div>
        
        {/* Bandwidth Chart */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
          className="card"
        >
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold">??? ?????? ???????</h2>
            <span className="badge badge-info">MB/s</span>
          </div>
          
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={performanceData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis dataKey="time" stroke="#666" />
              <YAxis stroke="#666" />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1a1a1a',
                  border: '1px solid #333',
                  borderRadius: '8px'
                }}
              />
              <Line 
                type="monotone" 
                dataKey="bandwidth" 
                stroke="#d946ef" 
                strokeWidth={3}
                dot={{ fill: '#d946ef', r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </motion.div>
      </div>
      
      {/* Recent Activities */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        {/* Recent Alerts */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="card"
        >
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-yellow-500" />
              ????????? ???????
            </h2>
            <button className="text-sm text-primary-500 hover:text-primary-400">
              ??? ????
            </button>
          </div>
          
          <div className="space-y-3">
            {recentAlerts.map((alert, index) => (
              <motion.div
                key={alert.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.5 + index * 0.1 }}
                className="glass p-4 rounded-lg hover:bg-white/10 transition-colors cursor-pointer"
              >
                <div className="flex items-start gap-3">
                  <div className={`p-2 rounded-lg ${
                    alert.type === 'warning' ? 'bg-yellow-500/20 text-yellow-500' :
                    alert.type === 'success' ? 'bg-green-500/20 text-green-500' :
                    'bg-cyan-500/20 text-cyan-500'
                  }`}>
                    {alert.type === 'warning' && <AlertTriangle className="w-4 h-4" />}
                    {alert.type === 'success' && <CheckCircle className="w-4 h-4" />}
                    {alert.type === 'info' && <Clock className="w-4 h-4" />}
                  </div>
                  
                  <div className="flex-1">
                    <p className="text-sm font-medium mb-1">{alert.message}</p>
                    <p className="text-xs text-gray-400">??? {alert.time}</p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
        
        {/* Recent Tasks */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="card"
        >
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-green-500" />
              ?????? ???????
            </h2>
            <button className="text-sm text-primary-500 hover:text-primary-400">
              ??? ????
            </button>
          </div>
          
          <div className="space-y-3">
            {recentTasks.map((task, index) => (
              <motion.div
                key={task.id}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.6 + index * 0.1 }}
                className="glass p-4 rounded-lg hover:bg-white/10 transition-colors cursor-pointer"
              >
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm font-medium">{task.title}</p>
                  <span className={`badge ${
                    task.status === 'completed' ? 'badge-success' :
                    task.status === 'running' ? 'badge-info' :
                    'badge-warning'
                  }`}>
                    {task.status === 'completed' ? '??????' :
                     task.status === 'running' ? '??? ???????' :
                     '??? ????????'}
                  </span>
                </div>
                <p className="text-xs text-gray-400">{task.time}</p>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  )
}
