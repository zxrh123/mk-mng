"""
Core AI Brain - ????? ??????? ???????
Integrates GPT-5 and Gemini for intelligent decision-making
"""

import os
import json
import asyncio
from typing import Dict, List, Optional, Any
from openai import AsyncOpenAI
import google.generativeai as genai
from app.core.config import settings


class AIBrain:
    """
    Core AI Brain that orchestrates GPT-5 and Gemini
    for intelligent network management decisions
    """
    
    def __init__(self):
        self.openai_client = None
        self.gemini_model = None
        self.is_initialized = False
        self.knowledge_base = []
        self.learning_history = []
        
    async def initialize(self):
        """Initialize AI models"""
        try:
            # Initialize OpenAI
            if settings.OPENAI_API_KEY:
                self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
                print("? OpenAI client initialized")
            
            # Initialize Gemini
            if settings.GEMINI_API_KEY:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.gemini_model = genai.GenerativeModel('gemini-pro')
                print("? Gemini model initialized")
            
            self.is_initialized = True
            await self.load_knowledge_base()
            
        except Exception as e:
            print(f"? Error initializing AI Brain: {e}")
            self.is_initialized = False
    
    def is_ready(self) -> bool:
        """Check if AI Brain is ready"""
        return self.is_initialized
    
    async def load_knowledge_base(self):
        """Load MikroTik knowledge base"""
        # This would load from database or file
        self.knowledge_base = [
            {
                "topic": "interface_monitoring",
                "patterns": ["interface down", "link down", "no carrier"],
                "solutions": ["check cable", "restart interface", "check physical connection"]
            },
            {
                "topic": "high_cpu",
                "patterns": ["cpu high", "cpu overload", "slow performance"],
                "solutions": ["check firewall rules", "optimize queues", "reduce logging"]
            }
        ]
    
    async def analyze_intent(self, user_message: str, context: Optional[Dict] = None) -> Dict:
        """
        Analyze user intent using GPT-5
        """
        if not self.openai_client:
            return {"error": "OpenAI client not initialized"}
        
        system_prompt = """??? ????? ??? ????? ?? ????? ????? MikroTik RouterOS.
        ????? ?? ??? ????? ???????? ???????? ??? ????? RouterOS ??????.
        
        ??? ?? ???? ????? (Intent) ?? ??????? ?????:
        1. ??? ??????? ???????? (monitoring, configuration, troubleshooting)
        2. ????? (interface, firewall, queue, hotspot, etc.)
        3. ??????? ??????? (check, modify, create, delete)
        4. ????????? ????????
        
        ??? ????? JSON:
        {
            "intent": "monitor|configure|troubleshoot|query",
            "target": "interface|firewall|queue|hotspot|system",
            "action": "check|modify|create|delete|restart",
            "parameters": {},
            "confidence": 0.0-1.0,
            "requires_confirmation": true|false
        }
        """
        
        try:
            response = await self.openai_client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            return {"error": str(e), "intent": "unknown"}
    
    async def generate_routeros_script(
        self, 
        intent: Dict, 
        router_info: Optional[Dict] = None
    ) -> Dict:
        """
        Generate RouterOS script based on intent
        Uses GPT-5 for script generation
        """
        if not self.openai_client:
            return {"error": "OpenAI client not initialized"}
        
        script_prompt = f"""??? ???? ?? ????? ??????? MikroTik RouterOS.
        
        ????? ???????:
        {json.dumps(intent, ensure_ascii=False, indent=2)}
        
        ??????? ???????:
        {json.dumps(router_info or {}, ensure_ascii=False, indent=2)}
        
        ???? ????? RouterOS ???? ???? ???? ???????.
        ??? ?? ???? ???????:
        1. ?????? ??????
        2. ????? (????? ?? ?????? ??? ???????)
        3. ????? ??? ?????? ???????
        4. ???? ????? ?????
        
        ??? ????? JSON:
        {{
            "script": "/interface enable ether1\\n/ip address print",
            "description": "??? ?? ????? ???????",
            "risk_level": "low|medium|high",
            "estimated_time": "seconds",
            "rollback_script": "????? ??????? ?? ???"
        }}
        """
        
        try:
            response = await self.openai_client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": script_prompt},
                    {"role": "user", "content": "???? ???????"}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            return {"error": str(e)}
    
    async def quick_analysis(self, data: Dict, query: str) -> Dict:
        """
        Quick analysis using Gemini for fast responses
        """
        if not self.gemini_model:
            return {"error": "Gemini model not initialized"}
        
        try:
            prompt = f"""????? ???? ???????? ???????:
            
            ?????????: {query}
            
            ????????:
            {json.dumps(data, ensure_ascii=False, indent=2)}
            
            ??? ??????? ?????? ????????? ?????.
            """
            
            response = await self.gemini_model.generate_content_async(prompt)
            return {
                "analysis": response.text,
                "source": "gemini"
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def make_decision(
        self, 
        user_message: str, 
        context: Dict,
        router_state: Optional[Dict] = None
    ) -> Dict:
        """
        Main decision-making function
        Combines GPT-5 and Gemini for optimal decisions
        """
        # Step 1: Analyze intent with GPT-5
        intent = await self.analyze_intent(user_message, context)
        
        if "error" in intent:
            return {"error": intent["error"]}
        
        # Step 2: Quick context analysis with Gemini
        quick_analysis_result = await self.quick_analysis(
            {"intent": intent, "router_state": router_state or {}},
            user_message
        )
        
        # Step 3: Generate RouterOS script if needed
        script_result = {}
        if intent.get("action") in ["modify", "create", "delete"]:
            script_result = await self.generate_routeros_script(intent, router_state)
        
        # Step 4: Create execution plan
        execution_plan = {
            "intent": intent,
            "quick_analysis": quick_analysis_result,
            "script": script_result,
            "requires_confirmation": intent.get("requires_confirmation", True),
            "risk_level": script_result.get("risk_level", "medium"),
            "dry_run": settings.AI_DRY_RUN,
            "auto_execute": settings.AI_AUTO_EXECUTE and intent.get("confidence", 0) > 0.9
        }
        
        return execution_plan
    
    async def learn_from_execution(
        self, 
        execution_result: Dict,
        original_intent: Dict
    ):
        """Learn from execution results"""
        if not settings.AI_ENABLE_LEARNING:
            return
        
        learning_entry = {
            "timestamp": asyncio.get_event_loop().time(),
            "intent": original_intent,
            "result": execution_result,
            "success": execution_result.get("success", False)
        }
        
        self.learning_history.append(learning_entry)
        
        # Keep only last 1000 entries
        if len(self.learning_history) > 1000:
            self.learning_history = self.learning_history[-1000:]
    
    async def chat_response(self, user_message: str, context: Dict) -> str:
        """
        Generate human-like chat response
        """
        if not self.openai_client:
            return "?????? ???? ?????? ??????? ??? ???? ??????."
        
        chat_prompt = """??? ????? ??? ????? ????? ?? ????? ????? MikroTik.
        ???? ?????? ????? ?????? ??? ?????.
        ?????? ????? ??????? ?????? ?? ???? ?????.
        ???? ??????? ?????? ?????.
        """
        
        try:
            response = await self.openai_client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": chat_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"??? ??? ????? ?????? ????: {str(e)}"
