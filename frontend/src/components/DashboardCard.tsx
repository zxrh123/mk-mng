import { motion } from "framer-motion";
import { ReactNode } from "react";

import { Card, CardContent, CardHeader, CardTitle } from "./ui/Card";

interface DashboardCardProps {
  title: string;
  metric: string;
  trend?: string;
  icon?: ReactNode;
  footer?: ReactNode;
}

export const DashboardCard = ({ title, metric, trend, icon, footer }: DashboardCardProps) => (
  <motion.div
    initial={{ opacity: 0, y: 24 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.6, ease: "easeOut" }}
  >
    <Card className="h-full">
      <CardHeader>
        <div>
          <CardTitle className="text-base text-azure/80">{title}</CardTitle>
          <div className="flex items-center gap-3 pt-3 text-3xl font-bold text-white">
            <span>{metric}</span>
            {icon && <span className="text-neon">{icon}</span>}
          </div>
        </div>
        {trend && <span className="rounded-full bg-neon/15 px-4 py-1 text-sm text-neon">{trend}</span>}
      </CardHeader>
      {footer && <CardContent>{footer}</CardContent>}
    </Card>
  </motion.div>
);
