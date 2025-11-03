import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Activity, 
  Cpu, 
  HardDrive, 
  Wifi, 
  Users,
  TrendingUp,
  AlertTriangle
} from 'lucide-react'
import { Line, Doughnut } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import axios from 'axios'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

const Dashboard = () => {
  const [stats, setStats] = useState({
    totalRouters: 0,
    activeRouters: 0,
    totalUsers: 0,
    alerts: 0,
  })
  
  const [cpuData, setCpuData] = useState({
    labels: [],
    datasets: [{
      label: '??????? CPU',
      data: [],
      borderColor: '#00d9ff',
      backgroundColor: 'rgba(0, 217, 255, 0.1)',
      fill: true,
      tension: 0.4,
    }]
  })

  useEffect(() => {
    // Fetch dashboard data
    fetchDashboardData()
    
    // Update every 5 seconds
    const interval = setInterval(fetchDashboardData, 5000)
    return () => clearInterval(interval)
  }, [])

  const fetchDashboardData = async () => {
    try {
      const routersRes = await axios.get('/api/v1/routers/')
      const alertsRes = await axios.get('/api/v1/monitoring/alerts?is_resolved=false')
      
      setStats({
        totalRouters: routersRes.data.length,
        activeRouters: routersRes.data.filter(r => r.is_active).length,
        totalUsers: 0, // Would fetch from monitoring
        alerts: alertsRes.data.length,
      })
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
    }
  }

  const statCards = [
    {
      title: '?????? ?????????',
      value: stats.totalRouters,
      icon: Wifi,
      color: 'accent-cyan',
      change: '+2'
    },
    {
      title: '????????? ??????',
      value: stats.activeRouters,
      icon: Activity,
      color: 'accent-blue',
      change: '+1'
    },
    {
      title: '?????????? ???????',
      value: stats.totalUsers,
      icon: Users,
      color: 'accent-pink',
      change: '+12'
    },
    {
      title: '?????????',
      value: stats.alerts,
      icon: AlertTriangle,
      color: 'yellow-500',
      change: '-3'
    },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold mb-2 glow-text">???? ??????</h1>
        <p className="text-gray-400">???? ????? ??? ???? ??????</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat, index) => {
          const Icon = stat.icon
          return (
            <motion.div
              key={stat.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="glass-card p-6"
            >
              <div className="flex items-center justify-between mb-4">
                <div className={`p-3 rounded-lg bg-${stat.color}/20`}>
                  <Icon className={`w-6 h-6 text-${stat.color}`} />
                </div>
                <span className="text-sm text-green-400 flex items-center gap-1">
                  <TrendingUp className="w-4 h-4" />
                  {stat.change}
                </span>
              </div>
              <h3 className="text-2xl font-bold mb-1">{stat.value}</h3>
              <p className="text-sm text-gray-400">{stat.title}</p>
            </motion.div>
          )
        })}
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* CPU Usage Chart */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="glass-card p-6"
        >
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <Cpu className="w-5 h-5 text-accent-cyan" />
            ??????? ???????
          </h2>
          <div className="h-64">
            <Line 
              data={cpuData} 
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    display: false,
                  },
                },
                scales: {
                  y: {
                    beginAtZero: true,
                    max: 100,
                    grid: {
                      color: 'rgba(255, 255, 255, 0.1)',
                    },
                    ticks: {
                      color: '#fff',
                    },
                  },
                  x: {
                    grid: {
                      color: 'rgba(255, 255, 255, 0.1)',
                    },
                    ticks: {
                      color: '#fff',
                    },
                  },
                },
              }}
            />
          </div>
        </motion.div>

        {/* RAM Usage Chart */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="glass-card p-6"
        >
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <HardDrive className="w-5 h-5 text-accent-blue" />
            ??????? ???????
          </h2>
          <div className="h-64 flex items-center justify-center">
            <Doughnut
              data={{
                labels: ['??????', '????'],
                datasets: [{
                  data: [65, 35],
                  backgroundColor: ['#00d9ff', 'rgba(255, 255, 255, 0.1)'],
                  borderWidth: 0,
                }]
              }}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    position: 'bottom',
                    labels: {
                      color: '#fff',
                      font: {
                        family: 'Cairo',
                      },
                    },
                  },
                },
              }}
            />
          </div>
        </motion.div>
      </div>

      {/* Recent Activity */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card p-6"
      >
        <h2 className="text-xl font-bold mb-4">?????? ??????</h2>
        <div className="space-y-3">
          {[1, 2, 3, 4, 5].map((item) => (
            <div
              key={item}
              className="flex items-center justify-between p-3 bg-glass-light rounded-lg"
            >
              <div className="flex items-center gap-3">
                <div className="w-2 h-2 bg-accent-cyan rounded-full"></div>
                <span className="text-sm">?? ????? ???? ??????? Router-{item}</span>
              </div>
              <span className="text-xs text-gray-400">??? {item} ?????</span>
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  )
}

export default Dashboard
