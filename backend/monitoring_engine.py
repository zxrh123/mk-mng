"""
?? Monitoring Engine - ???? ????????
????? ?? ?????? ???? ??????? ???? ??????? ????????
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Device, DeviceMetric, Alert, AlertSeverity, DeviceStatus, Interface
from mikrotik_connector import connection_pool
from core_ai_brain import ai_brain
from config import settings

logger = logging.getLogger(__name__)

class MonitoringEngine:
    """
    ???? ???????? ???????? ???????
    Continuous Device Monitoring Engine
    """
    
    def __init__(self):
        self.monitoring_tasks = {}
        self.is_running = False
        
    async def start(self, db: AsyncSession) -> None:
        """
        ??? ????????
        Start monitoring
        """
        self.is_running = True
        logger.info("?? Monitoring Engine started")
        
        # ??? ???? ???????? ????????
        asyncio.create_task(self._main_monitoring_loop(db))
    
    async def stop(self) -> None:
        """
        ????? ????????
        Stop monitoring
        """
        self.is_running = False
        logger.info("? Monitoring Engine stopped")
    
    async def _main_monitoring_loop(self, db: AsyncSession) -> None:
        """
        ???? ???????? ????????
        Main monitoring loop
        """
        while self.is_running:
            try:
                # ?????? ??? ???? ??????? ??????
                result = await db.execute(
                    select(Device).where(Device.status != DeviceStatus.MAINTENANCE)
                )
                devices = result.scalars().all()
                
                # ?????? ?? ????
                monitoring_tasks = [
                    self._monitor_device(db, device) 
                    for device in devices
                ]
                
                await asyncio.gather(*monitoring_tasks, return_exceptions=True)
                
                # ???????? ??? ?????? ???????
                await asyncio.sleep(settings.MONITORING_INTERVAL)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5)
    
    async def _monitor_device(self, db: AsyncSession, device: Device) -> None:
        """
        ?????? ???? ????
        Monitor single device
        """
        try:
            # ?????? ??? ??????
            connector = await connection_pool.get_connector(
                device_id=device.id,
                host=device.ip_address,
                username=device.username,
                password=device.encrypted_password,  # ??? ?? ???????
                port=device.ssh_port
            )
            
            # ?????? ???????
            connected = await connector.connect()
            
            if not connected:
                await self._handle_device_offline(db, device)
                return
            
            # ????? ???? ?????? ??? ????
            device.status = DeviceStatus.ONLINE
            device.last_seen = datetime.now()
            
            # ??? ????????
            metrics = await self._collect_metrics(connector, device)
            
            # ??? ???????? ?? ????? ????????
            device_metric = DeviceMetric(
                device_id=device.id,
                **metrics
            )
            db.add(device_metric)
            
            # ????? ???????? ???? ???????
            await self._analyze_metrics(db, device, metrics)
            
            # ??? ??????? ????????
            await self._collect_interfaces(db, connector, device)
            
            await db.commit()
            
            logger.debug(f"? Monitored device: {device.name} ({device.ip_address})")
            
        except Exception as e:
            logger.error(f"Error monitoring device {device.name}: {e}")
            device.status = DeviceStatus.ERROR
            await db.commit()
    
    async def _collect_metrics(
        self, 
        connector, 
        device: Device
    ) -> Dict[str, Any]:
        """
        ??? ???????? ?? ??????
        Collect metrics from device
        """
        try:
            # ?????? ??? ????? ??????
            resources = await connector.get_system_resources()
            
            # ?????? ??? ??? ?????????? ???????
            active_users = len(await connector.get_hotspot_users())
            
            # ?????? ???????
            ping_result = await connector.ping_test('8.8.8.8', count=2)
            
            metrics = {
                "cpu_load": resources.get('cpu_load', 0),
                "memory_used": resources.get('memory_used_percent', 0),
                "memory_total": resources.get('total_memory', 0),
                "uptime": resources.get('uptime', ''),
                "active_users": active_users,
                "latency": ping_result.get('avg_latency', 0),
                "packet_loss": ping_result.get('packet_loss', 0),
                "temperature": resources.get('cpu_temperature', 0),
                "voltage": resources.get('voltage', 0)
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
            return {}
    
    async def _collect_interfaces(
        self,
        db: AsyncSession,
        connector,
        device: Device
    ) -> None:
        """
        ??? ??????? ????????
        Collect interfaces information
        """
        try:
            interfaces_data = await connector.get_interfaces()
            
            for iface_data in interfaces_data:
                # ????? ?? ??????? ???????? ?? ????? ?????
                result = await db.execute(
                    select(Interface).where(
                        Interface.device_id == device.id,
                        Interface.name == iface_data['name']
                    )
                )
                interface = result.scalar_one_or_none()
                
                if interface:
                    # ????? ????????
                    for key, value in iface_data.items():
                        setattr(interface, key, value)
                else:
                    # ????? ????? ?????
                    interface = Interface(
                        device_id=device.id,
                        **iface_data
                    )
                    db.add(interface)
            
        except Exception as e:
            logger.error(f"Error collecting interfaces: {e}")
    
    async def _analyze_metrics(
        self,
        db: AsyncSession,
        device: Device,
        metrics: Dict[str, Any]
    ) -> None:
        """
        ????? ???????? ???? ???????
        Analyze metrics and detect issues
        """
        alerts = []
        
        # ??? ??????? CPU
        cpu_load = metrics.get('cpu_load', 0)
        if cpu_load > settings.ALERT_THRESHOLD_CPU:
            alerts.append({
                "severity": AlertSeverity.WARNING if cpu_load < 95 else AlertSeverity.CRITICAL,
                "title": "??????? CPU ?????",
                "message": f"??????? CPU ??? ??? {cpu_load}%",
                "alert_type": "performance",
                "metadata": {"cpu_load": cpu_load}
            })
        
        # ??? ??????? ???????
        memory_used = metrics.get('memory_used', 0)
        if memory_used > settings.ALERT_THRESHOLD_RAM:
            alerts.append({
                "severity": AlertSeverity.WARNING if memory_used < 95 else AlertSeverity.CRITICAL,
                "title": "??????? ??????? ?????",
                "message": f"??????? ??????? ??? ??? {memory_used}%",
                "alert_type": "performance",
                "metadata": {"memory_used": memory_used}
            })
        
        # ??? ??? ?????????
        latency = metrics.get('latency', 0)
        if latency > settings.ALERT_THRESHOLD_LATENCY:
            alerts.append({
                "severity": AlertSeverity.WARNING,
                "title": "??? ??????? ?????",
                "message": f"??? ?????????: {latency}ms",
                "alert_type": "connectivity",
                "metadata": {"latency": latency}
            })
        
        # ??? ????? ?????
        packet_loss = metrics.get('packet_loss', 0)
        if packet_loss > 5:
            alerts.append({
                "severity": AlertSeverity.ERROR if packet_loss > 20 else AlertSeverity.WARNING,
                "title": "????? ??? ????????",
                "message": f"????? ?????: {packet_loss}%",
                "alert_type": "connectivity",
                "metadata": {"packet_loss": packet_loss}
            })
        
        # ??? ?????????
        for alert_data in alerts:
            alert = Alert(
                device_id=device.id,
                **alert_data
            )
            db.add(alert)
            logger.warning(f"?? Alert: {alert_data['title']} - {device.name}")
        
        # ??? ???? ???? ????? ????? ????? ??????? ??????
        critical_alerts = [a for a in alerts if a['severity'] == AlertSeverity.CRITICAL]
        if critical_alerts and settings.ENABLE_AUTO_HEAL:
            await self._trigger_auto_heal(db, device, metrics, alerts)
    
    async def _handle_device_offline(self, db: AsyncSession, device: Device) -> None:
        """
        ??????? ?? ???? ??? ????
        Handle offline device
        """
        device.status = DeviceStatus.OFFLINE
        
        # ????? ?????
        alert = Alert(
            device_id=device.id,
            severity=AlertSeverity.ERROR,
            title="?????? ??? ????",
            message=f"??? ??????? ??????? {device.name} ({device.ip_address})",
            alert_type="connectivity",
            metadata={"last_seen": device.last_seen.isoformat() if device.last_seen else None}
        )
        db.add(alert)
        
        await db.commit()
        logger.error(f"? Device offline: {device.name} ({device.ip_address})")
    
    async def _trigger_auto_heal(
        self,
        db: AsyncSession,
        device: Device,
        metrics: Dict[str, Any],
        alerts: List[Dict]
    ) -> None:
        """
        ????? ??????? ??????
        Trigger auto-heal
        """
        logger.info(f"?? Triggering auto-heal for device: {device.name}")
        
        # ????? ??????? ???????
        issue = {
            "description": f"????? ???? ?? ???? {device.name}",
            "metrics": metrics,
            "alerts": alerts
        }
        
        # ??????? ????? ??????? ??????? ??????
        heal_result = await ai_brain.auto_heal(device.id, issue)
        
        if heal_result.get('success'):
            logger.info(f"? Auto-heal successful for {device.name}")
            
            # ????? ????? ???????
            alert = Alert(
                device_id=device.id,
                severity=AlertSeverity.INFO,
                title="??????? ?????? ???",
                message=f"?? ????? ??????? ???????? ?? ???? {device.name}",
                alert_type="system",
                metadata=heal_result
            )
            db.add(alert)
        else:
            logger.warning(f"?? Auto-heal requires approval for {device.name}")
    
    async def get_device_health(self, db: AsyncSession, device_id: int) -> Dict[str, Any]:
        """
        ?????? ??? ??? ??????
        Get device health
        """
        try:
            # ?????? ??? ??? ??????
            result = await db.execute(
                select(DeviceMetric)
                .where(DeviceMetric.device_id == device_id)
                .order_by(DeviceMetric.collected_at.desc())
                .limit(1)
            )
            latest_metric = result.scalar_one_or_none()
            
            if not latest_metric:
                return {"status": "unknown", "health_score": 0}
            
            # ???? ???? ?????
            health_score = 100
            
            # ??? ???? ????? ??? ????????
            cpu_load = latest_metric.cpu_load or 0
            memory_used = latest_metric.memory_used or 0
            latency = latest_metric.latency or 0
            packet_loss = latest_metric.packet_loss or 0
            
            if cpu_load > 80:
                health_score -= (cpu_load - 80) * 2
            if memory_used > 80:
                health_score -= (memory_used - 80) * 2
            if latency > 100:
                health_score -= min((latency - 100) / 10, 20)
            if packet_loss > 0:
                health_score -= packet_loss * 5
            
            health_score = max(0, min(100, health_score))
            
            # ????? ??????
            if health_score >= 80:
                status = "excellent"
            elif health_score >= 60:
                status = "good"
            elif health_score >= 40:
                status = "fair"
            else:
                status = "poor"
            
            return {
                "status": status,
                "health_score": round(health_score, 2),
                "metrics": {
                    "cpu_load": cpu_load,
                    "memory_used": memory_used,
                    "latency": latency,
                    "packet_loss": packet_loss,
                    "active_users": latest_metric.active_users
                },
                "last_check": latest_metric.collected_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting device health: {e}")
            return {"status": "error", "health_score": 0}

# ???? ??? ?? ???? ????????
monitoring_engine = MonitoringEngine()
