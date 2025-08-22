"""
Pattern Analyzer - Identifies patterns and trends in knowledge graph data.

Analyzes temporal patterns, relationship clusters, and behavioral trends
to provide insights and predictive capabilities.
"""

from typing import Dict, List, Set, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import defaultdict, Counter
import json
import math

from .graph_builder import KnowledgeGraphBuilder, Entity, Relationship


@dataclass
class Pattern:
    """Represents a discovered pattern."""
    pattern_type: str
    confidence: float
    frequency: int
    entities: List[str]
    relationships: List[str]
    time_range: Tuple[datetime, datetime]
    description: str
    metadata: Dict


@dataclass
class Trend:
    """Represents a trend analysis result."""
    trend_type: str
    direction: str  # increasing, decreasing, stable
    magnitude: float
    time_period: str
    entities_involved: List[str]
    confidence: float
    description: str


class PatternAnalyzer:
    """Analyzes patterns and trends in the knowledge graph."""
    
    def __init__(self, graph_builder: KnowledgeGraphBuilder):
        self.graph_builder = graph_builder
        self.entities: List[Entity] = []
        self.relationships: List[Relationship] = []
        self._load_graph()
    
    def _load_graph(self):
        """Load the current knowledge graph."""
        self.entities, self.relationships = self.graph_builder.load_from_memory()
    
    def find_temporal_patterns(
        self,
        time_window: timedelta = timedelta(days=30),
        min_frequency: int = 3
    ) -> List[Pattern]:
        """Find temporal patterns in entity and relationship activity."""
        patterns = []
        now = datetime.now()
        start_time = now - time_window
        
        # Group entities by time periods
        daily_entities = defaultdict(list)
        for entity in self.entities:
            if entity.last_seen >= start_time:
                day = entity.last_seen.date()
                daily_entities[day].append(entity)
        
        # Find daily patterns
        for day, day_entities in daily_entities.items():
            if len(day_entities) >= min_frequency:
                # Analyze entity types for this day
                entity_types = Counter([e.entity_type for e in day_entities])
                most_common_type = entity_types.most_common(1)[0]
                
                if most_common_type[1] >= min_frequency:
                    pattern = Pattern(
                        pattern_type="daily_entity_type",
                        confidence=min(1.0, most_common_type[1] / len(day_entities)),
                        frequency=most_common_type[1],
                        entities=[e.id for e in day_entities if e.entity_type == most_common_type[0]],
                        relationships=[],
                        time_range=(datetime.combine(day, datetime.min.time()), 
                                  datetime.combine(day, datetime.max.time())),
                        description=f"High frequency of {most_common_type[0]} entities on {day}",
                        metadata={"entity_type": most_common_type[0], "day": str(day)}
                    )
                    patterns.append(pattern)
        
        return patterns
    
    def find_relationship_clusters(
        self,
        min_cluster_size: int = 3,
        min_strength: float = 0.5
    ) -> List[Pattern]:
        """Find clusters of strongly connected entities."""
        patterns = []
        
        # Build adjacency matrix for relationships
        adjacency = defaultdict(set)
        for rel in self.relationships:
            if rel.strength >= min_strength:
                adjacency[rel.source_entity].add(rel.target_entity)
                adjacency[rel.target_entity].add(rel.source_entity)
        
        # Find connected components (clusters)
        visited = set()
        
        for entity_id in adjacency:
            if entity_id not in visited:
                cluster = self._find_connected_component(entity_id, adjacency, visited)
                
                if len(cluster) >= min_cluster_size:
                    # Calculate cluster metrics
                    cluster_entities = [e for e in self.entities if e.id in cluster]
                    cluster_relationships = [
                        r for r in self.relationships 
                        if r.source_entity in cluster and r.target_entity in cluster
                    ]
                    
                    avg_strength = sum(r.strength for r in cluster_relationships) / len(cluster_relationships) if cluster_relationships else 0
                    
                    pattern = Pattern(
                        pattern_type="relationship_cluster",
                        confidence=avg_strength,
                        frequency=len(cluster_relationships),
                        entities=list(cluster),
                        relationships=[r.id for r in cluster_relationships],
                        time_range=(
                            min(e.first_seen for e in cluster_entities),
                            max(e.last_seen for e in cluster_entities)
                        ),
                        description=f"Cluster of {len(cluster)} strongly connected entities",
                        metadata={
                            "cluster_size": len(cluster),
                            "avg_strength": avg_strength,
                            "entity_types": Counter([e.entity_type for e in cluster_entities])
                        }
                    )
                    patterns.append(pattern)
        
        return patterns
    
    def _find_connected_component(self, start_id: str, adjacency: Dict, visited: Set) -> Set:
        """Find all entities connected to start_id using DFS."""
        component = set()
        stack = [start_id]
        
        while stack:
            current_id = stack.pop()
            if current_id not in visited:
                visited.add(current_id)
                component.add(current_id)
                
                for neighbor_id in adjacency.get(current_id, set()):
                    if neighbor_id not in visited:
                        stack.append(neighbor_id)
        
        return component
    
    def analyze_behavioral_trends(
        self,
        time_window: timedelta = timedelta(days=7)
    ) -> List[Trend]:
        """Analyze behavioral trends over time."""
        trends = []
        now = datetime.now()
        start_time = now - time_window
        
        # Analyze entity frequency trends
        recent_entities = [e for e in self.entities if e.last_seen >= start_time]
        older_entities = [e for e in self.entities if e.last_seen < start_time]
        
        if recent_entities and older_entities:
            recent_freq = len(recent_entities) / time_window.days
            older_freq = len(older_entities) / (now - min(e.last_seen for e in older_entities)).days
            
            if recent_freq > older_freq * 1.2:
                direction = "increasing"
                magnitude = (recent_freq - older_freq) / older_freq
            elif recent_freq < older_freq * 0.8:
                direction = "decreasing"
                magnitude = (older_freq - recent_freq) / older_freq
            else:
                direction = "stable"
                magnitude = 0.0
            
            trend = Trend(
                trend_type="entity_frequency",
                direction=direction,
                magnitude=magnitude,
                time_period=str(time_window),
                entities_involved=[e.id for e in recent_entities],
                confidence=min(1.0, abs(magnitude)),
                description=f"Entity frequency is {direction} by {magnitude:.1%}"
            )
            trends.append(trend)
        
        # Analyze relationship strength trends
        recent_relationships = [r for r in self.relationships if r.last_seen >= start_time]
        if recent_relationships:
            avg_recent_strength = sum(r.strength for r in recent_relationships) / len(recent_relationships)
            avg_overall_strength = sum(r.strength for r in self.relationships) / len(self.relationships)
            
            if avg_recent_strength > avg_overall_strength * 1.1:
                direction = "increasing"
                magnitude = (avg_recent_strength - avg_overall_strength) / avg_overall_strength
            elif avg_recent_strength < avg_overall_strength * 0.9:
                direction = "decreasing"
                magnitude = (avg_overall_strength - avg_recent_strength) / avg_overall_strength
            else:
                direction = "stable"
                magnitude = 0.0
            
            trend = Trend(
                trend_type="relationship_strength",
                direction=direction,
                magnitude=magnitude,
                time_period=str(time_window),
                entities_involved=list(set([r.source_entity for r in recent_relationships] + 
                                         [r.target_entity for r in recent_relationships])),
                confidence=min(1.0, abs(magnitude)),
                description=f"Relationship strength is {direction} by {magnitude:.1%}"
            )
            trends.append(trend)
        
        return trends
    
    def find_anomalies(
        self,
        time_window: timedelta = timedelta(days=1),
        threshold: float = 2.0
    ) -> List[Pattern]:
        """Find anomalous patterns in the knowledge graph."""
        anomalies = []
        now = datetime.now()
        start_time = now - time_window
        
        # Find unusual entity frequency
        recent_entities = [e for e in self.entities if e.last_seen >= start_time]
        entity_types = Counter([e.entity_type for e in recent_entities])
        
        # Calculate expected frequency based on historical data
        all_entity_types = Counter([e.entity_type for e in self.entities])
        total_entities = len(self.entities)
        
        for entity_type, recent_count in entity_types.items():
            expected_fraction = all_entity_types[entity_type] / total_entities if total_entities > 0 else 0
            expected_count = expected_fraction * len(recent_entities)
            
            if expected_count > 0:
                z_score = abs(recent_count - expected_count) / math.sqrt(expected_count)
                
                if z_score > threshold:
                    anomaly = Pattern(
                        pattern_type="frequency_anomaly",
                        confidence=min(1.0, z_score / threshold),
                        frequency=recent_count,
                        entities=[e.id for e in recent_entities if e.entity_type == entity_type],
                        relationships=[],
                        time_range=(start_time, now),
                        description=f"Unusual frequency of {entity_type} entities (z-score: {z_score:.2f})",
                        metadata={
                            "entity_type": entity_type,
                            "observed": recent_count,
                            "expected": expected_count,
                            "z_score": z_score
                        }
                    )
                    anomalies.append(anomaly)
        
        return anomalies
    
    def generate_insights(self) -> Dict:
        """Generate comprehensive insights from pattern analysis."""
        insights = {
            "temporal_patterns": self.find_temporal_patterns(),
            "relationship_clusters": self.find_relationship_clusters(),
            "behavioral_trends": self.analyze_behavioral_trends(),
            "anomalies": self.find_anomalies(),
            "statistics": self._generate_statistics()
        }
        
        return insights
    
    def _generate_statistics(self) -> Dict:
        """Generate statistical summary of the knowledge graph."""
        entity_types = Counter([e.entity_type for e in self.entities])
        relationship_types = Counter([r.relationship_type for r in self.relationships])
        
        # Calculate average confidence and frequency
        avg_confidence = sum(e.confidence for e in self.entities) / len(self.entities) if self.entities else 0
        avg_frequency = sum(e.frequency for e in self.entities) / len(self.entities) if self.entities else 0
        avg_strength = sum(r.strength for r in self.relationships) / len(self.relationships) if self.relationships else 0
        
        return {
            "total_entities": len(self.entities),
            "total_relationships": len(self.relationships),
            "entity_type_distribution": dict(entity_types),
            "relationship_type_distribution": dict(relationship_types),
            "avg_entity_confidence": avg_confidence,
            "avg_entity_frequency": avg_frequency,
            "avg_relationship_strength": avg_strength,
            "most_frequent_entities": sorted(
                self.entities, 
                key=lambda x: x.frequency, 
                reverse=True
            )[:5],
            "strongest_relationships": sorted(
                self.relationships,
                key=lambda x: x.strength,
                reverse=True
            )[:5]
        }
    
    def export_patterns(self, patterns: List[Pattern], format: str = "json") -> str:
        """Export patterns in various formats."""
        if format == "json":
            return json.dumps([
                {
                    "pattern_type": p.pattern_type,
                    "confidence": p.confidence,
                    "frequency": p.frequency,
                    "entities": p.entities,
                    "relationships": p.relationships,
                    "time_range": [p.time_range[0].isoformat(), p.time_range[1].isoformat()],
                    "description": p.description,
                    "metadata": p.metadata
                }
                for p in patterns
            ], indent=2)
        
        elif format == "text":
            output = []
            for pattern in patterns:
                output.append(f"Pattern: {pattern.pattern_type}")
                output.append(f"Confidence: {pattern.confidence:.2f}")
                output.append(f"Frequency: {pattern.frequency}")
                output.append(f"Description: {pattern.description}")
                output.append(f"Time Range: {pattern.time_range[0]} to {pattern.time_range[1]}")
                output.append(f"Entities: {', '.join(pattern.entities[:5])}{'...' if len(pattern.entities) > 5 else ''}")
                output.append("-" * 50)
            
            return "\n".join(output)
        
        else:
            return f"Unsupported format: {format}"
