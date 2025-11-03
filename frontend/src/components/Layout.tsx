import { PropsWithChildren } from "react";
import { ShieldHalf, Cpu, BotIcon } from "lucide-react";

import { cn } from "../lib/utils";
import { strings } from "../lib/strings";

interface LayoutProps extends PropsWithChildren {
  className?: string;
}

export const Layout = ({ children, className }: LayoutProps) => (
  <div className="min-h-screen w-full overflow-hidden">
    <header className="relative z-10 border-b border-azure/20 bg-midnight/60 backdrop-blur-xl">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-8 py-6">
          <div className="flex items-center gap-4 text-neon">
            <div className="rounded-full bg-neon/20 p-3">
              <BotIcon className="h-7 w-7" />
            </div>
            <div>
              <h1 className="text-2xl font-bold">{strings.layout.title}</h1>
              <p className="text-sm text-azure/80">{strings.layout.tagline}</p>
            </div>
          </div>
          <div className="flex items-center gap-5 text-sm font-semibold text-white/80">
            <span className="flex items-center gap-2"><Cpu className="h-5 w-5 text-neon" />{strings.layout.systemStatus}</span>
            <span className="flex items-center gap-2"><ShieldHalf className="h-5 w-5 text-magenta" />{strings.layout.shieldStatus}</span>
          </div>
      </div>
    </header>
    <main className={cn("relative z-0 mx-auto max-w-7xl px-8 py-10", className)}>
      <div className="absolute inset-0 -z-10 bg-grid" />
      {children}
    </main>
  </div>
);
