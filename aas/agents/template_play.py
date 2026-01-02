"""
Template Play - Use this as a starting point for creating new plays

INSTRUCTIONS:
1. Copy this file to aas/agents/your_play_name.py
2. Rename the class from TemplateAgent to YourPlayNameAgent
3. Implement the three required methods: load_data(), analyze(), recommend_actions()
4. Register your play in aas/plays/plays.py
5. Test with: python -c "from aas.plays import get_agent; agent = get_agent('your_play_id'); print(agent.run())"
"""

from typing import Any, Dict, List
from .base import AgentPlay
from ..models.action import Action
from ..utils.logger import get_logger

logger = get_logger(__name__)


class TemplateAgent(AgentPlay):
    """
    [REPLACE THIS] Brief one-line description of your play.
    
    [REPLACE THIS] Detailed description:
    This agent:
    1. Loads data from [source]
    2. Analyzes [what]
    3. Recommends [actions]
    
    Example use case: [describe a real-world scenario]
    """
    
    def __init__(self):
        """Initialize the agent with default parameters."""
        self.params = {}
        # Add any instance variables you need here
        # Example: self.threshold = 100
    
    def load_data(self) -> Any:
        """
        Load or fetch the data needed for this play.
        
        This method should:
        - Load data from a file, database, or API
        - Return the data in a format suitable for analysis
        - Handle errors gracefully (return mock data if needed)
        
        Returns:
            Any data structure (DataFrame, dict, list, etc.)
            Return None if no data is needed
        
        Example:
            # Load from CSV
            import pandas as pd
            df = pd.read_csv('path/to/data.csv')
            return df
            
            # Load from API
            import requests
            response = requests.get('https://api.example.com/data')
            return response.json()
            
            # Return mock data for demo
            return {"sample": "data"}
        """
        logger.info("Loading data for TemplateAgent")
        
        # TODO: Implement your data loading logic here
        # For now, return mock data
        mock_data = {
            "records": [
                {"id": 1, "value": 100, "status": "active"},
                {"id": 2, "value": 200, "status": "inactive"},
            ]
        }
        
        return mock_data
    
    def analyze(self, data: Any) -> Dict[str, Any]:
        """
        Perform analysis on the loaded data and return findings.
        
        This method should:
        - Process the data from load_data()
        - Calculate metrics, identify patterns, detect anomalies, etc.
        - Return a dictionary of findings
        
        Args:
            data: The data returned from load_data()
        
        Returns:
            Dictionary containing analysis results. Common keys:
            - "summary": High-level summary string
            - "metrics": Dict of calculated metrics
            - "findings": List of specific findings
            - "risk_score": Numeric risk/priority score
        
        Example:
            return {
                "summary": "Found 3 high-risk items",
                "metrics": {
                    "total_items": 100,
                    "high_risk_count": 3,
                    "avg_value": 150.5
                },
                "findings": [
                    {"item_id": 1, "risk": "high", "reason": "..."},
                    {"item_id": 2, "risk": "medium", "reason": "..."}
                ]
            }
        """
        logger.info("Analyzing data for TemplateAgent")
        
        # TODO: Implement your analysis logic here
        # Example analysis:
        if data is None or not data:
            return {"error": "No data available"}
        
        # Simple example: count records by status
        records = data.get("records", [])
        active_count = sum(1 for r in records if r.get("status") == "active")
        inactive_count = len(records) - active_count
        total_value = sum(r.get("value", 0) for r in records)
        
        return {
            "summary": f"Analyzed {len(records)} records",
            "metrics": {
                "total_records": len(records),
                "active_count": active_count,
                "inactive_count": inactive_count,
                "total_value": total_value,
                "avg_value": total_value / len(records) if records else 0
            },
            "findings": [
                {"type": "status_distribution", "active": active_count, "inactive": inactive_count}
            ]
        }
    
    def recommend_actions(self, analysis: Dict[str, Any]) -> List[Action]:
        """
        Generate recommended actions based on analysis results.
        
        This method should:
        - Review the analysis findings
        - Create Action objects for each recommendation
        - Prioritize actions by impact
        - Include AI rationales for transparency
        
        Args:
            analysis: The analysis results from analyze()
        
        Returns:
            List of Action objects. Each action should have:
            - type: String identifier (e.g., "salesforce_task", "slack_message")
            - title: Short, actionable title
            - description: Detailed description
            - priority: "high", "medium", or "low"
            - impact_score: Numeric score (higher = more important)
            - metadata: Additional context (dict)
            - reasoning: AI-generated rationale (use self.generate_rationale())
        
        Example:
            actions = []
            
            if analysis.get("risk_score", 0) > 80:
                actions.append(Action(
                    type="urgent_review",
                    title="Urgent: Review High-Risk Items",
                    description="3 items require immediate attention",
                    priority="high",
                    impact_score=analysis["risk_score"],
                    metadata={"item_ids": [1, 2, 3]},
                    reasoning=self.generate_rationale(
                        f"Risk score of {analysis['risk_score']} exceeds threshold"
                    )
                ))
            
            return actions
        """
        logger.info("Generating actions for TemplateAgent")
        
        actions = []
        
        # TODO: Implement your action generation logic here
        # Example: Create action if there are inactive records
        metrics = analysis.get("metrics", {})
        inactive_count = metrics.get("inactive_count", 0)
        
        if inactive_count > 0:
            context = f"Found {inactive_count} inactive records out of {metrics.get('total_records', 0)} total. " \
                     f"Total value: ${metrics.get('total_value', 0):,.0f}"
            
            actions.append(Action(
                type="review_inactive",
                title=f"Review {inactive_count} Inactive Records",
                description=f"There are {inactive_count} inactive records that may need attention. "
                           f"Consider reactivating or archiving them to maintain data quality.",
                priority="medium" if inactive_count < 5 else "high",
                impact_score=inactive_count * 10,  # Simple scoring: 10 points per inactive record
                metadata={
                    "inactive_count": inactive_count,
                    "total_value": metrics.get("total_value", 0),
                    "avg_value": metrics.get("avg_value", 0)
                },
                reasoning=self.generate_rationale(context)
            ))
        
        # Add more actions based on your analysis
        # Example: actions for high-value items, anomalies, etc.
        
        logger.info(f"Generated {len(actions)} actions")
        return actions


# REGISTRATION INSTRUCTIONS:
# After implementing your play, register it in aas/plays/plays.py:
#
# from ..agents.your_play_name import YourPlayNameAgent
#
# register_play(
#     id="your_play_id",
#     label="Your Play Name",
#     description="Brief description for UI dropdown",
#     agent_class=YourPlayNameAgent,
#     tags=["category1", "category2"],
#     inputs_schema={
#         "param1": {
#             "type": "string",
#             "description": "Description of param1",
#             "optional": True
#         }
#     },
#     demo_seed="your_play_demo_1",
#     icon="🎯"
# )
