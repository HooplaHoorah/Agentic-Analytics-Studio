"""Quick test script for Revenue Forecasting agent."""

from aas.agents.revenue_forecasting import RevenueForecastingAgent

def test_revenue_forecasting():
    print("Testing Revenue Forecasting Agent...")
    
    agent = RevenueForecastingAgent()
    result = agent.run()
    
    print(f"\n✓ Analysis complete!")
    print(f"  - Generated {len(result['actions'])} actions")
    print(f"  - Forecasted Revenue: ${result['analysis']['forecasted_revenue']:,.0f}")
    print(f"  - Target Revenue: ${result['analysis']['target_revenue']:,.0f}")
    print(f"  - Shortfall: ${result['analysis']['shortfall']:,.0f} ({result['analysis']['shortfall_pct']:.1f}%)")
    print(f"  - Win Rate: {result['analysis']['win_rate']:.1%}")
    print(f"  - Avg Deal Velocity: {result['analysis']['avg_deal_velocity_days']:.0f} days")
    
    print("\nRecommended Actions:")
    for i, action in enumerate(result['actions'], 1):
        print(f"  {i}. [{action['priority'].upper()}] {action['title']}")
        print(f"     Impact Score: {action['impact_score']}")
    
    print("\n✓ Test passed!")
    return result

if __name__ == "__main__":
    test_revenue_forecasting()
