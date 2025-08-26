"""
Authorization module for tenant management integration.

This module provides JWT-based tenant authentication and authorization
for Django applications consuming tokens from a tenant management system.
"""

__version__ = '1.0.0'
__author__ = 'Your Team'

# Don't import anything at module level to avoid circular imports
# Import these when needed in your code:
# from authorization.consumer_middleware import TenantFlagsMiddleware, has_feature, require_feature
# from authorization.utils import get_tenant_info, check_tenant_limit
# from authorization.models import TenantSession, TenantAuditLog
