"""
Impact Analytics Module

Provides endpoints and utilities for calculating and reporting
the aggregate business impact of AAS recommendations.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
from ..db import get_conn
import json


def calculate_aggregate_impact() -> Dict[str, Any]:
    """
    Calculate aggregate impact metrics across all plays and actions.
    
    Returns:
        Dictionary containing:
        - total_runs: Number of pipeline runs
        - total_actions: Number of actions generated
        - total_approved: Number of actions approved
        - total_executed: Number of actions executed
        - total_impact_score: Sum of all impact scores
        - estimated_value: Estimated dollar value (heuristic)
        - top_plays: Top 3 plays by impact
        - recent_activity: Last 7 days of activity
    """
    conn = get_conn()
    if not conn:
        # Fallback to mock data if no DB
        return _generate_mock_impact_data()
    
    try:
        with conn.cursor() as cur:
            # Total runs
            cur.execute("SELECT COUNT(*) FROM aas_pipeline_runs")
            total_runs = cur.fetchone()[0] or 0
            
            # Total actions by status
            cur.execute("""
                SELECT status, COUNT(*), COALESCE(SUM(impact_score), 0)
                FROM aas_actions
                GROUP BY status
            """)
            status_counts = {}
            total_actions = 0
            total_impact = 0
            for row in cur.fetchall():
                status, count, impact = row
                status_counts[status] = {"count": count, "impact": impact}
                total_actions += count
                total_impact += impact
            
            total_approved = status_counts.get("approved", {}).get("count", 0) + \
                           status_counts.get("executed", {}).get("count", 0)
            total_executed = status_counts.get("executed", {}).get("count", 0)
            
            # Top plays by impact
            cur.execute("""
                SELECT r.play, COUNT(a.action_id) as action_count, 
                       COALESCE(SUM(a.impact_score), 0) as total_impact
                FROM aas_pipeline_runs r
                LEFT JOIN aas_actions a ON r.run_id = a.run_id
                GROUP BY r.play
                ORDER BY total_impact DESC
                LIMIT 3
            """)
            top_plays = []
            for row in cur.fetchall():
                play, count, impact = row
                top_plays.append({
                    "play": play,
                    "action_count": count,
                    "total_impact": float(impact) if impact else 0
                })
            
            # Recent activity (last 7 days)
            seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
            cur.execute("""
                SELECT DATE(run_ts) as date, COUNT(*) as runs
                FROM aas_pipeline_runs
                WHERE run_ts >= %s
                GROUP BY DATE(run_ts)
                ORDER BY date DESC
            """, (seven_days_ago,))
            recent_activity = [
                {"date": str(row[0]), "runs": row[1]}
                for row in cur.fetchall()
            ]
            
            # Estimated dollar value (heuristic: impact_score * $1000)
            estimated_value = total_impact * 1000
            
            conn.close()
            
            return {
                "total_runs": total_runs,
                "total_actions": total_actions,
                "total_approved": total_approved,
                "total_executed": total_executed,
                "total_impact_score": float(total_impact),
                "estimated_value": estimated_value,
                "top_plays": top_plays,
                "recent_activity": recent_activity,
                "status_breakdown": {
                    k: {"count": v["count"], "impact": float(v["impact"])}
                    for k, v in status_counts.items()
                },
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
    
    except Exception as e:
        print(f"Error calculating impact: {e}")
        return _generate_mock_impact_data()


def _generate_mock_impact_data() -> Dict[str, Any]:
    """Generate mock impact data for demo purposes."""
    return {
        "total_runs": 15,
        "total_actions": 42,
        "total_approved": 28,
        "total_executed": 22,
        "total_impact_score": 3250.0,
        "estimated_value": 3250000.0,  # $3.25M
        "top_plays": [
            {"play": "pipeline", "action_count": 18, "total_impact": 1500.0},
            {"play": "revenue", "action_count": 12, "total_impact": 1200.0},
            {"play": "churn", "action_count": 8, "total_impact": 450.0}
        ],
        "recent_activity": [
            {"date": "2026-01-02", "runs": 3},
            {"date": "2026-01-01", "runs": 5},
            {"date": "2025-12-31", "runs": 2}
        ],
        "status_breakdown": {
            "pending": {"count": 14, "impact": 1000.0},
            "approved": {"count": 6, "impact": 800.0},
            "executed": {"count": 22, "impact": 1450.0}
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "note": "Mock data - connect database for real metrics"
    }


def export_impact_report_csv() -> str:
    """
    Generate CSV export of impact report.
    
    Returns:
        CSV string with impact metrics
    """
    data = calculate_aggregate_impact()
    
    lines = []
    lines.append("Agentic Analytics Studio - Impact Report")
    lines.append(f"Generated: {data['generated_at']}")
    lines.append("")
    
    lines.append("Summary Metrics")
    lines.append("Metric,Value")
    lines.append(f"Total Runs,{data['total_runs']}")
    lines.append(f"Total Actions Generated,{data['total_actions']}")
    lines.append(f"Total Actions Approved,{data['total_approved']}")
    lines.append(f"Total Actions Executed,{data['total_executed']}")
    lines.append(f"Total Impact Score,{data['total_impact_score']:.2f}")
    lines.append(f"Estimated Value (USD),${data['estimated_value']:,.0f}")
    lines.append("")
    
    lines.append("Top Plays by Impact")
    lines.append("Play,Action Count,Total Impact")
    for play in data['top_plays']:
        lines.append(f"{play['play']},{play['action_count']},{play['total_impact']:.2f}")
    lines.append("")
    
    lines.append("Status Breakdown")
    lines.append("Status,Count,Impact Score")
    for status, metrics in data['status_breakdown'].items():
        lines.append(f"{status},{metrics['count']},{metrics['impact']:.2f}")
    lines.append("")
    
    lines.append("Recent Activity (Last 7 Days)")
    lines.append("Date,Runs")
    for activity in data['recent_activity']:
        lines.append(f"{activity['date']},{activity['runs']}")
    
    return "\n".join(lines)
