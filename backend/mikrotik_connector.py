"""
?? MikroTik Connector - ???? MikroTik
????? ?? ??????? ???????? ?? ????? MikroTik RouterOS
"""

import paramiko
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import json
import socket

logger = logging.getLogger(__name__)

class MikroTikConnector:
    """
    ???? MikroTik ??????? ?????? ???????
    MikroTik Connector for connection and command execution
    """
    
    def __init__(self, host: str, username: str, password: str, port: int = 22):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.ssh_client: Optional[paramiko.SSHClient] = None
        self.connected = False
        
    async def connect(self) -> bool:
        """
        ??????? ????? MikroTik
        Connect to MikroTik device
        
        Returns:
            bool: ??? ??????? ?? ??
        """
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            await asyncio.to_thread(
                self.ssh_client.connect,
                hostname=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                timeout=10,
                allow_agent=False,
                look_for_keys=False
            )
            
            self.connected = True
            logger.info(f"? Connected to MikroTik device: {self.host}")
            return True
            
        except Exception as e:
            logger.error(f"? Failed to connect to {self.host}: {e}")
            self.connected = False
            return False
    
    async def disconnect(self) -> None:
        """
        ??? ???????
        Disconnect
        """
        if self.ssh_client:
            self.ssh_client.close()
            self.connected = False
            logger.info(f"Disconnected from {self.host}")
    
    async def execute_command(self, command: str, timeout: int = 30) -> Dict[str, Any]:
        """
        ????? ??? RouterOS
        Execute RouterOS command
        
        Args:
            command: ????? ??????? ??????
            timeout: ?????? ??????? ????????
            
        Returns:
            Dict ????? ???: success, output, error, execution_time
        """
        if not self.connected:
            await self.connect()
        
        if not self.connected:
            return {
                "success": False,
                "output": "",
                "error": "Not connected to device",
                "execution_time": 0
            }
        
        start_time = datetime.now()
        
        try:
            stdin, stdout, stderr = await asyncio.to_thread(
                self.ssh_client.exec_command,
                command,
                timeout=timeout
            )
            
            output = await asyncio.to_thread(stdout.read)
            error = await asyncio.to_thread(stderr.read)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                "success": stdout.channel.recv_exit_status() == 0,
                "output": output.decode('utf-8', errors='ignore').strip(),
                "error": error.decode('utf-8', errors='ignore').strip(),
                "execution_time": execution_time
            }
            
            logger.info(f"Command executed on {self.host}: {command[:50]}... ({execution_time:.2f}s)")
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Error executing command on {self.host}: {e}")
            return {
                "success": False,
                "output": "",
                "error": str(e),
                "execution_time": execution_time
            }
    
    async def execute_script(self, script: str) -> Dict[str, Any]:
        """
        ????? ????? RouterOS ????? ??????
        Execute multi-line RouterOS script
        
        Args:
            script: ??????? ??????? ??????
            
        Returns:
            Dict ????? ??? ???????
        """
        # ????? ??????? ??? ?????
        commands = [cmd.strip() for cmd in script.split('\n') if cmd.strip() and not cmd.strip().startswith('#')]
        
        results = []
        overall_success = True
        
        for i, command in enumerate(commands):
            logger.info(f"Executing command {i+1}/{len(commands)}: {command[:50]}...")
            
            result = await self.execute_command(command)
            results.append({
                "command": command,
                "result": result
            })
            
            if not result['success']:
                overall_success = False
                logger.warning(f"Command failed: {command}")
                # ??? ??? ???? ???? ???????
                break
        
        return {
            "success": overall_success,
            "commands_executed": len(results),
            "total_commands": len(commands),
            "results": results
        }
    
    async def get_system_resources(self) -> Dict[str, Any]:
        """
        ?????? ??? ????? ??????
        Get system resources
        
        Returns:
            Dict ????? ???: cpu, memory, uptime, etc.
        """
        command = '/system resource print'
        result = await self.execute_command(command)
        
        if result['success']:
            return self._parse_system_resources(result['output'])
        
        return {}
    
    async def get_interfaces(self) -> List[Dict[str, Any]]:
        """
        ?????? ??? ????? ????????
        Get interfaces list
        
        Returns:
            List ?? Dict ????? ??? ??????? ????????
        """
        command = '/interface print stats'
        result = await self.execute_command(command)
        
        if result['success']:
            return self._parse_interfaces(result['output'])
        
        return []
    
    async def get_active_connections(self) -> int:
        """
        ?????? ??? ??? ????????? ??????
        Get active connections count
        
        Returns:
            int: ??? ????????? ??????
        """
        command = '/ip firewall connection print count-only'
        result = await self.execute_command(command)
        
        if result['success']:
            try:
                return int(result['output'].strip())
            except:
                pass
        
        return 0
    
    async def get_hotspot_users(self) -> List[Dict[str, Any]]:
        """
        ?????? ??? ??????? ????? ???? ???????
        Get active hotspot users
        
        Returns:
            List ?? Dict ????? ??? ??????? ??????????
        """
        command = '/ip hotspot active print'
        result = await self.execute_command(command)
        
        if result['success']:
            return self._parse_hotspot_users(result['output'])
        
        return []
    
    async def create_backup(self) -> Dict[str, Any]:
        """
        ????? ???? ????????
        Create backup
        
        Returns:
            Dict ????? ??? ??????? ?????? ??????????
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"backup_{timestamp}"
        
        command = f'/system backup save name={backup_name}'
        result = await self.execute_command(command)
        
        return {
            "success": result['success'],
            "backup_name": backup_name,
            "timestamp": timestamp,
            "error": result.get('error', '')
        }
    
    async def restore_backup(self, backup_name: str) -> Dict[str, Any]:
        """
        ??????? ???? ????????
        Restore backup
        
        Args:
            backup_name: ??? ?????? ??????????
            
        Returns:
            Dict ????? ??? ???????
        """
        command = f'/system backup load name={backup_name}'
        result = await self.execute_command(command)
        
        return {
            "success": result['success'],
            "backup_name": backup_name,
            "error": result.get('error', '')
        }
    
    async def get_logs(self, count: int = 50) -> List[Dict[str, Any]]:
        """
        ?????? ??? ????? ??????
        Get system logs
        
        Args:
            count: ??? ???????
            
        Returns:
            List ?? Dict ????? ??? ???????
        """
        command = f'/log print without-paging'
        result = await self.execute_command(command)
        
        if result['success']:
            return self._parse_logs(result['output'], count)
        
        return []
    
    async def ping_test(self, target: str, count: int = 4) -> Dict[str, Any]:
        """
        ?????? ???????
        Ping test
        
        Args:
            target: ????? (IP ?? ?????)
            count: ??? ?????
            
        Returns:
            Dict ????? ??? ???????
        """
        command = f'/ping {target} count={count}'
        result = await self.execute_command(command)
        
        if result['success']:
            return self._parse_ping_result(result['output'])
        
        return {
            "success": False,
            "target": target,
            "packet_loss": 100,
            "avg_latency": 0
        }
    
    def _parse_system_resources(self, output: str) -> Dict[str, Any]:
        """
        ????? ?????? ????? ??????
        Parse system resources output
        """
        resources = {}
        
        for line in output.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().replace(' ', '_').replace('-', '_').lower()
                value = value.strip()
                resources[key] = value
        
        # ????? ????? ?????? ??? ?????
        try:
            if 'cpu_load' in resources:
                resources['cpu_load'] = float(resources['cpu_load'].replace('%', ''))
            
            if 'total_memory' in resources and 'free_memory' in resources:
                total = self._parse_size(resources['total_memory'])
                free = self._parse_size(resources['free_memory'])
                resources['memory_used_percent'] = ((total - free) / total * 100) if total > 0 else 0
        except:
            pass
        
        return resources
    
    def _parse_interfaces(self, output: str) -> List[Dict[str, Any]]:
        """
        ????? ?????? ????????
        Parse interfaces output
        """
        interfaces = []
        
        # ??? ??? ????? ???????? ???????? ??? ????? ?? ????????
        # ??????? ????? ??? ????? ?????? MikroTik
        
        return interfaces
    
    def _parse_hotspot_users(self, output: str) -> List[Dict[str, Any]]:
        """
        ????? ?????? ??????? ????? ????
        Parse hotspot users output
        """
        users = []
        
        # ????? ????????
        
        return users
    
    def _parse_logs(self, output: str, count: int) -> List[Dict[str, Any]]:
        """
        ????? ???????
        Parse logs
        """
        logs = []
        
        lines = output.split('\n')[:count]
        
        for line in lines:
            if line.strip():
                logs.append({
                    "timestamp": datetime.now().isoformat(),
                    "message": line.strip()
                })
        
        return logs
    
    def _parse_ping_result(self, output: str) -> Dict[str, Any]:
        """
        ????? ????? ??? ping
        Parse ping results
        """
        result = {
            "success": True,
            "packet_loss": 0,
            "avg_latency": 0,
            "min_latency": 0,
            "max_latency": 0
        }
        
        # ????? ????????
        
        return result
    
    def _parse_size(self, size_str: str) -> float:
        """
        ????? ??? ??????? ??? ??????
        Convert memory size to bytes
        """
        units = {'KiB': 1024, 'MiB': 1024**2, 'GiB': 1024**3}
        
        for unit, multiplier in units.items():
            if unit in size_str:
                try:
                    return float(size_str.replace(unit, '').strip()) * multiplier
                except:
                    pass
        
        return 0.0

class MikroTikConnectionPool:
    """
    ???? ??????? MikroTik
    MikroTik Connection Pool
    """
    
    def __init__(self):
        self.connections: Dict[int, MikroTikConnector] = {}
        self.locks: Dict[int, asyncio.Lock] = {}
    
    async def get_connector(
        self, 
        device_id: int, 
        host: str, 
        username: str, 
        password: str, 
        port: int = 22
    ) -> MikroTikConnector:
        """
        ?????? ??? ???? ?? ?????? ?? ????? ????
        Get connector from pool or create new
        """
        if device_id not in self.connections:
            self.connections[device_id] = MikroTikConnector(host, username, password, port)
            self.locks[device_id] = asyncio.Lock()
        
        return self.connections[device_id]
    
    async def remove_connector(self, device_id: int) -> None:
        """
        ????? ???? ?? ??????
        Remove connector from pool
        """
        if device_id in self.connections:
            await self.connections[device_id].disconnect()
            del self.connections[device_id]
            del self.locks[device_id]
    
    async def close_all(self) -> None:
        """
        ????? ???? ?????????
        Close all connections
        """
        for connector in self.connections.values():
            await connector.disconnect()
        
        self.connections.clear()
        self.locks.clear()

# ???? ??? ?? ???? ?????????
connection_pool = MikroTikConnectionPool()
