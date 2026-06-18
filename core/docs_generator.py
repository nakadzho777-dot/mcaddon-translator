import json
from datetime import datetime

from core.analytics_engine import get_analytics_report
from core.cost_manager import get_total_cost
from core.audit_logger import audit_report
from core.ops_dashboard import get_dashboard


# =========================
# システム概要ドキュメント
# =========================
def generate_system_docs():
    dashboard = get_dashboard()

    docs = {
        "title": "System API & Architecture Documentation",
        "generated_at": datetime.now().isoformat(),

        "overview": {
            "status": "production-ready",
            "health_score": dashboard["health_score"],
            "active_users": dashboard["analytics"]["active_users_7d"]
        },

        "modules": [
            "auth_system",
            "analytics_engine",
            "cost_manager",
            "audit_logger",
            "job_queue",
            "ux_orchestrator",
            "security_layer",
            "cicd_pipeline",
            "backup_system",
            "scaling_manager"
        ],

        "api_contracts": {
            "base_url": "/api/v1",
            "auth": "API_KEY_REQUIRED",
            "rate_limit": "10 req/min"
        },

        "performance": {
            "cost": get_total_cost(),
            "audit_events": audit_report()["total_actions"]
        }
    }

    return docs


# =========================
# Markdown出力
# =========================
def export_markdown():
    docs = generate_system_docs()

    md = f"""
# 🚀 System Documentation

## Overview
- Status: {docs['overview']['status']}
- Health Score: {docs['overview']['health_score']}
- Active Users: {docs['overview']['active_users']}

## Modules
{chr(10).join(['- ' + m for m in docs['modules']])}

## API
- Base URL: {docs['api_contracts']['base_url']}
- Auth: {docs['api_contracts']['auth']}
- Rate Limit: {docs['api_contracts']['rate_limit']}

## Performance
- Cost: {docs['performance']['cost']}
- Audit Events: {docs['performance']['audit_events']}
"""

    return md


# =========================
# JSONエクスポート
# =========================
def export_json():
    return json.dumps(generate_system_docs(), indent=2, ensure_ascii=False)