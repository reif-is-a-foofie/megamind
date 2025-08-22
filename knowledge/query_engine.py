"""
Query Engine - Advanced querying capabilities for the knowledge graph.

Provides sophisticated querying across entities, relationships, and patterns
with complex filters, time-based queries, and relationship traversal.
"""

from typing import Dict, List, Set, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import defaultdict
import json

from .graph_builder import KnowledgeGraphBuilder, Entity, Relationship


@dataclass
class QueryResult:
    """Represents a query result with metadata."""
    entities: List[Entity]
    relationships: List[Relationship]
    total_count: int
    query_time: float
    filters_applied: Dict
    metadata: Dict


class QueryEngine:
    """Advanced query engine for the knowledge graph."""
    
    def __init__(self, graph_builder: KnowledgeGraphBuilder):
        self.graph_builder = graph_builder
        self.entities: List[Entity] = []
        self.relationships: List[Relationship] = []
        self._load_graph()
    
    def _load_graph(self):
        """Load the current knowledge graph."""
        self.entities, self.relationships = self.graph_builder.load_from_memory()
    
    def query_entities(
        self,
        entity_type: Optional[str] = None,
        name_pattern: Optional[str] = None,
        min_confidence: float = 0.0,
        min_frequency: int = 1,
        time_range: Optional[tuple] = None,
        limit: int = 100
    ) -> QueryResult:
        """Query entities with various filters."""
        import time
        start_time = time.time()
        
        filtered_entities = self.entities.copy()
        
        # Apply entity type filter
        if entity_type:
            filtered_entities = [e for e in filtered_entities if e.entity_type == entity_type]
        
        # Apply name pattern filter
        if name_pattern:
            import re
            pattern = re.compile(name_pattern, re.IGNORECASE)
            filtered_entities = [e for e in filtered_entities if pattern.search(e.name)]
        
        # Apply confidence filter
        filtered_entities = [e for e in filtered_entities if e.confidence >= min_confidence]
        
        # Apply frequency filter
        filtered_entities = [e for e in filtered_entities if e.frequency >= min_frequency]
        
        # Apply time range filter
        if time_range:
            start_time_range, end_time_range = time_range
            filtered_entities = [
                e for e in filtered_entities 
                if start_time_range <= e.last_seen <= end_time_range
            ]
        
        # Apply limit
        filtered_entities = filtered_entities[:limit]
        
        query_time = time.time() - start_time
        
        return QueryResult(
            entities=filtered_entities,
            relationships=[],
            total_count=len(filtered_entities),
            query_time=query_time,
            filters_applied={
                "entity_type": entity_type,
                "name_pattern": name_pattern,
                "min_confidence": min_confidence,
                "min_frequency": min_frequency,
                "time_range": time_range,
                "limit": limit
            },
            metadata={"query_type": "entity_query"}
        )
    
    def query_relationships(
        self,
        source_entity: Optional[str] = None,
        target_entity: Optional[str] = None,
        relationship_type: Optional[str] = None,
        min_strength: float = 0.0,
        min_frequency: int = 1,
        time_range: Optional[tuple] = None,
        limit: int = 100
    ) -> QueryResult:
        """Query relationships with various filters."""
        import time
        start_time = time.time()
        
        filtered_relationships = self.relationships.copy()
        
        # Apply source entity filter
        if source_entity:
            filtered_relationships = [r for r in filtered_relationships if r.source_entity == source_entity]
        
        # Apply target entity filter
        if target_entity:
            filtered_relationships = [r for r in filtered_relationships if r.target_entity == target_entity]
        
        # Apply relationship type filter
        if relationship_type:
            filtered_relationships = [r for r in filtered_relationships if r.relationship_type == relationship_type]
        
        # Apply strength filter
        filtered_relationships = [r for r in filtered_relationships if r.strength >= min_strength]
        
        # Apply frequency filter
        filtered_relationships = [r for r in filtered_relationships if r.frequency >= min_frequency]
        
        # Apply time range filter
        if time_range:
            start_time_range, end_time_range = time_range
            filtered_relationships = [
                r for r in filtered_relationships 
                if start_time_range <= r.last_seen <= end_time_range
            ]
        
        # Apply limit
        filtered_relationships = filtered_relationships[:limit]
        
        query_time = time.time() - start_time
        
        return QueryResult(
            entities=[],
            relationships=filtered_relationships,
            total_count=len(filtered_relationships),
            query_time=query_time,
            filters_applied={
                "source_entity": source_entity,
                "target_entity": target_entity,
                "relationship_type": relationship_type,
                "min_strength": min_strength,
                "min_frequency": min_frequency,
                "time_range": time_range,
                "limit": limit
            },
            metadata={"query_type": "relationship_query"}
        )
    
    def find_entity_network(
        self,
        entity_id: str,
        max_depth: int = 2,
        min_strength: float = 0.3
    ) -> QueryResult:
        """Find the network of entities connected to a given entity."""
        import time
        start_time = time.time()
        
        # Find the target entity
        target_entity = next((e for e in self.entities if e.id == entity_id), None)
        if not target_entity:
            return QueryResult([], [], 0, 0, {}, {"error": "Entity not found"})
        
        # Build entity map for quick lookup
        entity_map = {e.id: e for e in self.entities}
        relationship_map = defaultdict(list)
        
        for rel in self.relationships:
            if rel.strength >= min_strength:
                relationship_map[rel.source_entity].append(rel)
                relationship_map[rel.target_entity].append(rel)
        
        # BFS to find connected entities
        visited_entities = {entity_id}
        connected_entities = [target_entity]
        connected_relationships = []
        queue = [(entity_id, 0)]  # (entity_id, depth)
        
        while queue:
            current_entity_id, depth = queue.pop(0)
            
            if depth >= max_depth:
                continue
            
            # Find all relationships for current entity
            for rel in relationship_map[current_entity_id]:
                connected_relationships.append(rel)
                
                # Add connected entities
                for connected_id in [rel.source_entity, rel.target_entity]:
                    if connected_id != current_entity_id and connected_id not in visited_entities:
                        visited_entities.add(connected_id)
                        if connected_id in entity_map:
                            connected_entities.append(entity_map[connected_id])
                            queue.append((connected_id, depth + 1))
        
        query_time = time.time() - start_time
        
        return QueryResult(
            entities=connected_entities,
            relationships=connected_relationships,
            total_count=len(connected_entities),
            query_time=query_time,
            filters_applied={
                "entity_id": entity_id,
                "max_depth": max_depth,
                "min_strength": min_strength
            },
            metadata={"query_type": "network_query"}
        )
    
    def search_by_content(
        self,
        search_text: str,
        entity_types: Optional[List[str]] = None,
        case_sensitive: bool = False
    ) -> QueryResult:
        """Search entities by content/name with text matching."""
        import time
        start_time = time.time()
        
        if not case_sensitive:
            search_text = search_text.lower()
        
        matched_entities = []
        
        for entity in self.entities:
            # Skip if entity type filter is applied
            if entity_types and entity.entity_type not in entity_types:
                continue
            
            # Check if search text matches entity name
            entity_name = entity.name if case_sensitive else entity.name.lower()
            if search_text in entity_name:
                matched_entities.append(entity)
        
        query_time = time.time() - start_time
        
        return QueryResult(
            entities=matched_entities,
            relationships=[],
            total_count=len(matched_entities),
            query_time=query_time,
            filters_applied={
                "search_text": search_text,
                "entity_types": entity_types,
                "case_sensitive": case_sensitive
            },
            metadata={"query_type": "content_search"}
        )
    
    def get_temporal_analysis(
        self,
        entity_id: Optional[str] = None,
        time_window: timedelta = timedelta(days=30)
    ) -> Dict:
        """Get temporal analysis of entity or relationship activity."""
        import time
        start_time = time.time()
        
        now = datetime.now()
        start_time_range = now - time_window
        
        # Filter entities/relationships by time window
        recent_entities = [
            e for e in self.entities 
            if e.last_seen >= start_time_range
        ]
        
        recent_relationships = [
            r for r in self.relationships 
            if r.last_seen >= start_time_range
        ]
        
        # If specific entity is provided, filter to that entity
        if entity_id:
            recent_entities = [e for e in recent_entities if e.id == entity_id]
            recent_relationships = [
                r for r in recent_relationships 
                if r.source_entity == entity_id or r.target_entity == entity_id
            ]
        
        # Group by time periods
        daily_activity = defaultdict(int)
        for entity in recent_entities:
            day = entity.last_seen.date()
            daily_activity[day] += 1
        
        # Calculate trends
        activity_trend = "increasing" if len(recent_entities) > len(self.entities) // 2 else "stable"
        
        query_time = time.time() - start_time
        
        return {
            "time_window": str(time_window),
            "total_entities": len(recent_entities),
            "total_relationships": len(recent_relationships),
            "daily_activity": dict(daily_activity),
            "activity_trend": activity_trend,
            "query_time": query_time,
            "metadata": {"query_type": "temporal_analysis"}
        }
    
    def execute_complex_query(self, query_json: str) -> QueryResult:
        """Execute a complex query defined in JSON format."""
        try:
            query = json.loads(query_json)
            query_type = query.get("type", "entity")
            
            if query_type == "entity":
                return self.query_entities(**query.get("filters", {}))
            elif query_type == "relationship":
                return self.query_relationships(**query.get("filters", {}))
            elif query_type == "network":
                return self.find_entity_network(**query.get("filters", {}))
            elif query_type == "content":
                return self.search_by_content(**query.get("filters", {}))
            else:
                return QueryResult([], [], 0, 0, {}, {"error": f"Unknown query type: {query_type}"})
                
        except Exception as e:
            return QueryResult([], [], 0, 0, {}, {"error": f"Query execution failed: {str(e)}"})
    
    def export_query_results(self, result: QueryResult, format: str = "json") -> str:
        """Export query results in various formats."""
        if format == "json":
            return json.dumps({
                "entities": [
                    {
                        "id": e.id,
                        "name": e.name,
                        "type": e.entity_type,
                        "confidence": e.confidence,
                        "frequency": e.frequency,
                        "first_seen": e.first_seen.isoformat(),
                        "last_seen": e.last_seen.isoformat(),
                        "metadata": e.metadata
                    }
                    for e in result.entities
                ],
                "relationships": [
                    {
                        "id": r.id,
                        "source": r.source_entity,
                        "target": r.target_entity,
                        "type": r.relationship_type,
                        "strength": r.strength,
                        "frequency": r.frequency,
                        "context": r.context,
                        "metadata": r.metadata
                    }
                    for r in result.relationships
                ],
                "metadata": {
                    "total_count": result.total_count,
                    "query_time": result.query_time,
                    "filters_applied": result.filters_applied,
                    "query_metadata": result.metadata
                }
            }, indent=2)
        
        elif format == "csv":
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write entities
            writer.writerow(["Entity ID", "Name", "Type", "Confidence", "Frequency", "First Seen", "Last Seen"])
            for entity in result.entities:
                writer.writerow([
                    entity.id,
                    entity.name,
                    entity.entity_type,
                    entity.confidence,
                    entity.frequency,
                    entity.first_seen.isoformat(),
                    entity.last_seen.isoformat()
                ])
            
            # Write relationships
            writer.writerow([])
            writer.writerow(["Relationship ID", "Source", "Target", "Type", "Strength", "Frequency", "Context"])
            for rel in result.relationships:
                writer.writerow([
                    rel.id,
                    rel.source_entity,
                    rel.target_entity,
                    rel.relationship_type,
                    rel.strength,
                    rel.frequency,
                    rel.context[:100]  # Truncate long context
                ])
            
            return output.getvalue()
        
        else:
            return f"Unsupported format: {format}"
