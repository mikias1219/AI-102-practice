"""
Agent Testing and Optimization Framework
Tests, optimizes, and deploys agents with performance metrics
"""

import time
import json
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Callable
from datetime import datetime
from abc import ABC, abstractmethod


# ============================================================================
# PERFORMANCE METRICS
# ============================================================================

@dataclass
class PerformanceMetrics:
    """Agent performance metrics"""
    response_time: float
    accuracy: float
    token_count: int
    cost: float
    timestamp: str
    test_name: str
    passed: bool


class MetricsCollector:
    """Collects and analyzes agent performance metrics"""
    
    def __init__(self):
        self.metrics: List[PerformanceMetrics] = []
    
    def record_metric(self, metric: PerformanceMetrics):
        """Record a performance metric"""
        self.metrics.append(metric)
    
    def get_average_response_time(self) -> float:
        """Get average response time"""
        if not self.metrics:
            return 0.0
        return sum(m.response_time for m in self.metrics) / len(self.metrics)
    
    def get_success_rate(self) -> float:
        """Get test success rate"""
        if not self.metrics:
            return 0.0
        passed = sum(1 for m in self.metrics if m.passed)
        return (passed / len(self.metrics)) * 100
    
    def get_average_accuracy(self) -> float:
        """Get average accuracy"""
        if not self.metrics:
            return 0.0
        return sum(m.accuracy for m in self.metrics) / len(self.metrics)
    
    def get_total_cost(self) -> float:
        """Get total cost of all tests"""
        return sum(m.cost for m in self.metrics)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary"""
        return {
            "total_tests": len(self.metrics),
            "average_response_time": self.get_average_response_time(),
            "success_rate": self.get_success_rate(),
            "average_accuracy": self.get_average_accuracy(),
            "total_cost": self.get_total_cost(),
            "timestamp": datetime.now().isoformat()
        }


# ============================================================================
# TEST CASES
# ============================================================================

@dataclass
class TestCase:
    """Represents a test case"""
    name: str
    input: str
    expected_output: str
    timeout: int = 30
    priority: str = "normal"  # critical, high, normal, low


class AgentTester:
    """Tests agent performance and reliability"""
    
    def __init__(self, agent):
        self.agent = agent
        self.metrics = MetricsCollector()
    
    async def run_test(self, test_case: TestCase) -> PerformanceMetrics:
        """
        Run a single test case
        Returns: PerformanceMetrics
        """
        start_time = time.time()
        passed = False
        accuracy = 0.0
        
        try:
            # Run agent with timeout
            response = await self.agent.process(test_case.input)
            response_time = time.time() - start_time
            
            # Simple accuracy check (can be enhanced)
            accuracy = self._calculate_accuracy(response, test_case.expected_output)
            passed = accuracy > 0.7  # 70% threshold
            
            metric = PerformanceMetrics(
                response_time=response_time,
                accuracy=accuracy,
                token_count=len(response.split()),
                cost=0.001,  # Simplified cost calculation
                timestamp=datetime.now().isoformat(),
                test_name=test_case.name,
                passed=passed
            )
            
            self.metrics.record_metric(metric)
            return metric
            
        except Exception as e:
            response_time = time.time() - start_time
            metric = PerformanceMetrics(
                response_time=response_time,
                accuracy=0.0,
                token_count=0,
                cost=0.001,
                timestamp=datetime.now().isoformat(),
                test_name=test_case.name,
                passed=False
            )
            self.metrics.record_metric(metric)
            return metric
    
    def _calculate_accuracy(self, response: str, expected: str) -> float:
        """Calculate similarity between response and expected"""
        # Simple word overlap calculation
        response_words = set(response.lower().split())
        expected_words = set(expected.lower().split())
        
        if not expected_words:
            return 1.0
        
        overlap = len(response_words & expected_words)
        accuracy = overlap / len(expected_words)
        return min(accuracy, 1.0)
    
    async def run_test_suite(self, test_cases: List[TestCase]) -> Dict[str, Any]:
        """
        Run multiple test cases
        Returns: Summary of results
        """
        results = []
        for test_case in test_cases:
            result = await self.run_test(test_case)
            results.append(asdict(result))
        
        return {
            "test_results": results,
            "summary": self.metrics.get_summary()
        }


# ============================================================================
# AGENT OPTIMIZATION
# ============================================================================

class AgentOptimizer:
    """Optimizes agent performance"""
    
    def __init__(self, agent):
        self.agent = agent
        self.optimization_history = []
    
    def optimize_temperature(self, current_temp: float, direction: str = "decrease") -> float:
        """
        Optimize temperature parameter
        direction: "increase" or "decrease"
        """
        adjustment = 0.1
        new_temp = current_temp + adjustment if direction == "increase" else current_temp - adjustment
        new_temp = max(0.0, min(2.0, new_temp))  # Clamp between 0 and 2
        
        self.optimization_history.append({
            "parameter": "temperature",
            "old_value": current_temp,
            "new_value": new_temp,
            "timestamp": datetime.now().isoformat()
        })
        
        return new_temp
    
    def optimize_max_tokens(self, current_tokens: int, direction: str = "decrease") -> int:
        """Optimize max tokens parameter"""
        adjustment = 250
        new_tokens = current_tokens + adjustment if direction == "increase" else current_tokens - adjustment
        new_tokens = max(100, min(4000, new_tokens))  # Reasonable bounds
        
        self.optimization_history.append({
            "parameter": "max_tokens",
            "old_value": current_tokens,
            "new_value": new_tokens,
            "timestamp": datetime.now().isoformat()
        })
        
        return new_tokens
    
    def get_optimization_recommendations(self, metrics: MetricsCollector) -> List[str]:
        """Get optimization recommendations based on metrics"""
        recommendations = []
        summary = metrics.get_summary()
        
        if summary["average_response_time"] > 5.0:
            recommendations.append("Consider reducing max_tokens for faster responses")
            recommendations.append("Increase temperature to reduce model deliberation")
        
        if summary["success_rate"] < 70:
            recommendations.append("Increase temperature for more creative responses")
            recommendations.append("Add more diverse training examples")
            recommendations.append("Review system prompt clarity")
        
        if summary["average_accuracy"] < 0.7:
            recommendations.append("Improve prompt engineering")
            recommendations.append("Add context to inputs")
            recommendations.append("Review expected outputs for accuracy")
        
        return recommendations


# ============================================================================
# DEPLOYMENT CONFIGURATION
# ============================================================================

@dataclass
class DeploymentConfig:
    """Configuration for agent deployment"""
    name: str
    version: str
    environment: str  # development, staging, production
    resource_group: str
    region: str
    min_replicas: int = 1
    max_replicas: int = 3
    monitoring_enabled: bool = True
    auto_scale: bool = True


class AgentDeployer:
    """Manages agent deployment"""
    
    def __init__(self, config: DeploymentConfig):
        self.config = config
        self.deployment_log = []
    
    def validate_deployment_config(self) -> bool:
        """Validate deployment configuration"""
        checks = [
            bool(self.config.name),
            bool(self.config.version),
            self.config.min_replicas <= self.config.max_replicas,
            self.config.min_replicas >= 1,
            self.config.environment in ["development", "staging", "production"]
        ]
        return all(checks)
    
    def pre_deployment_checks(self) -> Dict[str, Any]:
        """Run pre-deployment checks"""
        checks = {
            "config_valid": self.validate_deployment_config(),
            "timestamp": datetime.now().isoformat(),
            "checklist": [
                {"name": "Configuration Validation", "passed": self.validate_deployment_config()},
                {"name": "Environment Check", "passed": bool(self.config.environment)},
                {"name": "Resource Check", "passed": bool(self.config.resource_group)},
            ]
        }
        return checks
    
    def get_deployment_script(self) -> str:
        """Generate deployment script"""
        script = f"""
#!/bin/bash
# Azure AI Agent Deployment Script
# Agent: {self.config.name}
# Version: {self.config.version}
# Environment: {self.config.environment}

echo "🚀 Deploying {self.config.name}..."

# Deploy to Azure
az containerapp create \\
  --name {self.config.name} \\
  --resource-group {self.config.resource_group} \\
  --environment {self.config.environment} \\
  --min-replicas {self.config.min_replicas} \\
  --max-replicas {self.config.max_replicas}

echo "✅ Deployment complete!"
"""
        return script
    
    def log_deployment(self, status: str, message: str):
        """Log deployment action"""
        self.deployment_log.append({
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })


# ============================================================================
# MONITORING AND OBSERVABILITY
# ============================================================================

class AgentMonitor:
    """Monitors agent performance in production"""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.events = []
        self.alerts = []
    
    def record_event(self, event_type: str, details: Dict):
        """Record monitoring event"""
        self.events.append({
            "type": event_type,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def check_health(self, metrics: PerformanceMetrics) -> str:
        """Check agent health based on metrics"""
        if metrics.response_time > 10:
            status = "warning"
            self.alerts.append(f"High response time: {metrics.response_time}s")
        elif metrics.response_time > 20:
            status = "critical"
            self.alerts.append(f"Critical response time: {metrics.response_time}s")
        else:
            status = "healthy"
        
        return status
    
    def get_health_report(self) -> Dict[str, Any]:
        """Get health report"""
        return {
            "agent": self.agent_name,
            "total_events": len(self.events),
            "total_alerts": len(self.alerts),
            "alerts": self.alerts[-10:],  # Last 10 alerts
            "timestamp": datetime.now().isoformat()
        }


# ============================================================================
# TESTING UTILITIES
# ============================================================================

def create_test_suite_for_agent(agent_name: str) -> List[TestCase]:
    """Create standard test suite for agent"""
    return [
        TestCase(
            name="Basic Greeting",
            input="Hello, how are you?",
            expected_output="greeting response",
            priority="high"
        ),
        TestCase(
            name="Question Answering",
            input="What is machine learning?",
            expected_output="machine learning definition explanation",
            priority="critical"
        ),
        TestCase(
            name="Task Completion",
            input="Help me with a problem",
            expected_output="problem solving assistance",
            priority="high"
        ),
        TestCase(
            name="Complex Reasoning",
            input="Compare and contrast different approaches",
            expected_output="comparison analysis",
            priority="normal"
        ),
    ]


def export_metrics_to_json(metrics: MetricsCollector, filename: str) -> str:
    """Export metrics to JSON file"""
    data = {
        "metrics": [asdict(m) for m in metrics.metrics],
        "summary": metrics.get_summary()
    }
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    return filename




