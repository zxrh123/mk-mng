import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Plus, Edit, Trash2, Power, Activity } from 'lucide-react'
import axios from 'axios'
import toast from 'react-hot-toast'

const Routers = () => {
  const [routers, setRouters] = useState([])
  const [showModal, setShowModal] = useState(false)
  const [editingRouter, setEditingRouter] = useState(null)
  const [formData, setFormData] = useState({
    name: '',
    host: '',
    username: '',
    password: '',
    description: '',
  })

  useEffect(() => {
    fetchRouters()
  }, [])

  const fetchRouters = async () => {
    try {
      const response = await axios.get('/api/v1/routers/')
      setRouters(response.data)
    } catch (error) {
      console.error('Error fetching routers:', error)
      toast.error('??? ?? ??? ????????')
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      if (editingRouter) {
        await axios.put(`/api/v1/routers/${editingRouter.id}`, formData)
        toast.success('?? ????? ??????? ?????')
      } else {
        await axios.post('/api/v1/routers/', formData)
        toast.success('?? ????? ??????? ?????')
      }
      setShowModal(false)
      setEditingRouter(null)
      setFormData({
        name: '',
        host: '',
        username: '',
        password: '',
        description: '',
      })
      fetchRouters()
    } catch (error) {
      console.error('Error saving router:', error)
      toast.error('??? ??? ????? ?????')
    }
  }

  const handleDelete = async (id) => {
    if (!confirm('?? ??? ????? ?? ??? ??? ????????')) return
    
    try {
      await axios.delete(`/api/v1/routers/${id}`)
      toast.success('?? ??? ??????? ?????')
      fetchRouters()
    } catch (error) {
      console.error('Error deleting router:', error)
      toast.error('??? ??? ????? ?????')
    }
  }

  const handleEdit = (router) => {
    setEditingRouter(router)
    setFormData({
      name: router.name,
      host: router.host,
      username: router.username,
      password: '', // Don't show password
      description: router.description || '',
    })
    setShowModal(true)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold mb-2 glow-text">????? ?????????</h1>
          <p className="text-gray-400">????? ?????? ????? MikroTik</p>
        </div>
        <button
          onClick={() => {
            setEditingRouter(null)
            setFormData({
              name: '',
              host: '',
              username: '',
              password: '',
              description: '',
            })
            setShowModal(true)
          }}
          className="px-6 py-3 bg-accent-cyan text-white rounded-lg hover:bg-accent-blue transition-colors flex items-center gap-2 glow-button"
        >
          <Plus className="w-5 h-5" />
          ????? ?????
        </button>
      </div>

      {/* Routers Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {routers.map((router, index) => (
          <motion.div
            key={router.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="glass-card p-6"
          >
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-accent-cyan/20 rounded-lg flex items-center justify-center">
                  <Activity className="w-6 h-6 text-accent-cyan" />
                </div>
                <div>
                  <h3 className="font-bold text-lg">{router.name}</h3>
                  <p className="text-sm text-gray-400">{router.host}</p>
                </div>
              </div>
              <div className={`w-3 h-3 rounded-full ${
                router.is_active ? 'bg-green-500' : 'bg-gray-500'
              }`}></div>
            </div>

            {router.description && (
              <p className="text-sm text-gray-400 mb-4">{router.description}</p>
            )}

            <div className="flex items-center gap-2">
              <button
                onClick={() => handleEdit(router)}
                className="flex-1 px-4 py-2 bg-glass-light hover:bg-glass-medium rounded-lg transition-colors flex items-center justify-center gap-2"
              >
                <Edit className="w-4 h-4" />
                ?????
              </button>
              <button
                onClick={() => handleDelete(router.id)}
                className="px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-lg transition-colors"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="glass-card p-6 w-full max-w-md"
          >
            <h2 className="text-2xl font-bold mb-6">
              {editingRouter ? '????? ?????' : '????? ????? ????'}
            </h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm mb-2">?????</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full bg-glass-light border border-white/10 rounded-lg px-4 py-2 focus:outline-none focus:border-accent-cyan"
                  required
                />
              </div>
              <div>
                <label className="block text-sm mb-2">????? IP</label>
                <input
                  type="text"
                  value={formData.host}
                  onChange={(e) => setFormData({ ...formData, host: e.target.value })}
                  className="w-full bg-glass-light border border-white/10 rounded-lg px-4 py-2 focus:outline-none focus:border-accent-cyan"
                  required
                />
              </div>
              <div>
                <label className="block text-sm mb-2">??? ????????</label>
                <input
                  type="text"
                  value={formData.username}
                  onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                  className="w-full bg-glass-light border border-white/10 rounded-lg px-4 py-2 focus:outline-none focus:border-accent-cyan"
                  required
                />
              </div>
              <div>
                <label className="block text-sm mb-2">???? ??????</label>
                <input
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  className="w-full bg-glass-light border border-white/10 rounded-lg px-4 py-2 focus:outline-none focus:border-accent-cyan"
                  required={!editingRouter}
                />
              </div>
              <div>
                <label className="block text-sm mb-2">????? (???????)</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full bg-glass-light border border-white/10 rounded-lg px-4 py-2 focus:outline-none focus:border-accent-cyan"
                  rows="3"
                />
              </div>
              <div className="flex gap-3">
                <button
                  type="submit"
                  className="flex-1 px-6 py-3 bg-accent-cyan text-white rounded-lg hover:bg-accent-blue transition-colors glow-button"
                >
                  {editingRouter ? '?????' : '?????'}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowModal(false)
                    setEditingRouter(null)
                  }}
                  className="px-6 py-3 bg-glass-light hover:bg-glass-medium rounded-lg transition-colors"
                >
                  ?????
                </button>
              </div>
            </form>
          </motion.div>
        </div>
      )}
    </div>
  )
}

export default Routers
