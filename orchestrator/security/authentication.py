"""Authentication System.

This module implements authentication functionality for the orchestrator,
including user management, session handling, and token-based authentication.
"""

from __future__ import annotations

import time
import uuid
import hashlib
import threading
from typing import Any, Dict, List, Optional
from enum import Enum
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


class AuthenticationMethod(str, Enum):
    """Authentication methods."""
    PASSWORD = "password"
    TOKEN = "token"
    OAUTH = "oauth"
    API_KEY = "api_key"
    CERTIFICATE = "certificate"


class UserStatus(str, Enum):
    """User status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    LOCKED = "locked"
    PENDING = "pending"


@dataclass
class User:
    """Represents a user in the system."""
    user_id: str
    username: str
    email: str
    status: UserStatus
    roles: List[str]
    created_at: float
    last_login: Optional[float]
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary."""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "status": self.status,
            "roles": self.roles,
            "created_at": self.created_at,
            "last_login": self.last_login,
            "metadata": self.metadata
        }

    def add_role(self, role: str) -> None:
        """Add a role to the user."""
        if role not in self.roles:
            self.roles.append(role)

    def remove_role(self, role: str) -> None:
        """Remove a role from the user."""
        if role in self.roles:
            self.roles.remove(role)


@dataclass
class Session:
    """Represents a user session."""
    session_id: str
    user_id: str
    created_at: float
    expires_at: float
    ip_address: str
    user_agent: str
    status: str
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary."""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "status": self.status,
            "metadata": self.metadata
        }

    def is_expired(self) -> bool:
        """Check if the session is expired."""
        return time.time() > self.expires_at

    def extend(self, duration: float) -> None:
        """Extend the session expiration."""
        self.expires_at = time.time() + duration


@dataclass
class AuthenticationToken:
    """Represents an authentication token."""
    token_id: str
    user_id: str
    token_hash: str
    created_at: float
    expires_at: float
    token_type: AuthenticationMethod
    status: str
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert token to dictionary."""
        return {
            "token_id": self.token_id,
            "user_id": self.user_id,
            "token_hash": self.token_hash,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "token_type": self.token_type,
            "status": self.status,
            "metadata": self.metadata
        }

    def is_expired(self) -> bool:
        """Check if the token is expired."""
        return time.time() > self.expires_at


class AuthenticationManager:
    """Manages user authentication and sessions."""

    def __init__(self):
        self._users: Dict[str, User] = {}
        self._sessions: Dict[str, Session] = {}
        self._tokens: Dict[str, AuthenticationToken] = {}
        self._lock = threading.Lock()
        
        # Default session duration (in seconds)
        self.session_duration = 3600  # 1 hour
        self.token_duration = 86400  # 24 hours

    def create_user(self, username: str, email: str, 
                   roles: Optional[List[str]] = None) -> User:
        """Create a new user."""
        user_id = str(uuid.uuid4())
        
        user = User(
            user_id=user_id,
            username=username,
            email=email,
            status=UserStatus.ACTIVE,
            roles=roles or [],
            created_at=time.time(),
            last_login=None,
            metadata={}
        )
        
        with self._lock:
            self._users[user_id] = user
        
        logger.info(f"Created user {username} with ID {user_id}")
        
        return user

    def get_user(self, user_id: str) -> Optional[User]:
        """Get a user by ID."""
        with self._lock:
            return self._users.get(user_id)

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get a user by username."""
        with self._lock:
            for user in self._users.values():
                if user.username == username:
                    return user
            return None

    def authenticate_user(self, username: str, password: str) -> Optional[Session]:
        """Authenticate a user and create a session."""
        user = self.get_user_by_username(username)
        if not user:
            logger.warning(f"Authentication failed: user {username} not found")
            return None
        
        # In a real implementation, this would verify the password
        # For now, we'll simulate successful authentication
        
        session_id = str(uuid.uuid4())
        
        session = Session(
            session_id=session_id,
            user_id=user.user_id,
            created_at=time.time(),
            expires_at=time.time() + self.session_duration,
            ip_address="127.0.0.1",  # Would be real IP in production
            user_agent="orchestrator-client",  # Would be real user agent
            status="active",
            metadata={}
        )
        
        with self._lock:
            self._sessions[session_id] = session
            user.last_login = time.time()
        
        logger.info(f"User {username} authenticated successfully, created session {session_id}")
        
        return session

    def create_token(self, user_id: str, token_type: AuthenticationMethod = AuthenticationMethod.TOKEN) -> AuthenticationToken:
        """Create an authentication token for a user."""
        user = self.get_user(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # Generate a random token
        token_value = str(uuid.uuid4())
        token_hash = self._hash_token(token_value)
        
        token = AuthenticationToken(
            token_id=str(uuid.uuid4()),
            user_id=user_id,
            token_hash=token_hash,
            created_at=time.time(),
            expires_at=time.time() + self.token_duration,
            token_type=token_type,
            status="active",
            metadata={}
        )
        
        with self._lock:
            self._tokens[token.token_id] = token
        
        logger.info(f"Created {token_type} token for user {user.username}")
        
        # Return the token value (in real implementation, this would be the actual token)
        return token

    def validate_token(self, token_value: str) -> Optional[User]:
        """Validate an authentication token."""
        token_hash = self._hash_token(token_value)
        
        with self._lock:
            for token in self._tokens.values():
                if (token.token_hash == token_hash and 
                    not token.is_expired() and 
                    token.status == "active"):
                    
                    user = self.get_user(token.user_id)
                    if user:
                        return user
        
        logger.warning(f"Token validation failed for token {token_value}")
        return None

    def get_session(self, session_id: str) -> Optional[Session]:
        """Get a session by ID."""
        with self._lock:
            return self._sessions.get(session_id)

    def invalidate_session(self, session_id: str) -> bool:
        """Invalidate a session."""
        with self._lock:
            session = self._sessions.get(session_id)
            if session:
                session.status = "invalidated"
                return True
            return False

    def invalidate_token(self, token_id: str) -> bool:
        """Invalidate an authentication token."""
        with self._lock:
            token = self._tokens.get(token_id)
            if token:
                token.status = "invalidated"
                return True
            return False

    def list_users(self) -> List[User]:
        """List all users."""
        with self._lock:
            return list(self._users.values())

    def list_sessions(self, user_id: Optional[str] = None) -> List[Session]:
        """List sessions."""
        with self._lock:
            if user_id:
                return [session for session in self._sessions.values() 
                       if session.user_id == user_id]
            else:
                return list(self._sessions.values())

    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions."""
        with self._lock:
            expired_count = 0
            for session_id, session in list(self._sessions.items()):
                if session.is_expired():
                    del self._sessions[session_id]
                    expired_count += 1
            
            logger.info(f"Cleaned up {expired_count} expired sessions")
            return expired_count

    def cleanup_expired_tokens(self) -> int:
        """Clean up expired tokens."""
        with self._lock:
            expired_count = 0
            for token_id, token in list(self._tokens.items()):
                if token.is_expired():
                    del self._tokens[token_id]
                    expired_count += 1
            
            logger.info(f"Cleaned up {expired_count} expired tokens")
            return expired_count

    def _hash_token(self, token: str) -> str:
        """Hash a token for secure storage."""
        return hashlib.sha256(token.encode()).hexdigest()

    def get_authentication_stats(self) -> Dict[str, Any]:
        """Get authentication statistics."""
        with self._lock:
            return {
                "users": {
                    "total": len(self._users),
                    "active": len([u for u in self._users.values() if u.status == UserStatus.ACTIVE]),
                    "inactive": len([u for u in self._users.values() if u.status == UserStatus.INACTIVE]),
                    "locked": len([u for u in self._users.values() if u.status == UserStatus.LOCKED])
                },
                "sessions": {
                    "total": len(self._sessions),
                    "active": len([s for s in self._sessions.values() if s.status == "active"]),
                    "expired": len([s for s in self._sessions.values() if s.is_expired()])
                },
                "tokens": {
                    "total": len(self._tokens),
                    "active": len([t for t in self._tokens.values() if t.status == "active"]),
                    "expired": len([t for t in self._tokens.values() if t.is_expired()])
                }
            }


# Global authentication manager instance
authentication_manager = AuthenticationManager()


def get_authentication_manager() -> AuthenticationManager:
    """Get the global authentication manager instance."""
    global authentication_manager
    return authentication_manager