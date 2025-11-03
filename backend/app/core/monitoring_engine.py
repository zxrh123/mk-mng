"""
Monitoring Engine - ?????? ?????? ???????
"""

import asyncio
from typing import Dict, List, Optional
from datetime import datetime
from routeros_api import RouterOsApi
from app.core.config import settings


class MonitoringEngine:
    """Real-time monitoring of MikroTik routers"""
    
    def __init__(self):
        self.monitoring_tasks = {}
        self.alert_callbacks = []
        self.is_running = False
    
    async def connect_router(self, host: str, user: str, password: str) -> Optional[RouterOsApi]:
        """Connect to MikroTik router"""
        try:
            connection = RouterOsApi(host, user=user, password=password)
            return connection
        except Exception as e:
            print(f"Error connecting to router {host}: {e}")
            return None
    
    async def get_system_resources(self, connection: RouterOsApi) -> Dict:
        """Get CPU, RAM, and disk usage"""
        try:
            resources = connection.get_resource('/system/resource')
            return {
                "cpu_load": float(resources.get('cpu-load', 0)),
                "free_memory": int(resources.get('free-memory', 0)),
                "total_memory": int(resources.get('total-memory', 0)),
                "used_memory": int(resources.get('total-memory', 0)) - int(resources.get('free-memory', 0)),
                "uptime": resources.get('uptime', '0s'),
                "version": resources.get('version', 'unknown'),
                "board_name": resources.get('board-name', 'unknown'),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def get_interfaces_status(self, connection: RouterOsApi) -> List[Dict]:
        """Get status of all interfaces"""
        try:
            interfaces = connection.get_resource('/interface')
            result = []
            
            for iface in interfaces:
                result.append({
                    "name": iface.get('name', 'unknown'),
                    "type": iface.get('type', 'unknown'),
                    "mtu": iface.get('mtu', 0),
                    "mac_address": iface.get('mac-address', ''),
                    "running": iface.get('running', False),
                    "disabled": iface.get('disabled', False),
                    "link_downs": int(iface.get('link-downs', 0)),
                    "rx_byte": int(iface.get('rx-byte', 0)),
                    "tx_byte": int(iface.get('tx-byte', 0)),
                    "rx_packet": int(iface.get('rx-packet', 0)),
                    "tx_packet": int(iface.get('tx-packet', 0)),
                    "rx_drop": int(iface.get('rx-drop', 0)),
                    "tx_drop": int(iface.get('tx-drop', 0)),
                    "rx_error": int(iface.get('rx-error', 0)),
                    "tx_error": int(iface.get('tx-error', 0))
                })
            
            return result
        except Exception as e:
            return [{"error": str(e)}]
    
    async def get_hotspot_users(self, connection: RouterOsApi) -> List[Dict]:
        """Get active hotspot users"""
        try:
            users = connection.get_resource('/ip/hotspot/active')
            result = []
            
            for user in users:
                result.append({
                    "user": user.get('user', 'unknown'),
                    "address": user.get('address', ''),
                    "uptime": user.get('uptime', '0s'),
                    "bytes": int(user.get('bytes', 0)),
                    "packets": int(user.get('packets', 0)),
                    "server": user.get('server', 'all')
                })
            
            return result
        except Exception as e:
            return [{"error": str(e)}]
    
    async def check_latency(self, connection: RouterOsApi, target: str = "8.8.8.8") -> Dict:
        """Check latency to target"""
        try:
            ping_result = connection.talk('/ping', target=target, count='3')
            # Parse ping result
            return {
                "target": target,
                "avg_time": 0,  # Would parse from ping_result
                "packet_loss": 0,
                "status": "ok"
            }
        except Exception as e:
            return {"error": str(e), "target": target}
    
    async def monitor_router(
        self, 
        router_id: str,
        host: str,
        user: str,
        password: str
    ):
        """Continuous monitoring of a router"""
        connection = await self.connect_router(host, user, password)
        if not connection:
            return
        
        while self.is_running:
            try:
                # Get all metrics
                resources = await self.get_system_resources(connection)
                interfaces = await self.get_interfaces_status(connection)
                hotspot_users = await self.get_hotspot_users(connection)
                latency = await self.check_latency(connection)
                
                # Check for alerts
                await self.check_alerts(resources, interfaces, latency)
                
                # Wait for next interval
                await asyncio.sleep(settings.MONITORING_INTERVAL)
                
            except Exception as e:
                print(f"Error monitoring router {router_id}: {e}")
                await asyncio.sleep(settings.MONITORING_INTERVAL)
    
    async def check_alerts(
        self,
        resources: Dict,
        interfaces: List[Dict],
        latency: Dict
    ):
        """Check for alert conditions"""
        alerts = []
        
        # CPU Alert
        if resources.get("cpu_load", 0) > settings.ALERT_THRESHOLD_CPU:
            alerts.append({
                "type": "high_cpu",
                "severity": "warning",
                "message": f"CPU usage is {resources.get('cpu_load')}%",
                "value": resources.get("cpu_load")
            })
        
        # RAM Alert
        ram_usage = (resources.get("used_memory", 0) / resources.get("total_memory", 1)) * 100
        if ram_usage > settings.ALERT_THRESHOLD_RAM:
            alerts.append({
                "type": "high_ram",
                "severity": "warning",
                "message": f"RAM usage is {ram_usage:.1f}%",
                "value": ram_usage
            })
        
        # Interface Down Alert
        for iface in interfaces:
            if not iface.get("running", False) and not iface.get("disabled", False):
                alerts.append({
                    "type": "interface_down",
                    "severity": "error",
                    "message": f"Interface {iface.get('name')} is down",
                    "interface": iface.get("name")
                })
        
        # Latency Alert
        if latency.get("avg_time", 0) > settings.ALERT_THRESHOLD_LATENCY:
            alerts.append({
                "type": "high_latency",
                "severity": "warning",
                "message": f"High latency: {latency.get('avg_time')}ms",
                "value": latency.get("avg_time")
            })
        
        # Trigger callbacks
        for callback in self.alert_callbacks:
            for alert in alerts:
                await callback(alert)
    
    def register_alert_callback(self, callback):
        """Register callback for alerts"""
        self.alert_callbacks.append(callback)
    
    async def start_monitoring(self, router_id: str, host: str, user: str, password: str):
        """Start monitoring a router"""
        self.is_running = True
        task = asyncio.create_task(
            self.monitor_router(router_id, host, user, password)
        )
        self.monitoring_tasks[router_id] = task
    
    async def stop_monitoring(self, router_id: str):
        """Stop monitoring a router"""
        if router_id in self.monitoring_tasks:
            self.monitoring_tasks[router_id].cancel()
            del self.monitoring_tasks[router_id]
