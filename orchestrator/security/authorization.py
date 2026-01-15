"""Authorization System.

This module implements authorization and access control for the orchestrator,
including role-based access control (RBAC) and permission management.
"""

from __future__ import annotations

import threading
from typing import Any, Dict, List, Optional, Set
from enum import Enum
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


class PermissionType(str, Enum):
    """Types of permissions."""
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    ADMIN = "admin"
    MANAGE = "manage"


class ResourceType(str, Enum):
    """Types of resources."""
    AGENT = "agent"
    TASK = "task"
    WORKFLOW = "workflow"
    CONFIGURATION = "configuration"
    SYSTEM = "system"
    USER = "user"
    ROLE = "role"


@dataclass
class Permission:
    """Represents a permission."""
    permission_id: str
    name: str
    permission_type: PermissionType
    resource_type: ResourceType
    resource_id: Optional[str]
    description: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert permission to dictionary."""
        return {
            "permission_id": self.permission_id,
            "name": self.name,
            "permission_type": self.permission_type,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "description": self.description
        }


@dataclass
class Role:
    """Represents a role with associated permissions."""
    role_id: str
    name: str
    permissions: List[Permission]
    description: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert role to dictionary."""
        return {
            "role_id": self.role_id,
            "name": self.name,
            "permissions": [p.to_dict() for p in self.permissions],
            "description": self.description
        }

    def add_permission(self, permission: Permission) -> None:
        """Add a permission to the role."""
        if permission not in self.permissions:
            self.permissions.append(permission)

    def remove_permission(self, permission: Permission) -> None:
        """Remove a permission from the role."""
        if permission in self.permissions:
            self.permissions.remove(permission)

    def has_permission(self, permission_type: PermissionType, 
                      resource_type: ResourceType, resource_id: Optional[str] = None) -> bool:
        """Check if the role has a specific permission."""
        for permission in self.permissions:
            if (permission.permission_type == permission_type and
                permission.resource_type == resource_type and
                (resource_id is None or permission.resource_id == resource_id)):
                return True
        return False


class AuthorizationManager:
    """Manages authorization and access control."""

    def __init__(self):
        self._roles: Dict[str, Role] = {}
        self._permissions: Dict[str, Permission] = {}
        self._role_permissions: Dict[str, Set[str]] = {}  # role_id -> permission_ids
        self._lock = threading.Lock()

    def create_permission(self, name: str, permission_type: PermissionType,
                         resource_type: ResourceType, resource_id: Optional[str] = None,
                         description: str = "") -> Permission:
        """Create a new permission."""
        import uuid
        permission_id = str(uuid.uuid4())
        
        permission = Permission(
            permission_id=permission_id,
            name=name,
            permission_type=permission_type,
            resource_type=resource_type,
            resource_id=resource_id,
            description=description
        )
        
        with self._lock:
            self._permissions[permission_id] = permission
        
        logger.info(f"Created permission {name} for {resource_type}/{permission_type}")
        
        return permission

    def create_role(self, name: str, description: str = "") -> Role:
        """Create a new role."""
        import uuid
        role_id = str(uuid.uuid4())
        
        role = Role(
            role_id=role_id,
            name=name,
            permissions=[],
            description=description
        )
        
        with self._lock:
            self._roles[role_id] = role
            self._role_permissions[role_id] = set()
        
        logger.info(f"Created role {name}")
        
        return role

    def add_permission_to_role(self, role_id: str, permission_id: str) -> bool:
        """Add a permission to a role."""
        with self._lock:
            role = self._roles.get(role_id)
            permission = self._permissions.get(permission_id)
            
            if role and permission:
                role.add_permission(permission)
                self._role_permissions[role_id].add(permission_id)
                logger.info(f"Added permission {permission.name} to role {role.name}")
                return True
            return False

    def remove_permission_from_role(self, role_id: str, permission_id: str) -> bool:
        """Remove a permission from a role."""
        with self._lock:
            role = self._roles.get(role_id)
            permission = self._permissions.get(permission_id)
            
            if role and permission:
                role.remove_permission(permission)
                self._role_permissions[role_id].discard(permission_id)
                logger.info(f"Removed permission {permission.name} from role {role.name}")
                return True
            return False

    def get_role(self, role_id: str) -> Optional[Role]:
        """Get a role by ID."""
        with self._lock:
            return self._roles.get(role_id)

    def get_permission(self, permission_id: str) -> Optional[Permission]:
        """Get a permission by ID."""
        with self._lock:
            return self._permissions.get(permission_id)

    def check_permission(self, user_roles: List[str], permission_type: PermissionType,
                        resource_type: ResourceType, resource_id: Optional[str] = None) -> bool:
        """Check if a user with given roles has a specific permission."""
        with self._lock:
            for role_id in user_roles:
                role = self._roles.get(role_id)
                if role and role.has_permission(permission_type, resource_type, resource_id):
                    return True
            return False

    def list_roles(self) -> List[Role]:
        """List all roles."""
        with self._lock:
            return list(self._roles.values())

    def list_permissions(self) -> List[Permission]:
        """List all permissions."""
        with self._lock:
            return list(self._permissions.values())

    def get_role_permissions(self, role_id: str) -> List[Permission]:
        """Get all permissions for a role."""
        with self._lock:
            role = self._roles.get(role_id)
            return role.permissions if role else []

    def create_default_roles(self) -> None:
        """Create default roles and permissions."""
        with self._lock:
            # Create basic permissions
            read_agent = self.create_permission(
                "read_agent", PermissionType.READ, ResourceType.AGENT,
                description="Read agent information"
            )
            
            write_agent = self.create_permission(
                "write_agent", PermissionType.WRITE, ResourceType.AGENT,
                description="Modify agent configuration"
            )
            
            execute_task = self.create_permission(
                "execute_task", PermissionType.EXECUTE, ResourceType.TASK,
                description="Execute tasks"
            )
            
            manage_system = self.create_permission(
                "manage_system", PermissionType.ADMIN, ResourceType.SYSTEM,
                description="Manage system configuration"
            )
            
            # Create roles
            viewer_role = self.create_role("viewer", "Role for read-only access")
            operator_role = self.create_role("operator", "Role for operational tasks")
            admin_role = self.create_role("admin", "Role for system administration")
            
            # Assign permissions to roles
            self.add_permission_to_role(viewer_role.role_id, read_agent.permission_id)
            
            self.add_permission_to_role(operator_role.role_id, read_agent.permission_id)
            self.add_permission_to_role(operator_role.role_id, write_agent.permission_id)
            self.add_permission_to_role(operator_role.role_id, execute_task.permission_id)
            
            self.add_permission_to_role(admin_role.role_id, read_agent.permission_id)
            self.add_permission_to_role(admin_role.role_id, write_agent.permission_id)
            self.add_permission_to_role(admin_role.role_id, execute_task.permission_id)
            self.add_permission_to_role(admin_role.role_id, manage_system.permission_id)
            
            logger.info("Created default roles and permissions")

    def get_authorization_stats(self) -> Dict[str, Any]:
        """Get authorization statistics."""
        with self._lock:
            return {
                "roles": len(self._roles),
                "permissions": len(self._permissions),
                "role_permissions": sum(len(permissions) for permissions in self._role_permissions.values())
            }


# Global authorization manager instance
authorization_manager = AuthorizationManager()


def get_authorization_manager() -> AuthorizationManager:
    """Get the global authorization manager instance."""
    global authorization_manager
    return authorization_manager