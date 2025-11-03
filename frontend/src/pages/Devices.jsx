import { motion } from 'framer-motion'
import { Server, Plus, Search, Wifi, Activity, AlertCircle } from 'lucide-react'
import { useState } from 'react'

const devices = [
  {
    id: 1,
    name: 'Router-01',
    ip: '192.168.1.1',
    model: 'RB4011iGS+',
    status: 'online',
    cpu: 45,
    memory: 60,
    uptime: '15 ???',
    users: 234
  },
  {
    id: 2,
    name: 'Router-02',
    ip: '192.168.2.1',
    model: 'CCR1036-12G-4S',
    status: 'online',
    cpu: 65,
    memory: 70,
    uptime: '30 ???',
    users: 456
  },
  {
    id: 3,
    name: 'Router-03',
    ip: '192.168.3.1',
    model: 'RB5009UG+S+',
    status: 'warning',
    cpu: 85,
    memory: 80,
    uptime: '7 ???',
    users: 123
  },
]

export default function Devices() {
  const [searchTerm, setSearchTerm] = useState('')
  
  const filteredDevices = devices.filter(device =>
    device.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    device.ip.includes(searchTerm)
  )
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-3xl font-bold gradient-text mb-2">
            ????? ???????
          </h1>
          <p className="text-gray-400">
            ??? ?????? ???? ????? MikroTik ???????
          </p>
        </div>
        
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="btn-primary"
        >
          <Plus className="w-5 h-5" />
          ????? ???? ????
        </motion.button>
      </motion.div>
      
      {/* Search and Filters */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="card"
      >
        <div className="flex items-center gap-4">
          <div className="flex-1 relative">
            <Search className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="???? ?? ???? ?????? ?? IP..."
              className="input pr-12"
            />
          </div>
          
          <button className="btn-secondary">
            <Server className="w-5 h-5" />
            ???? (12)
          </button>
          
          <button className="btn-secondary">
            <Wifi className="w-5 h-5" />
            ???? (10)
          </button>
          
          <button className="btn-secondary">
            <AlertCircle className="w-5 h-5" />
            ??????? (2)
          </button>
        </div>
      </motion.div>
      
      {/* Devices Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {filteredDevices.map((device, index) => (
          <motion.div
            key={device.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 + index * 0.1 }}
            whileHover={{ y: -5 }}
            className={`card cursor-pointer ${
              device.status === 'online' ? 'glow' :
              device.status === 'warning' ? 'border-yellow-500/50' :
              'border-red-500/50'
            }`}
          >
            {/* Device Header */}
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <motion.div
                  animate={device.status === 'online' ? {
                    scale: [1, 1.1, 1],
                  } : {}}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                  }}
                  className={`p-3 rounded-xl bg-gradient-to-br ${
                    device.status === 'online' ? 'from-green-500 to-green-600' :
                    device.status === 'warning' ? 'from-yellow-500 to-yellow-600' :
                    'from-red-500 to-red-600'
                  }`}
                >
                  <Server className="w-5 h-5" />
                </motion.div>
                
                <div>
                  <h3 className="font-bold text-lg">{device.name}</h3>
                  <p className="text-sm text-gray-400">{device.ip}</p>
                </div>
              </div>
              
              <span className={`badge ${
                device.status === 'online' ? 'badge-success' :
                device.status === 'warning' ? 'badge-warning' :
                'badge-error'
              }`}>
                {device.status === 'online' ? '????' :
                 device.status === 'warning' ? '?????' :
                 '??? ????'}
              </span>
            </div>
            
            {/* Device Info */}
            <div className="space-y-3 mb-4">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-400">???????:</span>
                <span className="font-medium">{device.model}</span>
              </div>
              
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-400">??? ???????:</span>
                <span className="font-medium">{device.uptime}</span>
              </div>
              
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-400">??????????:</span>
                <span className="font-medium">{device.users}</span>
              </div>
            </div>
            
            {/* Resource Usage */}
            <div className="space-y-3">
              <div>
                <div className="flex items-center justify-between text-xs mb-1">
                  <span className="text-gray-400">CPU</span>
                  <span className={`font-semibold ${
                    device.cpu > 80 ? 'text-red-500' :
                    device.cpu > 60 ? 'text-yellow-500' :
                    'text-green-500'
                  }`}>{device.cpu}%</span>
                </div>
                <div className="h-2 bg-dark-700 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${device.cpu}%` }}
                    transition={{ duration: 1, delay: 0.3 + index * 0.1 }}
                    className={`h-full rounded-full ${
                      device.cpu > 80 ? 'bg-gradient-to-r from-red-500 to-red-600' :
                      device.cpu > 60 ? 'bg-gradient-to-r from-yellow-500 to-yellow-600' :
                      'bg-gradient-to-r from-green-500 to-green-600'
                    }`}
                  />
                </div>
              </div>
              
              <div>
                <div className="flex items-center justify-between text-xs mb-1">
                  <span className="text-gray-400">???????</span>
                  <span className={`font-semibold ${
                    device.memory > 80 ? 'text-red-500' :
                    device.memory > 60 ? 'text-yellow-500' :
                    'text-cyan-500'
                  }`}>{device.memory}%</span>
                </div>
                <div className="h-2 bg-dark-700 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${device.memory}%` }}
                    transition={{ duration: 1, delay: 0.4 + index * 0.1 }}
                    className={`h-full rounded-full ${
                      device.memory > 80 ? 'bg-gradient-to-r from-red-500 to-red-600' :
                      device.memory > 60 ? 'bg-gradient-to-r from-yellow-500 to-yellow-600' :
                      'bg-gradient-to-r from-cyan-500 to-cyan-600'
                    }`}
                  />
                </div>
              </div>
            </div>
            
            {/* Actions */}
            <div className="flex gap-2 mt-4 pt-4 border-t border-white/10">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="flex-1 btn-secondary text-sm"
              >
                <Activity className="w-4 h-4" />
                ????????
              </motion.button>
              
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="flex-1 btn-secondary text-sm"
              >
                ?????
              </motion.button>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  )
}
