"""
Auto-Healing Engine - ???? ??????? ????????
"""

import asyncio
from typing import Dict, List, Optional
from datetime import datetime
from app.core.monitoring_engine import MonitoringEngine
from app.core.executor_engine import ExecutorEngine
from app.core.ai_brain import AIBrain
from app.core.config import settings


class AutoHealEngine:
    """Automatic healing and recovery system"""
    
    def __init__(self):
        self.monitoring_engine = MonitoringEngine()
        self.executor_engine = ExecutorEngine()
        self.ai_brain = AIBrain()
        self.healing_history = []
        self.active_heals = {}
    
    async def initialize(self):
        """Initialize auto-heal engine"""
        # Register alert callback
        self.monitoring_engine.register_alert_callback(self.handle_alert)
    
    async def handle_alert(self, alert: Dict):
        """Handle alerts and trigger auto-healing if needed"""
        alert_type = alert.get("type")
        severity = alert.get("severity")
        
        # Only auto-heal for certain alert types
        auto_heal_types = [
            "interface_down",
            "high_cpu",
            "high_latency"
        ]
        
        if alert_type in auto_heal_types and severity in ["warning", "error"]:
            await self.attempt_heal(alert)
    
    async def attempt_heal(self, alert: Dict):
        """Attempt to heal an issue"""
        alert_type = alert.get("type")
        router_id = alert.get("router_id")
        
        if not router_id:
            return
        
        healing_id = f"heal_{router_id}_{datetime.now().timestamp()}"
        
        healing_record = {
            "healing_id": healing_id,
            "router_id": router_id,
            "alert": alert,
            "status": "attempting",
            "timestamp": datetime.now().isoformat(),
            "actions_taken": [],
            "result": None
        }
        
        try:
            if alert_type == "interface_down":
                result = await self.heal_interface_down(router_id, alert)
            elif alert_type == "high_cpu":
                result = await self.heal_high_cpu(router_id, alert)
            elif alert_type == "high_latency":
                result = await self.heal_high_latency(router_id, alert)
            else:
                result = {"status": "unknown_alert_type"}
            
            healing_record["status"] = "completed"
            healing_record["result"] = result
            
        except Exception as e:
            healing_record["status"] = "failed"
            healing_record["result"] = {"error": str(e)}
        
        finally:
            self.healing_history.append(healing_record)
            # Keep only last 500 entries
            if len(self.healing_history) > 500:
                self.healing_history = self.healing_history[-500:]
    
    async def heal_interface_down(self, router_id: str, alert: Dict) -> Dict:
        """Heal interface down issue"""
        interface_name = alert.get("interface")
        
        # Use AI to generate healing script
        intent = {
            "intent": "troubleshoot",
            "target": "interface",
            "action": "restart",
            "parameters": {"interface": interface_name}
        }
        
        script_result = await self.ai_brain.generate_routeros_script(intent)
        
        if "error" in script_result:
            return {"error": script_result["error"]}
        
        # Execute healing script
        # Note: In production, this would require router connection details
        healing_script = f"""/interface disable {interface_name}
        :delay 2s
        /interface enable {interface_name}
        """
        
        execution_result = await self.executor_engine.execute_script(
            router_id,
            "",  # host
            "",  # user
            "",  # password
            healing_script,
            dry_run=False,
            auto_execute=True
        )
        
        return {
            "action": "interface_restart",
            "interface": interface_name,
            "execution": execution_result
        }
    
    async def heal_high_cpu(self, router_id: str, alert: Dict) -> Dict:
        """Heal high CPU usage"""
        # Analyze with AI
        analysis = await self.ai_brain.quick_analysis(
            {"alert": alert, "router_id": router_id},
            "??? ???? ????? ??????? ??????? ?? MikroTik?"
        )
        
        # Generate optimization script
        intent = {
            "intent": "optimize",
            "target": "system",
            "action": "modify",
            "parameters": {"optimization": "cpu"}
        }
        
        script_result = await self.ai_brain.generate_routeros_script(intent)
        
        return {
            "action": "cpu_optimization",
            "analysis": analysis,
            "script": script_result
        }
    
    async def heal_high_latency(self, router_id: str, alert: Dict) -> Dict:
        """Heal high latency issue"""
        # Check routing and optimize
        intent = {
            "intent": "troubleshoot",
            "target": "routing",
            "action": "optimize",
            "parameters": {"issue": "latency"}
        }
        
        script_result = await self.ai_brain.generate_routeros_script(intent)
        
        return {
            "action": "latency_optimization",
            "script": script_result
        }
    
    def get_healing_history(self, router_id: Optional[str] = None) -> List[Dict]:
        """Get healing history"""
        if router_id:
            return [h for h in self.healing_history if h.get("router_id") == router_id]
        return self.healing_history
