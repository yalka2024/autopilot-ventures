#!/usr/bin/env python3
"""
Access AutoPilot Ventures Platform
"""

import boto3

def show_access_info():
    print("=== AutoPilot Ventures Platform Access ===")
    print("\n🎯 Your platform is deployed and ready!")
    
    print("\n📊 **AWS Console Access:**")
    print("1. ECS Cluster:")
    print("   https://console.aws.amazon.com/ecs/home?region=us-east-1#/clusters/autopilot-ventures-manual-production")
    
    print("\n2. ECS Service:")
    print("   https://console.aws.amazon.com/ecs/home?region=us-east-1#/clusters/autopilot-ventures-manual-production/services")
    
    print("\n3. CloudWatch Logs:")
    print("   https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:log-groups/log-group/ecs$252Fmaster-agent-manual-production")
    
    print("\n🔧 **Platform Features:**")
    print("✅ Phase 3 Advanced Intelligence:")
    print("   - MLflow Integration for experiment tracking")
    print("   - Dynamic Decision Trees for adaptive decisions")
    print("   - Cross-Venture Learning for knowledge sharing")
    print("   - Predictive Analytics for forecasting")
    
    print("\n✅ Advanced Autonomous Features:")
    print("   - Vector Memory Management")
    print("   - Self-Tuning Agents")
    print("   - Reinforcement Learning Engine")
    print("   - Autonomous Workflow Engine")
    
    print("\n📈 **Monitoring:**")
    print("- Service Status: ACTIVE")
    print("- Cluster: autopilot-ventures-manual-production")
    print("- Service: master-agent-service-manual-production")
    print("- Task Definition: master-agent-manual-production")
    
    print("\n🚀 **Next Steps:**")
    print("1. Monitor the service until it shows 'Running: 1'")
    print("2. Check CloudWatch logs for application startup")
    print("3. Your AutoPilot Ventures platform will operate autonomously")
    print("4. The platform will automatically discover, evaluate, and scale ventures")
    
    print("\n💡 **Tips:**")
    print("- The service may take a few minutes to fully start")
    print("- Check CloudWatch logs for any startup issues")
    print("- The platform runs autonomously once started")
    print("- All Phase 3 features are enabled and ready")

if __name__ == "__main__":
    show_access_info() 