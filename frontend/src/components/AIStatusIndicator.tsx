import { motion } from "framer-motion";
import { BrainCircuit } from "lucide-react";

import { strings } from "../lib/strings";

interface AIStatusIndicatorProps {
  isThinking: boolean;
}

export const AIStatusIndicator = ({ isThinking }: AIStatusIndicatorProps) => (
  <motion.div
    className="flex items-center gap-3 rounded-full border border-magenta/40 bg-glass px-5 py-2 text-sm text-white shadow-neon/30"
    animate={{ opacity: isThinking ? [0.6, 1, 0.6] : 1 }}
    transition={{ duration: 1.2, repeat: isThinking ? Infinity : 0 }}
  >
    <BrainCircuit className="h-5 w-5 text-magenta" />
    <span>{isThinking ? strings.ai.thinking : strings.ai.ready}</span>
  </motion.div>
);
