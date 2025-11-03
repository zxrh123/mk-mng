import type { ReactNode } from "react";
import { motion } from "framer-motion";
import { BrainCircuit, Network } from "lucide-react";

export const HeroHeader = () => {
  return (
    <div className="relative overflow-hidden rounded-3xl border border-white/10 bg-gradient-to-br from-brand-dark/80 via-brand-dark to-brand-dark/60 p-8 shadow-xl backdrop-blur-md">
      <motion.div
        className="absolute inset-0 bg-grid-glow opacity-60"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1.2 }}
      />
      <div className="relative z-10 flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
        <div className="space-y-4">
          <motion.h1
            className="font-heading text-4xl font-semibold tracking-tight text-white/90 sm:text-5xl"
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.6 }}
          >
            ???? ???? ???? ?????? MikroTik ?????? ??? ????? ?????
          </motion.h1>
          <motion.p
            className="max-w-2xl text-lg text-white/70"
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.1 }}
          >
            ????? ????? ??????? ?????? ?????? ????? ?? ???? ?????? ?????. ??????? ???????
            ????? ?? ???????? ?????? ?? ?? ??? ?????? ????? ????????.
          </motion.p>
          <div className="flex flex-wrap gap-3 text-sm text-white/60">
            <Badge icon={<BrainCircuit size={16} />} label="AI-Driven Decisions" />
            <Badge icon={<Network size={16} />} label="Live RouterOS Telemetry" />
            <Badge label="Auto-Heal & Rollback" />
            <Badge label="Hotspot Conversational Assistant" />
          </div>
        </div>
        <motion.div
          className="rounded-2xl border border-white/10 bg-white/5 p-6 text-sm text-white/70 shadow-inner"
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <p>??? ????? ?????</p>
          <div className="mt-2 text-3xl font-semibold text-brand">Load balancing optimized</div>
          <p className="mt-1 text-xs text-white/50">??? ????? ????? ?????? Core AI Brain</p>
        </motion.div>
      </div>
    </div>
  );
};

const Badge = ({ icon, label }: { icon?: ReactNode; label: string }) => (
  <span className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/10 px-4 py-2 text-xs uppercase tracking-wide text-white">
    {icon}
    {label}
  </span>
);


