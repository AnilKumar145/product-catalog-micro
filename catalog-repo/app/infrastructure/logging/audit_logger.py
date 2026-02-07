"""Audit logging for tracking user actions."""

import logging
import json
from datetime import datetime
from typing import Optional
from app.config.settings import get_settings


class AuditLogger:
    """Audit logger for tracking critical operations."""
    
    def __init__(self):
        settings = get_settings()
        self.logger = logging.getLogger("audit")
        handler = logging.FileHandler(settings.AUDIT_LOG_FILE)
        handler.setFormatter(logging.Formatter('%(message)s'))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log(self, user_id: Optional[str], action: str, resource: str, details: dict):
        """Log audit event."""
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "details": details
        }
        self.logger.info(json.dumps(audit_entry))


audit_logger = AuditLogger()
