"""
?? Executor Engine - ???? ???????
????? ?? ????? ??????? ?????????? ??? ????? MikroTik ?????
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models import Task, TaskStatus, Device, SystemLog
from mikrotik_connector import connection_pool
from core_ai_brain import ai_brain
from config import settings

logger = logging.getLogger(__name__)

class ExecutorEngine:
    """
    ???? ????? ??????? ??????????
    Command and Script Execution Engine
    """
    
    def __init__(self):
        self.running_tasks = {}
        self.task_queue = asyncio.Queue()
        self.is_running = False
        
    async def start(self) -> None:
        """
        ??? ???? ???????
        Start executor engine
        """
        self.is_running = True
        logger.info("?? Executor Engine started")
        
        # ??? ????? ????? ??????
        asyncio.create_task(self._task_processor())
    
    async def stop(self) -> None:
        """
        ????? ???? ???????
        Stop executor engine
        """
        self.is_running = False
        logger.info("? Executor Engine stopped")
    
    async def execute_task(
        self,
        db: AsyncSession,
        task_id: int,
        force: bool = False
    ) -> Dict[str, Any]:
        """
        ????? ????
        Execute task
        
        Args:
            db: ???? ????? ????????
            task_id: ???? ??????
            force: ????? ?????? (????? ???????)
            
        Returns:
            Dict ????? ??? ????? ???????
        """
        try:
            # ?????? ??? ??????
            result = await db.execute(
                select(Task).where(Task.id == task_id)
            )
            task = result.scalar_one_or_none()
            
            if not task:
                return {"success": False, "error": "Task not found"}
            
            # ?????? ?? ???? ??????
            if task.status == TaskStatus.RUNNING:
                return {"success": False, "error": "Task already running"}
            
            if task.status == TaskStatus.COMPLETED:
                return {"success": False, "error": "Task already completed"}
            
            # ?????? ?? ??????
            if not force and not task.auto_execute and not settings.AUTO_EXECUTE:
                if task.dry_run:
                    return await self._dry_run_task(db, task)
                else:
                    return {"success": False, "error": "Manual approval required"}
            
            # ????? ???? ??????
            task.status = TaskStatus.RUNNING
            task.executed_at = datetime.now()
            await db.commit()
            
            # ?????? ??? ??????
            device_result = await db.execute(
                select(Device).where(Device.id == task.device_id)
            )
            device = device_result.scalar_one()
            
            # ????? ???? ???????? ??? ???????
            backup_result = await self._create_backup(device)
            
            # ????? ??????
            execution_result = await self._execute_on_device(task, device)
            
            # ????? ?????? ????????
            if execution_result['success']:
                task.status = TaskStatus.COMPLETED
                task.result = execution_result
                task.completed_at = datetime.now()
                
                logger.info(f"? Task {task_id} completed successfully")
                
                # ?????? ?? ??????
                if settings.ENABLE_LEARNING:
                    await ai_brain.learn_from_execution(
                        task={
                            "task_type": task.task_type,
                            "description": task.description,
                            "script": task.script,
                            "device_info": {
                                "model": device.model,
                                "routeros_version": device.routeros_version
                            }
                        },
                        execution_result=execution_result,
                        success=True
                    )
            else:
                task.status = TaskStatus.FAILED
                task.error_message = execution_result.get('error', 'Unknown error')
                task.result = execution_result
                task.completed_at = datetime.now()
                
                logger.error(f"? Task {task_id} failed: {task.error_message}")
                
                # ??????? ?????? ?????????? ??? ??? ?????
                if backup_result.get('success'):
                    await self._restore_backup(device, backup_result['backup_name'])
                
                # ?????? ?? ?????
                if settings.ENABLE_LEARNING:
                    await ai_brain.learn_from_execution(
                        task={
                            "task_type": task.task_type,
                            "description": task.description,
                            "script": task.script,
                            "device_info": {
                                "model": device.model,
                                "routeros_version": device.routeros_version
                            }
                        },
                        execution_result=execution_result,
                        success=False
                    )
            
            await db.commit()
            
            # ????? ?? ????? ??????
            await self._log_execution(db, task, execution_result)
            
            return {
                "success": execution_result['success'],
                "task_id": task_id,
                "result": execution_result,
                "backup": backup_result
            }
            
        except Exception as e:
            logger.error(f"Error executing task {task_id}: {e}")
            
            # ????? ???? ??????
            if task:
                task.status = TaskStatus.FAILED
                task.error_message = str(e)
                task.completed_at = datetime.now()
                await db.commit()
            
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _dry_run_task(self, db: AsyncSession, task: Task) -> Dict[str, Any]:
        """
        ????? ?????? ?????? (???? ????? ?????????)
        Dry run task (without applying changes)
        
        Args:
            db: ???? ????? ????????
            task: ??????
            
        Returns:
            Dict ????? ??? ????? ??????? ????????
        """
        logger.info(f"?? Dry run for task {task.id}")
        
        # ????? ??????? ???????? ?????? ???????
        device_result = await db.execute(
            select(Device).where(Device.id == task.device_id)
        )
        device = device_result.scalar_one()
        
        analysis = await ai_brain.generate_routeros_script(
            task_description=task.description,
            device_info={
                "model": device.model,
                "routeros_version": device.routeros_version,
                "ip_address": device.ip_address
            }
        )
        
        return {
            "success": True,
            "dry_run": True,
            "analysis": analysis,
            "script": task.script,
            "warnings": analysis.get('warnings', []),
            "estimated_impact": analysis.get('estimated_impact', 'unknown'),
            "confidence": analysis.get('confidence', 0)
        }
    
    async def _execute_on_device(self, task: Task, device: Device) -> Dict[str, Any]:
        """
        ????? ?????? ??? ??????
        Execute task on device
        
        Args:
            task: ??????
            device: ??????
            
        Returns:
            Dict ????? ??? ????? ???????
        """
        try:
            # ?????? ??? ??????
            connector = await connection_pool.get_connector(
                device_id=device.id,
                host=device.ip_address,
                username=device.username,
                password=device.encrypted_password,
                port=device.ssh_port
            )
            
            # ??????? ???????
            connected = await connector.connect()
            if not connected:
                return {
                    "success": False,
                    "error": "Failed to connect to device"
                }
            
            # ????? ??? ??? ??????
            if task.task_type == "execute":
                # ????? ??? ????
                result = await connector.execute_command(task.command or task.script)
            elif task.task_type == "script":
                # ????? ????? ????? ??????
                result = await connector.execute_script(task.script)
            elif task.task_type == "config":
                # ????? ???????
                result = await connector.execute_script(task.script)
            else:
                result = {
                    "success": False,
                    "error": f"Unknown task type: {task.task_type}"
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing on device: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _create_backup(self, device: Device) -> Dict[str, Any]:
        """
        ????? ???? ???????? ??? ???????
        Create backup before execution
        """
        try:
            connector = await connection_pool.get_connector(
                device_id=device.id,
                host=device.ip_address,
                username=device.username,
                password=device.encrypted_password,
                port=device.ssh_port
            )
            
            backup_result = await connector.create_backup()
            
            if backup_result['success']:
                logger.info(f"?? Backup created: {backup_result['backup_name']}")
            
            return backup_result
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _restore_backup(self, device: Device, backup_name: str) -> Dict[str, Any]:
        """
        ??????? ???? ????????
        Restore backup
        """
        try:
            connector = await connection_pool.get_connector(
                device_id=device.id,
                host=device.ip_address,
                username=device.username,
                password=device.encrypted_password,
                port=device.ssh_port
            )
            
            restore_result = await connector.restore_backup(backup_name)
            
            if restore_result['success']:
                logger.info(f"?? Backup restored: {backup_name}")
            
            return restore_result
            
        except Exception as e:
            logger.error(f"Error restoring backup: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _log_execution(
        self,
        db: AsyncSession,
        task: Task,
        result: Dict[str, Any]
    ) -> None:
        """
        ????? ??????? ?? ????? ??????
        Log execution to system logs
        """
        try:
            log = SystemLog(
                level="INFO" if result['success'] else "ERROR",
                module="executor_engine",
                message=f"Task {task.id} ({task.task_type}): {task.description}",
                user_id=task.user_id,
                device_id=task.device_id,
                metadata={
                    "task_id": task.id,
                    "result": result,
                    "executed_at": task.executed_at.isoformat() if task.executed_at else None,
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None
                }
            )
            db.add(log)
            await db.commit()
            
        except Exception as e:
            logger.error(f"Error logging execution: {e}")
    
    async def _task_processor(self) -> None:
        """
        ????? ????? ??????
        Task queue processor
        """
        while self.is_running:
            try:
                # ?????? ??? ???? ?? ???????
                task_data = await asyncio.wait_for(
                    self.task_queue.get(),
                    timeout=1.0
                )
                
                # ????? ??????
                # await self.execute_task(**task_data)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error in task processor: {e}")
                await asyncio.sleep(1)
    
    async def add_to_queue(self, db: AsyncSession, task_id: int) -> None:
        """
        ????? ???? ??? ???????
        Add task to queue
        """
        await self.task_queue.put({
            "db": db,
            "task_id": task_id
        })
        logger.info(f"Task {task_id} added to queue")
    
    async def batch_execute(
        self,
        db: AsyncSession,
        task_ids: List[int],
        force: bool = False
    ) -> List[Dict[str, Any]]:
        """
        ????? ?????? ?? ??????
        Batch execute tasks
        
        Args:
            db: ???? ????? ????????
            task_ids: ????? ?????? ??????
            force: ????? ??????
            
        Returns:
            List ?? Dict ????? ??? ????? ???????
        """
        tasks = [
            self.execute_task(db, task_id, force)
            for task_id in task_ids
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return [
            result if not isinstance(result, Exception) else {"success": False, "error": str(result)}
            for result in results
        ]

# ???? ??? ?? ???? ???????
executor_engine = ExecutorEngine()
