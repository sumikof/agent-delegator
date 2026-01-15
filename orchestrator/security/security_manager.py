"""Security Manager.

This module provides a comprehensive security management system that integrates
authentication, authorization, and security policies for the orchestrator.
"""

from __future__ import annotations

import threading
from typing import Any, Dict, List, Optional
import logging

from .authentication import AuthenticationManager, User
from .authorization import AuthorizationManager, PermissionType, ResourceType

logger = logging.getLogger(__name__)


class SecurityManager:
    """Comprehensive security manager for the orchestrator."""

    def __init__(self):
        self.authentication_manager = AuthenticationManager()
        self.authorization_manager = AuthorizationManager()
        self._lock = threading.Lock()
        
        # Initialize with default roles and permissions
        self.authorization_manager.create_default_roles()

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user."""
        session = self.authentication_manager.authenticate_user(username, password)
        return self.authentication_manager.get_user(session.user_id) if session else None

    def authorize_user(self, user: User, permission_type: PermissionType,
                      resource_type: ResourceType, resource_id: Optional[str] = None) -> bool:
        """Check if a user is authorized for a specific action."""
        return self.authorization_manager.check_permission(
            user.roles, permission_type, resource_type, resource_id
        )

    def create_user_with_role(self, username: str, email: str, role_name: str) -> User:
        """Create a user and assign a role."""
        # Find the role
        role = None
        for r in self.authorization_manager.list_roles():
            if r.name == role_name:
                role = r
                break
        
        if not role:
            raise ValueError(f"Role {role_name} not found")
        
        # Create the user
        user = self.authentication_manager.create_user(username, email, [role.role_id])
        
        logger.info(f"Created user {username} with role {role_name}")
        
        return user

    def get_user_permissions(self, user: User) -> List[Dict[str, Any]]:
        """Get all permissions for a user."""
        permissions = []
        
        for role_id in user.roles:
            role = self.authorization_manager.get_role(role_id)
            if role:
                for permission in role.permissions:
                    permissions.append(permission.to_dict())
        
        return permissions

    def add_permission_to_user_role(self, user: User, permission_name: str) -> bool:
        """Add a permission to one of the user's roles."""
        # Find the permission
        permission = None
        for p in self.authorization_manager.list_permissions():
            if p.name == permission_name:
                permission = p
                break
        
        if not permission:
            return False
        
        # Add permission to all user roles
        success = True
        for role_id in user.roles:
            if not self.authorization_manager.add_permission_to_role(role_id, permission.permission_id):
                success = False
        
        return success

    def create_api_key(self, user: User, description: str = "") -> str:
        """Create an API key for a user."""
        # In a real implementation, this would generate and store a secure API key
        import uuid
        api_key = str(uuid.uuid4())
        
        # Store the API key (simplified)
        token = self.authentication_manager.create_token(
            user.user_id, 
            self.authentication_manager.AuthenticationMethod.API_KEY
        )
        
        logger.info(f"Created API key for user {user.username}")
        
        return api_key

    def validate_api_key(self, api_key: str) -> Optional[User]:
        """Validate an API key."""
        return self.authentication_manager.validate_token(api_key)

    def get_security_audit(self) -> Dict[str, Any]:
        """Get a security audit report."""
        auth_stats = self.authentication_manager.get_authentication_stats()
        authz_stats = self.authorization_manager.get_authorization_stats()
        
        return {
            "authentication": auth_stats,
            "authorization": authz_stats,
            "security_status": "operational"
        }

    def cleanup_expired_sessions_and_tokens(self) -> Dict[str, int]:
        """Clean up expired sessions and tokens."""
        expired_sessions = self.authentication_manager.cleanup_expired_sessions()
        expired_tokens = self.authentication_manager.cleanup_expired_tokens()
        
        return {
            "expired_sessions": expired_sessions,
            "expired_tokens": expired_tokens
        }


# Global security manager instance
security_manager = SecurityManager()


def get_security_manager() -> SecurityManager:
    """Get the global security manager instance."""
    global security_manager
    return security_manager