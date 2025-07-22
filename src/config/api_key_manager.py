"""
API Key Manager

This module provides secure management of API keys with encryption,
rotation, and validation capabilities.
"""

import os
import json
import base64
import secrets
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from ..utils.logger import get_logger


@dataclass
class APIKeyInfo:
    """Information about an API key."""
    provider: str
    key_id: str
    api_key: str
    api_base: Optional[str] = None
    created_at: datetime = None
    last_used: datetime = None
    expires_at: Optional[datetime] = None
    usage_count: int = 0
    is_active: bool = True
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.metadata is None:
            self.metadata = {}


@dataclass
class KeyRotationPolicy:
    """Policy for automatic key rotation."""
    enabled: bool = True
    rotation_interval_days: int = 90
    warning_days_before: int = 7
    auto_rotate: bool = False
    backup_old_keys: bool = True


class APIKeyValidationError(Exception):
    """API key validation errors."""
    pass


class APIKeyManager:
    """
    Secure API key manager with encryption and rotation capabilities.
    
    Provides secure storage, validation, rotation, and monitoring
    of API keys for various service providers.
    """
    
    def __init__(self, storage_path: Optional[str] = None, master_password: Optional[str] = None):
        """
        Initialize the API key manager.
        
        Args:
            storage_path: Path to store encrypted keys
            master_password: Master password for encryption (optional)
        """
        self.logger = get_logger("api_key_manager")
        
        # Storage configuration
        self.storage_path = Path(storage_path) if storage_path else Path.home() / ".social-media-agent" / "keys"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Encryption setup
        self.master_password = master_password
        self.encryption_key = None
        self.cipher_suite = None
        self._setup_encryption()
        
        # Key storage
        self.keys_file = self.storage_path / "api_keys.encrypted"
        self.backup_dir = self.storage_path / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        # API keys storage
        self.api_keys: Dict[str, APIKeyInfo] = {}
        
        # Rotation policies
        self.rotation_policies: Dict[str, KeyRotationPolicy] = {}
        
        # Load existing keys
        self._load_keys()
        
        # Set up default rotation policies
        self._setup_default_policies()
        
        self.logger.info("API Key Manager initialized")
    
    def _setup_encryption(self):
        """Setup encryption for API key storage."""
        try:
            key_file = self.storage_path / "master.key"
            
            if key_file.exists():
                # Load existing key
                with open(key_file, "rb") as f:
                    self.encryption_key = f.read()
            else:
                # Generate new encryption key
                if self.master_password:
                    # Derive key from password
                    password = self.master_password.encode()
                    salt = os.urandom(16)
                    kdf = PBKDF2HMAC(
                        algorithm=hashes.SHA256(),
                        length=32,
                        salt=salt,
                        iterations=100000,
                    )
                    key = base64.urlsafe_b64encode(kdf.derive(password))
                    
                    # Store salt with key
                    key_data = {
                        "key": key.decode(),
                        "salt": base64.b64encode(salt).decode(),
                        "iterations": 100000
                    }
                    
                    with open(key_file, "w") as f:
                        json.dump(key_data, f)
                    
                    self.encryption_key = key
                else:
                    # Generate random key
                    self.encryption_key = Fernet.generate_key()
                    with open(key_file, "wb") as f:
                        f.write(self.encryption_key)
                
                # Set restrictive permissions
                os.chmod(key_file, 0o600)
            
            self.cipher_suite = Fernet(self.encryption_key)
            self.logger.info("Encryption setup completed")
            
        except Exception as e:
            self.logger.error(f"Failed to setup encryption: {e}")
            raise
    
    def _load_keys(self):
        """Load API keys from encrypted storage."""
        if not self.keys_file.exists():
            return
        
        try:
            with open(self.keys_file, "rb") as f:
                encrypted_data = f.read()
            
            decrypted_data = self.cipher_suite.decrypt(encrypted_data)
            keys_data = json.loads(decrypted_data.decode())
            
            # Convert to APIKeyInfo objects
            for key_id, key_data in keys_data.get("keys", {}).items():
                # Convert datetime strings back to datetime objects
                if "created_at" in key_data:
                    key_data["created_at"] = datetime.fromisoformat(key_data["created_at"])
                if "last_used" in key_data and key_data["last_used"]:
                    key_data["last_used"] = datetime.fromisoformat(key_data["last_used"])
                if "expires_at" in key_data and key_data["expires_at"]:
                    key_data["expires_at"] = datetime.fromisoformat(key_data["expires_at"])
                
                self.api_keys[key_id] = APIKeyInfo(**key_data)
            
            # Load rotation policies
            if "rotation_policies" in keys_data:
                for provider, policy_data in keys_data["rotation_policies"].items():
                    self.rotation_policies[provider] = KeyRotationPolicy(**policy_data)
            
            self.logger.info(f"Loaded {len(self.api_keys)} API keys")
            
        except Exception as e:
            self.logger.error(f"Failed to load API keys: {e}")
    
    def _save_keys(self):
        """Save API keys to encrypted storage."""
        try:
            # Create backup first
            self._create_backup()
            
            # Prepare data for saving
            keys_data = {
                "keys": {},
                "rotation_policies": {},
                "metadata": {
                    "version": "1.0",
                    "last_updated": datetime.utcnow().isoformat(),
                    "total_keys": len(self.api_keys)
                }
            }
            
            # Convert APIKeyInfo objects to dictionaries
            for key_id, key_info in self.api_keys.items():
                key_dict = asdict(key_info)
                
                # Convert datetime objects to ISO strings
                if key_dict["created_at"]:
                    key_dict["created_at"] = key_dict["created_at"].isoformat()
                if key_dict["last_used"]:
                    key_dict["last_used"] = key_dict["last_used"].isoformat()
                if key_dict["expires_at"]:
                    key_dict["expires_at"] = key_dict["expires_at"].isoformat()
                
                keys_data["keys"][key_id] = key_dict
            
            # Add rotation policies
            for provider, policy in self.rotation_policies.items():
                keys_data["rotation_policies"][provider] = asdict(policy)
            
            # Encrypt and save
            json_data = json.dumps(keys_data, indent=2)
            encrypted_data = self.cipher_suite.encrypt(json_data.encode())
            
            with open(self.keys_file, "wb") as f:
                f.write(encrypted_data)
            
            # Set restrictive permissions
            os.chmod(self.keys_file, 0o600)
            
            self.logger.info("API keys saved successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to save API keys: {e}")
            raise
    
    def _create_backup(self):
        """Create backup of current keys."""
        if not self.keys_file.exists():
            return
        
        try:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"keys_backup_{timestamp}.encrypted"
            
            import shutil
            shutil.copy2(self.keys_file, backup_file)
            
            # Keep only last 10 backups
            backups = sorted(self.backup_dir.glob("keys_backup_*.encrypted"))
            if len(backups) > 10:
                for old_backup in backups[:-10]:
                    old_backup.unlink()
            
            self.logger.debug(f"Backup created: {backup_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to create backup: {e}")
    
    def _setup_default_policies(self):
        """Setup default rotation policies for common providers."""
        default_policies = {
            "openai": KeyRotationPolicy(
                enabled=True,
                rotation_interval_days=90,
                warning_days_before=7,
                auto_rotate=False
            ),
            "anthropic": KeyRotationPolicy(
                enabled=True,
                rotation_interval_days=90,
                warning_days_before=7,
                auto_rotate=False
            ),
            "stability": KeyRotationPolicy(
                enabled=True,
                rotation_interval_days=60,
                warning_days_before=5,
                auto_rotate=False
            ),
            "facebook": KeyRotationPolicy(
                enabled=True,
                rotation_interval_days=180,
                warning_days_before=14,
                auto_rotate=False
            ),
            "twitter": KeyRotationPolicy(
                enabled=True,
                rotation_interval_days=90,
                warning_days_before=7,
                auto_rotate=False
            ),
            "instagram": KeyRotationPolicy(
                enabled=True,
                rotation_interval_days=180,
                warning_days_before=14,
                auto_rotate=False
            ),
            "linkedin": KeyRotationPolicy(
                enabled=True,
                rotation_interval_days=180,
                warning_days_before=14,
                auto_rotate=False
            ),
            "tiktok": KeyRotationPolicy(
                enabled=True,
                rotation_interval_days=90,
                warning_days_before=7,
                auto_rotate=False
            )
        }
        
        for provider, policy in default_policies.items():
            if provider not in self.rotation_policies:
                self.rotation_policies[provider] = policy
    
    def add_api_key(
        self,
        provider: str,
        api_key: str,
        api_base: Optional[str] = None,
        expires_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add a new API key.
        
        Args:
            provider: Provider name (e.g., 'openai', 'anthropic')
            api_key: The API key
            api_base: Optional API base URL
            expires_at: Optional expiration date
            metadata: Optional metadata
        
        Returns:
            Key ID for the stored key
        """
        # Generate unique key ID
        key_id = f"{provider}_{secrets.token_hex(8)}"
        
        # Validate API key format
        self._validate_api_key(provider, api_key)
        
        # Create key info
        key_info = APIKeyInfo(
            provider=provider,
            key_id=key_id,
            api_key=api_key,
            api_base=api_base,
            expires_at=expires_at,
            metadata=metadata or {}
        )
        
        # Store key
        self.api_keys[key_id] = key_info
        
        # Save to storage
        self._save_keys()
        
        self.logger.info(f"Added API key for provider: {provider}")
        return key_id
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """
        Get the active API key for a provider.
        
        Args:
            provider: Provider name
        
        Returns:
            API key string or None if not found
        """
        # Find active key for provider
        for key_info in self.api_keys.values():
            if (key_info.provider == provider and 
                key_info.is_active and 
                not self._is_key_expired(key_info)):
                
                # Update last used timestamp
                key_info.last_used = datetime.utcnow()
                key_info.usage_count += 1
                
                # Save updated info
                self._save_keys()
                
                return key_info.api_key
        
        return None
    
    def get_api_base(self, provider: str) -> Optional[str]:
        """
        Get the API base URL for a provider.
        
        Args:
            provider: Provider name
        
        Returns:
            API base URL or None if not found
        """
        for key_info in self.api_keys.values():
            if (key_info.provider == provider and 
                key_info.is_active and 
                not self._is_key_expired(key_info)):
                return key_info.api_base
        
        return None
    
    def get_key_info(self, key_id: str) -> Optional[APIKeyInfo]:
        """
        Get information about a specific key.
        
        Args:
            key_id: Key identifier
        
        Returns:
            APIKeyInfo object or None if not found
        """
        return self.api_keys.get(key_id)
    
    def list_keys(self, provider: Optional[str] = None) -> List[APIKeyInfo]:
        """
        List API keys, optionally filtered by provider.
        
        Args:
            provider: Optional provider filter
        
        Returns:
            List of APIKeyInfo objects
        """
        keys = list(self.api_keys.values())
        
        if provider:
            keys = [k for k in keys if k.provider == provider]
        
        return keys
    
    def deactivate_key(self, key_id: str):
        """
        Deactivate an API key.
        
        Args:
            key_id: Key identifier
        """
        if key_id in self.api_keys:
            self.api_keys[key_id].is_active = False
            self._save_keys()
            self.logger.info(f"Deactivated API key: {key_id}")
        else:
            raise ValueError(f"Key not found: {key_id}")
    
    def remove_key(self, key_id: str):
        """
        Remove an API key completely.
        
        Args:
            key_id: Key identifier
        """
        if key_id in self.api_keys:
            provider = self.api_keys[key_id].provider
            del self.api_keys[key_id]
            self._save_keys()
            self.logger.info(f"Removed API key for provider: {provider}")
        else:
            raise ValueError(f"Key not found: {key_id}")
    
    def rotate_key(self, provider: str, new_api_key: str, new_api_base: Optional[str] = None) -> str:
        """
        Rotate API key for a provider.
        
        Args:
            provider: Provider name
            new_api_key: New API key
            new_api_base: Optional new API base URL
        
        Returns:
            New key ID
        """
        # Deactivate old keys for this provider
        for key_info in self.api_keys.values():
            if key_info.provider == provider and key_info.is_active:
                key_info.is_active = False
        
        # Add new key
        new_key_id = self.add_api_key(provider, new_api_key, new_api_base)
        
        self.logger.info(f"Rotated API key for provider: {provider}")
        return new_key_id
    
    def check_key_expiration(self) -> Dict[str, List[str]]:
        """
        Check for expiring keys.
        
        Returns:
            Dictionary with 'expired' and 'expiring_soon' key lists
        """
        now = datetime.utcnow()
        expired = []
        expiring_soon = []
        
        for key_id, key_info in self.api_keys.items():
            if not key_info.is_active:
                continue
            
            # Check explicit expiration
            if key_info.expires_at and key_info.expires_at <= now:
                expired.append(key_id)
                continue
            
            # Check rotation policy
            policy = self.rotation_policies.get(key_info.provider)
            if policy and policy.enabled:
                rotation_date = key_info.created_at + timedelta(days=policy.rotation_interval_days)
                warning_date = rotation_date - timedelta(days=policy.warning_days_before)
                
                if rotation_date <= now:
                    expired.append(key_id)
                elif warning_date <= now:
                    expiring_soon.append(key_id)
        
        return {
            "expired": expired,
            "expiring_soon": expiring_soon
        }
    
    def _is_key_expired(self, key_info: APIKeyInfo) -> bool:
        """Check if a key is expired."""
        now = datetime.utcnow()
        
        # Check explicit expiration
        if key_info.expires_at and key_info.expires_at <= now:
            return True
        
        # Check rotation policy
        policy = self.rotation_policies.get(key_info.provider)
        if policy and policy.enabled:
            rotation_date = key_info.created_at + timedelta(days=policy.rotation_interval_days)
            if rotation_date <= now:
                return True
        
        return False
    
    def _validate_api_key(self, provider: str, api_key: str):
        """
        Validate API key format for a provider.
        
        Args:
            provider: Provider name
            api_key: API key to validate
        
        Raises:
            APIKeyValidationError: If key format is invalid
        """
        if not api_key or not isinstance(api_key, str):
            raise APIKeyValidationError("API key must be a non-empty string")
        
        # Provider-specific validation
        if provider == "openai":
            if not api_key.startswith("sk-"):
                raise APIKeyValidationError("OpenAI API key must start with 'sk-'")
            if len(api_key) < 20:
                raise APIKeyValidationError("OpenAI API key is too short")
        
        elif provider == "anthropic":
            if not api_key.startswith("sk-ant-"):
                raise APIKeyValidationError("Anthropic API key must start with 'sk-ant-'")
        
        elif provider == "stability":
            if len(api_key) < 20:
                raise APIKeyValidationError("Stability AI API key is too short")
        
        # Add more provider-specific validations as needed
    
    def validate_key_access(self, provider: str) -> bool:
        """
        Validate that we can access the API with the stored key.
        
        Args:
            provider: Provider name
        
        Returns:
            True if key is valid and accessible
        """
        api_key = self.get_api_key(provider)
        if not api_key:
            return False
        
        # This would make actual API calls to validate
        # For now, just check if key exists and is not expired
        for key_info in self.api_keys.values():
            if (key_info.provider == provider and 
                key_info.api_key == api_key and
                key_info.is_active and 
                not self._is_key_expired(key_info)):
                return True
        
        return False
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics for all keys."""
        stats = {
            "total_keys": len(self.api_keys),
            "active_keys": len([k for k in self.api_keys.values() if k.is_active]),
            "providers": {},
            "usage_by_provider": {},
            "expiration_status": self.check_key_expiration()
        }
        
        # Provider statistics
        for key_info in self.api_keys.values():
            provider = key_info.provider
            
            if provider not in stats["providers"]:
                stats["providers"][provider] = {
                    "total": 0,
                    "active": 0,
                    "expired": 0
                }
            
            stats["providers"][provider]["total"] += 1
            
            if key_info.is_active:
                if self._is_key_expired(key_info):
                    stats["providers"][provider]["expired"] += 1
                else:
                    stats["providers"][provider]["active"] += 1
            
            # Usage statistics
            if provider not in stats["usage_by_provider"]:
                stats["usage_by_provider"][provider] = {
                    "total_usage": 0,
                    "last_used": None
                }
            
            stats["usage_by_provider"][provider]["total_usage"] += key_info.usage_count
            
            if key_info.last_used:
                if (stats["usage_by_provider"][provider]["last_used"] is None or
                    key_info.last_used > stats["usage_by_provider"][provider]["last_used"]):
                    stats["usage_by_provider"][provider]["last_used"] = key_info.last_used
        
        return stats
    
    def export_keys(self, include_keys: bool = False) -> Dict[str, Any]:
        """
        Export key information for backup or analysis.
        
        Args:
            include_keys: Whether to include actual API keys (dangerous!)
        
        Returns:
            Dictionary with key information
        """
        export_data = {
            "metadata": {
                "export_timestamp": datetime.utcnow().isoformat(),
                "total_keys": len(self.api_keys),
                "include_keys": include_keys
            },
            "keys": {},
            "rotation_policies": {}
        }
        
        # Export key information
        for key_id, key_info in self.api_keys.items():
            key_data = {
                "provider": key_info.provider,
                "key_id": key_info.key_id,
                "created_at": key_info.created_at.isoformat() if key_info.created_at else None,
                "last_used": key_info.last_used.isoformat() if key_info.last_used else None,
                "expires_at": key_info.expires_at.isoformat() if key_info.expires_at else None,
                "usage_count": key_info.usage_count,
                "is_active": key_info.is_active,
                "metadata": key_info.metadata
            }
            
            if include_keys:
                key_data["api_key"] = key_info.api_key
                key_data["api_base"] = key_info.api_base
            
            export_data["keys"][key_id] = key_data
        
        # Export rotation policies
        for provider, policy in self.rotation_policies.items():
            export_data["rotation_policies"][provider] = asdict(policy)
        
        return export_data
    
    def set_rotation_policy(self, provider: str, policy: KeyRotationPolicy):
        """
        Set rotation policy for a provider.
        
        Args:
            provider: Provider name
            policy: Rotation policy
        """
        self.rotation_policies[provider] = policy
        self._save_keys()
        self.logger.info(f"Updated rotation policy for provider: {provider}")
    
    def get_rotation_policy(self, provider: str) -> Optional[KeyRotationPolicy]:
        """
        Get rotation policy for a provider.
        
        Args:
            provider: Provider name
        
        Returns:
            KeyRotationPolicy or None if not found
        """
        return self.rotation_policies.get(provider)
    
    def cleanup_expired_keys(self):
        """Remove expired and inactive keys."""
        to_remove = []
        
        for key_id, key_info in self.api_keys.items():
            if not key_info.is_active or self._is_key_expired(key_info):
                # Keep keys for 30 days after expiration for audit purposes
                if key_info.created_at < datetime.utcnow() - timedelta(days=30):
                    to_remove.append(key_id)
        
        for key_id in to_remove:
            del self.api_keys[key_id]
        
        if to_remove:
            self._save_keys()
            self.logger.info(f"Cleaned up {len(to_remove)} expired keys")
    
    def get_environment_variables(self) -> Dict[str, str]:
        """
        Get environment variables for active API keys.
        
        Returns:
            Dictionary of environment variables
        """
        env_vars = {}
        
        for key_info in self.api_keys.values():
            if key_info.is_active and not self._is_key_expired(key_info):
                env_key = f"{key_info.provider.upper()}_API_KEY"
                env_vars[env_key] = key_info.api_key
                
                if key_info.api_base:
                    base_key = f"{key_info.provider.upper()}_API_BASE"
                    env_vars[base_key] = key_info.api_base
        
        return env_vars

