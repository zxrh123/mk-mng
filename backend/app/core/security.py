"""
Security & Policy Layer - ???? ?????? ??????????
"""

from typing import Dict, Optional, List
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SecurityManager:
    """Security and authentication manager"""
    
    def __init__(self):
        self.pwd_context = pwd_context
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash password"""
        return self.pwd_context.hash(password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Create JWT token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            return None


class PolicyManager:
    """Policy and permission manager"""
    
    def __init__(self):
        self.policies = {
            "auto_execute": settings.AI_AUTO_EXECUTE,
            "dry_run_default": settings.AI_DRY_RUN,
            "require_confirmation": True,
            "max_script_length": 10000,
            "allowed_commands": [
                "/interface",
                "/ip",
                "/system",
                "/queue",
                "/ip/hotspot"
            ],
            "blocked_commands": [
                "/system/reset-configuration",
                "/system/reset-data",
                "/user/remove"
            ]
        }
    
    def check_policy(self, action: str, context: Dict) -> Dict:
        """Check if action is allowed by policy"""
        result = {
            "allowed": True,
            "reason": None,
            "requires_confirmation": self.policies.get("require_confirmation", True)
        }
        
        # Check command restrictions
        if "script" in context:
            script = context["script"]
            
            # Check blocked commands
            for blocked in self.policies["blocked_commands"]:
                if blocked in script:
                    result["allowed"] = False
                    result["reason"] = f"Command {blocked} is blocked by policy"
                    return result
            
            # Check script length
            if len(script) > self.policies["max_script_length"]:
                result["allowed"] = False
                result["reason"] = "Script exceeds maximum length"
                return result
        
        # Check auto-execute policy
        if action == "execute" and not self.policies["auto_execute"]:
            result["requires_confirmation"] = True
        
        return result
    
    def update_policy(self, policy_name: str, value):
        """Update policy"""
        if policy_name in self.policies:
            self.policies[policy_name] = value
            return True
        return False
