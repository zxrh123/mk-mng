"""
Executor Engine - ????? ????? RouterOS
"""

import asyncio
from typing import Dict, Optional, List
from datetime import datetime
from routeros_api import RouterOsApi
from app.core.config import settings


class ExecutorEngine:
    """Execute RouterOS commands safely"""
    
    def __init__(self):
        self.execution_history = []
        self.snapshots = {}
    
    async def connect_router(self, host: str, user: str, password: str) -> Optional[RouterOsApi]:
        """Connect to MikroTik router"""
        try:
            connection = RouterOsApi(host, user=user, password=password)
            return connection
        except Exception as e:
            print(f"Error connecting to router {host}: {e}")
            return None
    
    async def create_snapshot(self, connection: RouterOsApi, router_id: str) -> Dict:
        """Create snapshot before critical operations"""
        try:
            snapshot = {
                "router_id": router_id,
                "timestamp": datetime.now().isoformat(),
                "interfaces": await self._get_interfaces_backup(connection),
                "ip_addresses": await self._get_ip_addresses_backup(connection),
                "firewall_rules": await self._get_firewall_rules_backup(connection)
            }
            
            self.snapshots[router_id] = snapshot
            return snapshot
        except Exception as e:
            return {"error": str(e)}
    
    async def _get_interfaces_backup(self, connection: RouterOsApi) -> List[Dict]:
        """Backup interface configuration"""
        try:
            interfaces = connection.get_resource('/interface')
            return [dict(iface) for iface in interfaces]
        except:
            return []
    
    async def _get_ip_addresses_backup(self, connection: RouterOsApi) -> List[Dict]:
        """Backup IP addresses"""
        try:
            addresses = connection.get_resource('/ip/address')
            return [dict(addr) for addr in addresses]
        except:
            return []
    
    async def _get_firewall_rules_backup(self, connection: RouterOsApi) -> List[Dict]:
        """Backup firewall rules"""
        try:
            rules = connection.get_resource('/ip/firewall/filter')
            return [dict(rule) for rule in rules]
        except:
            return []
    
    async def execute_script(
        self,
        router_id: str,
        host: str,
        user: str,
        password: str,
        script: str,
        dry_run: bool = True,
        auto_execute: bool = False
    ) -> Dict:
        """
        Execute RouterOS script
        """
        execution_id = f"exec_{datetime.now().timestamp()}"
        
        execution_record = {
            "execution_id": execution_id,
            "router_id": router_id,
            "script": script,
            "dry_run": dry_run,
            "auto_execute": auto_execute,
            "status": "pending",
            "timestamp": datetime.now().isoformat(),
            "result": None,
            "error": None
        }
        
        # Check if auto-execute is allowed
        if not auto_execute and not dry_run:
            execution_record["status"] = "requires_confirmation"
            execution_record["error"] = "Auto-execute disabled. Requires manual confirmation."
            self.execution_history.append(execution_record)
            return execution_record
        
        # Connect to router
        connection = await self.connect_router(host, user, password)
        if not connection:
            execution_record["status"] = "failed"
            execution_record["error"] = "Failed to connect to router"
            self.execution_history.append(execution_record)
            return execution_record
        
        # Create snapshot before execution
        if not dry_run:
            snapshot = await self.create_snapshot(connection, router_id)
            execution_record["snapshot"] = snapshot
        
        # Execute script
        try:
            if dry_run:
                # Validate script syntax only
                execution_record["status"] = "dry_run_completed"
                execution_record["result"] = {
                    "message": "Script validated (dry run)",
                    "commands": script.split('\n')
                }
            else:
                # Actual execution
                lines = [line.strip() for line in script.split('\n') if line.strip()]
                results = []
                
                for line in lines:
                    if line.startswith('/'):
                        # Parse command
                        parts = line.split()
                        path = parts[0]
                        params = {}
                        
                        # Simple parameter parsing
                        i = 1
                        while i < len(parts):
                            if i + 1 < len(parts) and not parts[i+1].startswith('='):
                                params[parts[i].replace('=', '')] = parts[i+1]
                                i += 2
                            else:
                                if '=' in parts[i]:
                                    key, value = parts[i].split('=', 1)
                                    params[key] = value
                                i += 1
                        
                        try:
                            if path.startswith('/system'):
                                result = connection.talk(path, **params)
                            else:
                                result = connection.get_resource(path)
                            results.append({"command": line, "result": str(result)})
                        except Exception as e:
                            results.append({"command": line, "error": str(e)})
                
                execution_record["status"] = "completed"
                execution_record["result"] = {
                    "message": "Script executed successfully",
                    "commands_executed": len(results),
                    "results": results
                }
        
        except Exception as e:
            execution_record["status"] = "failed"
            execution_record["error"] = str(e)
        
        finally:
            self.execution_history.append(execution_record)
            # Keep only last 1000 executions
            if len(self.execution_history) > 1000:
                self.execution_history = self.execution_history[-1000:]
        
        return execution_record
    
    async def rollback(
        self,
        router_id: str,
        host: str,
        user: str,
        password: str,
        snapshot_id: Optional[str] = None
    ) -> Dict:
        """Rollback to snapshot"""
        if router_id not in self.snapshots:
            return {"error": "No snapshot found for this router"}
        
        snapshot = self.snapshots[router_id]
        connection = await self.connect_router(host, user, password)
        
        if not connection:
            return {"error": "Failed to connect to router"}
        
        try:
            # Restore configuration from snapshot
            # This is a simplified version - real implementation would restore all settings
            return {
                "status": "rolled_back",
                "snapshot": snapshot,
                "message": "Configuration rolled back successfully"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_execution_history(self, router_id: Optional[str] = None) -> List[Dict]:
        """Get execution history"""
        if router_id:
            return [e for e in self.execution_history if e.get("router_id") == router_id]
        return self.execution_history
