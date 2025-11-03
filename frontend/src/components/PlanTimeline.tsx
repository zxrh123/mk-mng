import { motion } from "framer-motion";
import { BadgeInfo, CheckCircle2, Code2, ExternalLink } from "lucide-react";

import { useAIStore } from "@/store/useAIStore";

export const PlanTimeline = () => {
  const { lastResponse, approveDecision, sending, error } = useAIStore();

  if (!lastResponse) {
    return (
      <div className="rounded-3xl border border-white/10 bg-white/5 p-6 text-sm text-white/60">
        <p>???? ?? ?????? ????? ???? ?????? ?? ????? ????? ????? ??? ????? ????????? ???.</p>
      </div>
    );
  }

  const { plan, script, metadata, auto_execute } = lastResponse;
  const canExecute = !auto_execute;

  return (
    <motion.div
      className="space-y-6 rounded-3xl border border-white/10 bg-white/5 p-6"
      initial={{ y: 12, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.4 }}
    >
      <header className="flex items-center justify-between">
        <div>
          <h3 className="font-heading text-lg text-white">??? ??????? ??????</h3>
          <p className="text-xs text-white/50">
            ?????: {plan.intent} ? ?????: {(plan.confidence * 100).toFixed(1)}%
          </p>
        </div>
        <button
          className="rounded-full border border-brand/30 bg-brand/10 px-4 py-2 text-xs uppercase tracking-wide text-brand transition hover:bg-brand/20 disabled:cursor-not-allowed disabled:opacity-50"
          onClick={() => approveDecision(metadata.decision_id)}
          disabled={sending || !canExecute}
        >
          {canExecute ? "????? ????" : "????? ?????? ???"}
        </button>
      </header>

      <ol className="space-y-4">
        {plan.steps.map((step, idx) => (
          <motion.li
            key={step.order}
            className="relative rounded-2xl border border-white/5 bg-black/20 p-4"
            initial={{ x: -10, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ delay: idx * 0.05 }}
          >
            <span className="absolute -left-3 top-5 inline-flex h-6 w-6 items-center justify-center rounded-full bg-brand text-xs text-white">
              {idx + 1}
            </span>
            <div className="ml-4 space-y-2">
              <div className="flex items-center gap-2 text-sm text-white">
                <CheckCircle2 className="h-4 w-4 text-brand" />
                <span>{step.description}</span>
              </div>
              {step.command_preview && (
                <code className="block rounded-xl bg-black/40 p-3 text-xs text-brand/80">
                  {step.command_preview}
                </code>
              )}
            </div>
          </motion.li>
        ))}
      </ol>

      {script && (
        <div className="space-y-3 rounded-2xl border border-white/5 bg-black/30 p-4">
          <div className="flex items-center gap-2 text-sm text-brand">
            <Code2 className="h-4 w-4" />
            ????? RouterOS ??????? (????: {script.safe ? "???" : "????? ??????"})
          </div>
          <pre className="overflow-x-auto rounded-xl bg-black/60 p-4 text-xs text-white/80">
            <code>{script.contents}</code>
          </pre>
        </div>
      )}

      <footer className="space-y-3 text-xs text-white/60">
        <div className="flex items-center gap-2">
          <BadgeInfo className="h-4 w-4" />
          <span>???? ??????: {metadata.decision_id}</span>
        </div>
        {metadata.knowledge.length > 0 && (
          <div className="space-y-2">
            <p className="text-xs uppercase tracking-wide text-white/50">??????? ?? ????? ???????</p>
            <ul className="space-y-2">
              {metadata.knowledge.map((snippet, idx) => (
                <li key={idx} className="rounded-lg bg-black/20 p-3 text-[0.7rem] text-white/70">
                  {snippet}...
                </li>
              ))}
            </ul>
          </div>
        )}
        <a
          className="inline-flex items-center gap-2 text-brand hover:text-brand-magenta"
          href="https://wiki.mikrotik.com/wiki/Main_Page"
          target="_blank"
          rel="noreferrer"
        >
          ????? ??????
          <ExternalLink className="h-4 w-4" />
        </a>
        {error && <p className="text-red-400">{error}</p>}
      </footer>
    </motion.div>
  );
};


