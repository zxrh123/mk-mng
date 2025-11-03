import { useMemo } from "react";
import { Activity, AlertTriangle, ShieldAlert } from "lucide-react";

import { TelemetryPayload } from "../hooks/useTelemetry";
import { strings } from "../lib/strings";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/Card";

interface NotificationCenterProps {
  telemetry?: TelemetryPayload;
}

export const NotificationCenter = ({ telemetry }: NotificationCenterProps) => {
  const notifications = useMemo(() => {
    if (!telemetry) {
      return [] as Array<{ title: string; detail: string; icon: "alert" | "activity" }>;
    }

    const items: Array<{ title: string; detail: string; icon: "alert" | "activity" }> = [];

    if ((telemetry.anomalies?.cpu_load ?? 0) > 0) {
      items.push({
        title: strings.notifications.cpuAlert,
        detail: `${Math.round((telemetry.anomalies?.cpu_load ?? 0) * 100)}%`,
        icon: "alert"
      });
    }

    if ((telemetry.anomalies?.memory_usage ?? 0) > 0) {
      items.push({
        title: strings.notifications.memoryAlert,
        detail: `${Math.round((telemetry.memory_usage ?? 0) * 100)}%`,
        icon: "alert"
      });
    }

    if ((telemetry.anomalies?.interfaces ?? 0) > 0) {
      items.push({
        title: strings.notifications.interfaceAlert,
        detail: `${telemetry.anomalies?.interfaces}`,
        icon: "activity"
      });
    }

    return items;
  }, [telemetry]);

  return (
    <Card>
      <CardHeader className="flex-row items-center justify-between">
        <CardTitle>{strings.notifications.title}</CardTitle>
        <span className="flex items-center gap-2 text-sm text-magenta">
          <ShieldAlert className="h-4 w-4" /> {strings.notifications.shieldActive}
        </span>
      </CardHeader>
      <CardContent className="space-y-4">
        {notifications.length === 0 && <p className="text-sm text-azure/70">{strings.notifications.noAlerts}</p>}
        {notifications.map((notification, index) => (
          <div
            key={index}
            className="flex items-center justify-between rounded-2xl border border-magenta/30 bg-magenta/10 px-4 py-3 text-sm text-white"
          >
            <div className="flex items-center gap-3">
              {notification.icon === "alert" ? (
                <AlertTriangle className="h-5 w-5 text-magenta" />
              ) : (
                <Activity className="h-5 w-5 text-neon" />
              )}
              <div>
                <p className="font-semibold">{notification.title}</p>
                <p className="text-xs text-azure/80">{notification.detail}</p>
              </div>
            </div>
            <button className="text-xs text-neon hover:underline">{strings.notifications.actionPlan}</button>
          </div>
        ))}
      </CardContent>
    </Card>
  );
};
