import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Activity, AlertTriangle, CheckCircle, Clock } from 'lucide-react'
import axios from 'axios'
import toast from 'react-hot-toast'

const Monitoring = () => {
  const [routers, setRouters] = useState([])
  const [selectedRouter, setSelectedRouter] = useState(null)
  const [status, setStatus] = useState(null)
  const [alerts, setAlerts] = useState([])

  useEffect(() => {
    fetchRouters()
    fetchAlerts()
  }, [])

  useEffect(() => {
    if (selectedRouter) {
      fetchRouterStatus(selectedRouter)
      const interval = setInterval(() => fetchRouterStatus(selectedRouter), 5000)
      return () => clearInterval(interval)
    }
  }, [selectedRouter])

  const fetchRouters = async () => {
    try {
      const response = await axios.get('/api/v1/routers/')
      setRouters(response.data)
      if (response.data.length > 0 && !selectedRouter) {
        setSelectedRouter(response.data[0].id)
      }
    } catch (error) {
      console.error('Error fetching routers:', error)
    }
  }

  const fetchRouterStatus = async (routerId) => {
    try {
      const response = await axios.get(`/api/v1/monitoring/routers/${routerId}/status`)
      setStatus(response.data)
    } catch (error) {
      console.error('Error fetching status:', error)
      toast.error('??? ?? ??? ???? ???????')
    }
  }

  const fetchAlerts = async () => {
    try {
      const response = await axios.get('/api/v1/monitoring/alerts?is_resolved=false')
      setAlerts(response.data)
    } catch (error) {
      console.error('Error fetching alerts:', error)
    }
  }

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical':
        return 'text-red-500 bg-red-500/20'
      case 'error':
        return 'text-red-400 bg-red-400/20'
      case 'warning':
        return 'text-yellow-400 bg-yellow-400/20'
      default:
        return 'text-blue-400 bg-blue-400/20'
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold mb-2 glow-text">???????? ???????</h1>
        <p className="text-gray-400">?????? ???? ????????? ???????</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Router Selection & Status */}
        <div className="lg:col-span-2 space-y-6">
          {/* Router Selector */}
          <div className="glass-card p-6">
            <h2 className="text-xl font-bold mb-4">???? ???????</h2>
            <div className="grid grid-cols-2 gap-3">
              {routers.map((router) => (
                <button
                  key={router.id}
                  onClick={() => setSelectedRouter(router.id)}
                  className={`p-4 rounded-lg border transition-all ${
                    selectedRouter === router.id
                      ? 'bg-accent-cyan/20 border-accent-cyan'
                      : 'bg-glass-light border-white/10 hover:border-accent-cyan/50'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-medium">{router.name}</span>
                    <div className={`w-2 h-2 rounded-full ${
                      router.is_active ? 'bg-green-500' : 'bg-gray-500'
                    }`}></div>
                  </div>
                  <p className="text-sm text-gray-400 mt-1">{router.host}</p>
                </button>
              ))}
            </div>
          </div>

          {/* Status Details */}
          {status && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="glass-card p-6"
            >
              <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                <Activity className="w-5 h-5 text-accent-cyan" />
                ???? ??????
              </h2>

              {/* Resources */}
              {status.resources && (
                <div className="grid grid-cols-3 gap-4 mb-6">
                  <div className="bg-glass-light p-4 rounded-lg">
                    <p className="text-sm text-gray-400 mb-1">???????</p>
                    <p className="text-2xl font-bold">{status.resources.cpu_load || 0}%</p>
                  </div>
                  <div className="bg-glass-light p-4 rounded-lg">
                    <p className="text-sm text-gray-400 mb-1">???????</p>
                    <p className="text-2xl font-bold">
                      {status.resources.total_memory 
                        ? Math.round((status.resources.used_memory / status.resources.total_memory) * 100)
                        : 0}%
                    </p>
                  </div>
                  <div className="bg-glass-light p-4 rounded-lg">
                    <p className="text-sm text-gray-400 mb-1">??????????</p>
                    <p className="text-2xl font-bold">{status.hotspot_users?.length || 0}</p>
                  </div>
                </div>
              )}

              {/* Interfaces */}
              {status.interfaces && (
                <div>
                  <h3 className="font-bold mb-3">?????? ??????</h3>
                  <div className="space-y-2">
                    {status.interfaces.map((iface, index) => (
                      <div
                        key={index}
                        className="bg-glass-light p-3 rounded-lg flex items-center justify-between"
                      >
                        <div>
                          <span className="font-medium">{iface.name}</span>
                          <span className="text-sm text-gray-400 mr-2">({iface.type})</span>
                        </div>
                        <div className="flex items-center gap-2">
                          {iface.running ? (
                            <CheckCircle className="w-4 h-4 text-green-500" />
                          ) : (
                            <AlertTriangle className="w-4 h-4 text-red-500" />
                          )}
                          <span className={`text-sm ${
                            iface.running ? 'text-green-400' : 'text-red-400'
                          }`}>
                            {iface.running ? '???' : '????'}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </motion.div>
          )}
        </div>

        {/* Alerts Sidebar */}
        <div className="space-y-6">
          <div className="glass-card p-6">
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-yellow-400" />
              ?????????
            </h2>
            <div className="space-y-3">
              {alerts.length === 0 ? (
                <p className="text-gray-400 text-sm text-center py-4">?? ???? ???????</p>
              ) : (
                alerts.map((alert) => (
                  <div
                    key={alert.id}
                    className={`p-3 rounded-lg ${getSeverityColor(alert.severity)}`}
                  >
                    <div className="flex items-start justify-between mb-1">
                      <span className="font-medium text-sm">{alert.alert_type}</span>
                      <Clock className="w-3 h-3" />
                    </div>
                    <p className="text-xs">{alert.message}</p>
                    <p className="text-xs opacity-70 mt-1">
                      {new Date(alert.created_at).toLocaleString('ar-SA')}
                    </p>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Monitoring
