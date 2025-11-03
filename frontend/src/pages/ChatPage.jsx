import { motion } from 'framer-motion'

export default function ChatPage() {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="text-center py-20"
    >
      <h1 className="text-4xl font-bold gradient-text mb-4">???? ????????</h1>
      <p className="text-gray-400">??? ???????...</p>
    </motion.div>
  )
}
