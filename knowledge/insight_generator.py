"""
Insight Generator - Provides intelligent insights and recommendations.

Generates actionable insights, recommendations, and predictive analysis
based on knowledge graph patterns and trends.
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import defaultdict
import json

from .graph_builder import KnowledgeGraphBuilder
from .pattern_analyzer import PatternAnalyzer, Pattern, Trend


@dataclass
class Insight:
    """Represents an actionable insight."""
    insight_type: str
    title: str
    description: str
    confidence: float
    priority: str  # high, medium, low
    actionable: bool
    recommendations: List[str]
    related_entities: List[str]
    timestamp: datetime
    metadata: Dict


@dataclass
class Recommendation:
    """Represents a specific recommendation."""
    title: str
    description: str
    action_type: str  # immediate, scheduled, monitoring
    priority: str
    estimated_impact: str
    prerequisites: List[str]
    metadata: Dict


class InsightGenerator:
    """Generates intelligent insights and recommendations from knowledge graph analysis."""
    
    def __init__(self, graph_builder: KnowledgeGraphBuilder, pattern_analyzer: PatternAnalyzer):
        self.graph_builder = graph_builder
        self.pattern_analyzer = pattern_analyzer
        self.insights: List[Insight] = []
        self.recommendations: List[Recommendation] = []
    
    def generate_insights(self) -> List[Insight]:
        """Generate comprehensive insights from knowledge graph analysis."""
        insights = []
        
        # Get pattern analysis
        pattern_data = self.pattern_analyzer.generate_insights()
        
        # Generate insights from temporal patterns
        insights.extend(self._analyze_temporal_patterns(pattern_data["temporal_patterns"]))
        
        # Generate insights from relationship clusters
        insights.extend(self._analyze_relationship_clusters(pattern_data["relationship_clusters"]))
        
        # Generate insights from behavioral trends
        insights.extend(self._analyze_behavioral_trends(pattern_data["behavioral_trends"]))
        
        # Generate insights from anomalies
        insights.extend(self._analyze_anomalies(pattern_data["anomalies"]))
        
        # Generate predictive insights
        insights.extend(self._generate_predictive_insights(pattern_data))
        
        self.insights = insights
        return insights
    
    def _analyze_temporal_patterns(self, patterns: List[Pattern]) -> List[Insight]:
        """Analyze temporal patterns and generate insights."""
        insights = []
        
        for pattern in patterns:
            if pattern.pattern_type == "daily_entity_type":
                insight = Insight(
                    insight_type="temporal_pattern",
                    title=f"Daily Pattern: {pattern.metadata['entity_type']} Activity",
                    description=f"High concentration of {pattern.metadata['entity_type']} activity detected on {pattern.metadata['day']}",
                    confidence=pattern.confidence,
                    priority="medium" if pattern.frequency > 5 else "low",
                    actionable=True,
                    recommendations=[
                        f"Schedule {pattern.metadata['entity_type']}-related tasks for {pattern.metadata['day']}",
                        f"Monitor for recurring patterns on similar days",
                        f"Consider automation for {pattern.metadata['entity_type']} processing"
                    ],
                    related_entities=pattern.entities,
                    timestamp=datetime.now(),
                    metadata=pattern.metadata
                )
                insights.append(insight)
        
        return insights
    
    def _analyze_relationship_clusters(self, patterns: List[Pattern]) -> List[Insight]:
        """Analyze relationship clusters and generate insights."""
        insights = []
        
        for pattern in patterns:
            if pattern.pattern_type == "relationship_cluster":
                cluster_size = pattern.metadata["cluster_size"]
                avg_strength = pattern.metadata["avg_strength"]
                
                insight = Insight(
                    insight_type="relationship_cluster",
                    title=f"Strong Entity Cluster ({cluster_size} entities)",
                    description=f"Detected a cluster of {cluster_size} strongly connected entities with average relationship strength of {avg_strength:.2f}",
                    confidence=pattern.confidence,
                    priority="high" if avg_strength > 0.8 else "medium",
                    actionable=True,
                    recommendations=[
                        "Investigate the nature of these strong relationships",
                        "Consider grouping related tasks or communications",
                        "Monitor for new entities joining this cluster"
                    ],
                    related_entities=pattern.entities,
                    timestamp=datetime.now(),
                    metadata=pattern.metadata
                )
                insights.append(insight)
        
        return insights
    
    def _analyze_behavioral_trends(self, trends: List[Trend]) -> List[Insight]:
        """Analyze behavioral trends and generate insights."""
        insights = []
        
        for trend in trends:
            if trend.direction != "stable":
                insight = Insight(
                    insight_type="behavioral_trend",
                    title=f"{trend.trend_type.replace('_', ' ').title()} Trend",
                    description=f"{trend.description} over the past {trend.time_period}",
                    confidence=trend.confidence,
                    priority="high" if abs(trend.magnitude) > 0.5 else "medium",
                    actionable=True,
                    recommendations=[
                        f"Investigate the cause of {trend.direction} {trend.trend_type}",
                        "Adjust monitoring and alerting thresholds",
                        "Consider proactive measures based on trend direction"
                    ],
                    related_entities=trend.entities_involved,
                    timestamp=datetime.now(),
                    metadata={
                        "trend_type": trend.trend_type,
                        "direction": trend.direction,
                        "magnitude": trend.magnitude,
                        "time_period": trend.time_period
                    }
                )
                insights.append(insight)
        
        return insights
    
    def _analyze_anomalies(self, anomalies: List[Pattern]) -> List[Insight]:
        """Analyze anomalies and generate insights."""
        insights = []
        
        for anomaly in anomalies:
            if anomaly.pattern_type == "frequency_anomaly":
                z_score = anomaly.metadata["z_score"]
                entity_type = anomaly.metadata["entity_type"]
                
                insight = Insight(
                    insight_type="anomaly",
                    title=f"Anomalous {entity_type} Activity",
                    description=f"Unusual frequency of {entity_type} entities detected (z-score: {z_score:.2f})",
                    confidence=anomaly.confidence,
                    priority="high" if z_score > 3.0 else "medium",
                    actionable=True,
                    recommendations=[
                        "Investigate the cause of unusual activity",
                        "Check for system issues or external factors",
                        "Consider if this represents a new normal pattern"
                    ],
                    related_entities=anomaly.entities,
                    timestamp=datetime.now(),
                    metadata=anomaly.metadata
                )
                insights.append(insight)
        
        return insights
    
    def _generate_predictive_insights(self, pattern_data: Dict) -> List[Insight]:
        """Generate predictive insights based on historical patterns."""
        insights = []
        
        # Analyze entity frequency trends for predictions
        trends = pattern_data["behavioral_trends"]
        for trend in trends:
            if trend.trend_type == "entity_frequency" and trend.direction != "stable":
                # Predict future activity based on trend
                if trend.direction == "increasing":
                    prediction = "Continued increase in entity activity expected"
                    recommendations = [
                        "Prepare for higher processing load",
                        "Consider scaling up resources",
                        "Monitor for performance impacts"
                    ]
                else:
                    prediction = "Continued decrease in entity activity expected"
                    recommendations = [
                        "Investigate potential issues or changes",
                        "Consider if this represents a new normal",
                        "Monitor for complete cessation of activity"
                    ]
                
                insight = Insight(
                    insight_type="prediction",
                    title=f"Activity Prediction: {trend.direction.title()} Trend",
                    description=f"Based on current {trend.direction} trend, {prediction.lower()}",
                    confidence=trend.confidence * 0.8,  # Reduce confidence for predictions
                    priority="medium",
                    actionable=True,
                    recommendations=recommendations,
                    related_entities=trend.entities_involved,
                    timestamp=datetime.now(),
                    metadata={
                        "prediction_type": "trend_extrapolation",
                        "base_trend": trend.trend_type,
                        "direction": trend.direction,
                        "magnitude": trend.magnitude
                    }
                )
                insights.append(insight)
        
        return insights
    
    def generate_recommendations(self) -> List[Recommendation]:
        """Generate specific actionable recommendations based on insights."""
        recommendations = []
        
        # Generate recommendations from insights
        for insight in self.insights:
            if insight.actionable:
                for rec_text in insight.recommendations:
                    recommendation = Recommendation(
                        title=f"Action: {rec_text[:50]}...",
                        description=rec_text,
                        action_type=self._determine_action_type(insight),
                        priority=insight.priority,
                        estimated_impact=self._estimate_impact(insight),
                        prerequisites=[],
                        metadata={
                            "insight_id": insight.insight_type,
                            "confidence": insight.confidence,
                            "related_entities": insight.related_entities
                        }
                    )
                    recommendations.append(recommendation)
        
        # Generate system-level recommendations
        recommendations.extend(self._generate_system_recommendations())
        
        self.recommendations = recommendations
        return recommendations
    
    def _determine_action_type(self, insight: Insight) -> str:
        """Determine the appropriate action type for an insight."""
        if insight.priority == "high":
            return "immediate"
        elif insight.insight_type == "anomaly":
            return "immediate"
        elif insight.insight_type == "prediction":
            return "scheduled"
        else:
            return "monitoring"
    
    def _estimate_impact(self, insight: Insight) -> str:
        """Estimate the potential impact of acting on an insight."""
        if insight.priority == "high":
            return "high"
        elif insight.confidence > 0.8:
            return "medium"
        else:
            return "low"
    
    def _generate_system_recommendations(self) -> List[Recommendation]:
        """Generate system-level recommendations."""
        recommendations = []
        
        # Get graph statistics
        stats = self.graph_builder.get_entity_statistics()
        
        # Recommend based on entity distribution
        if stats["total_entities"] > 1000:
            recommendations.append(Recommendation(
                title="Consider Graph Optimization",
                description="Large knowledge graph detected. Consider implementing graph optimization techniques.",
                action_type="scheduled",
                priority="medium",
                estimated_impact="medium",
                prerequisites=[],
                metadata={"trigger": "large_graph", "entity_count": stats["total_entities"]}
            ))
        
        # Recommend based on relationship strength
        if stats["strongest_relationships"]:
            avg_strength = sum(r.strength for r in stats["strongest_relationships"]) / len(stats["strongest_relationships"])
            if avg_strength < 0.3:
                recommendations.append(Recommendation(
                    title="Investigate Weak Relationships",
                    description="Many relationships have low strength. Consider improving relationship detection.",
                    action_type="monitoring",
                    priority="low",
                    estimated_impact="low",
                    prerequisites=[],
                    metadata={"trigger": "weak_relationships", "avg_strength": avg_strength}
                ))
        
        return recommendations
    
    def get_insight_summary(self) -> Dict:
        """Get a summary of all insights and recommendations."""
        return {
            "total_insights": len(self.insights),
            "total_recommendations": len(self.recommendations),
            "insights_by_type": self._group_insights_by_type(),
            "recommendations_by_priority": self._group_recommendations_by_priority(),
            "high_priority_items": [
                insight for insight in self.insights 
                if insight.priority == "high"
            ],
            "immediate_actions": [
                rec for rec in self.recommendations 
                if rec.action_type == "immediate"
            ]
        }
    
    def _group_insights_by_type(self) -> Dict:
        """Group insights by their type."""
        grouped = defaultdict(list)
        for insight in self.insights:
            grouped[insight.insight_type].append(insight)
        return dict(grouped)
    
    def _group_recommendations_by_priority(self) -> Dict:
        """Group recommendations by priority."""
        grouped = defaultdict(list)
        for rec in self.recommendations:
            grouped[rec.priority].append(rec)
        return dict(grouped)
    
    def export_insights(self, format: str = "json") -> str:
        """Export insights in various formats."""
        if format == "json":
            return json.dumps({
                "insights": [
                    {
                        "type": i.insight_type,
                        "title": i.title,
                        "description": i.description,
                        "confidence": i.confidence,
                        "priority": i.priority,
                        "actionable": i.actionable,
                        "recommendations": i.recommendations,
                        "related_entities": i.related_entities,
                        "timestamp": i.timestamp.isoformat(),
                        "metadata": i.metadata
                    }
                    for i in self.insights
                ],
                "recommendations": [
                    {
                        "title": r.title,
                        "description": r.description,
                        "action_type": r.action_type,
                        "priority": r.priority,
                        "estimated_impact": r.estimated_impact,
                        "prerequisites": r.prerequisites,
                        "metadata": r.metadata
                    }
                    for r in self.recommendations
                ],
                "summary": self.get_insight_summary()
            }, indent=2)
        
        elif format == "text":
            output = []
            output.append("KNOWLEDGE GRAPH INSIGHTS")
            output.append("=" * 50)
            
            for insight in self.insights:
                output.append(f"\n{insight.title}")
                output.append(f"Type: {insight.insight_type}")
                output.append(f"Priority: {insight.priority}")
                output.append(f"Confidence: {insight.confidence:.2f}")
                output.append(f"Description: {insight.description}")
                if insight.recommendations:
                    output.append("Recommendations:")
                    for rec in insight.recommendations:
                        output.append(f"  - {rec}")
                output.append("-" * 30)
            
            output.append(f"\nTotal Insights: {len(self.insights)}")
            output.append(f"Total Recommendations: {len(self.recommendations)}")
            
            return "\n".join(output)
        
        else:
            return f"Unsupported format: {format}"
