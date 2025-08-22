"""
Knowledge Graph Builder - Constructs intelligent relationship graphs from memory data.

Builds sophisticated relationship mappings between entities, events, and patterns
from the persistent memory system.
"""

import json
import sqlite3
from typing import Dict, List, Set, Tuple, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import defaultdict
import re


@dataclass
class Entity:
    """Represents an entity in the knowledge graph."""
    id: str
    name: str
    entity_type: str  # person, location, topic, action, etc.
    confidence: float
    first_seen: datetime
    last_seen: datetime
    frequency: int
    metadata: Dict


@dataclass
class Relationship:
    """Represents a relationship between entities."""
    id: str
    source_entity: str
    target_entity: str
    relationship_type: str  # mentions, interacts_with, follows, etc.
    strength: float
    first_seen: datetime
    last_seen: datetime
    frequency: int
    context: str
    metadata: Dict


class KnowledgeGraphBuilder:
    """Builds and maintains the knowledge graph from memory data."""
    
    def __init__(self, memory_db_path: str = "memory/memory.db"):
        self.memory_db_path = memory_db_path
        self.entities: Dict[str, Entity] = {}
        self.relationships: Dict[str, Relationship] = {}
        self.entity_patterns = self._build_entity_patterns()
    
    def _build_entity_patterns(self) -> Dict[str, List[str]]:
        """Build regex patterns for entity extraction."""
        return {
            "email": [
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            ],
            "url": [
                r'https?://[^\s]+',
                r'www\.[^\s]+'
            ],
            "person": [
                r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',  # First Last
                r'\b[A-Z][a-z]+ [A-Z]\. [A-Z][a-z]+\b',  # First M. Last
            ],
            "topic": [
                r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'  # Capitalized phrases
            ],
            "action": [
                r'\b(replied|sent|received|scheduled|completed|deleted)\b',
                r'\b(meeting|call|email|task|reminder)\b'
            ]
        }
    
    def extract_entities(self, text: str, source_type: str, timestamp: datetime) -> List[Entity]:
        """Extract entities from text using pattern matching and NLP techniques."""
        entities = []
        
        # Extract emails
        for pattern in self.entity_patterns["email"]:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entity = Entity(
                    id=f"email_{match.group()}",
                    name=match.group(),
                    entity_type="email",
                    confidence=0.9,
                    first_seen=timestamp,
                    last_seen=timestamp,
                    frequency=1,
                    metadata={"source": source_type, "pattern": pattern}
                )
                entities.append(entity)
        
        # Extract URLs
        for pattern in self.entity_patterns["url"]:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entity = Entity(
                    id=f"url_{hash(match.group())}",
                    name=match.group(),
                    entity_type="url",
                    confidence=0.8,
                    first_seen=timestamp,
                    last_seen=timestamp,
                    frequency=1,
                    metadata={"source": source_type, "pattern": pattern}
                )
                entities.append(entity)
        
        # Extract people (simple name detection)
        for pattern in self.entity_patterns["person"]:
            for match in re.finditer(pattern, text):
                entity = Entity(
                    id=f"person_{hash(match.group())}",
                    name=match.group(),
                    entity_type="person",
                    confidence=0.7,
                    first_seen=timestamp,
                    last_seen=timestamp,
                    frequency=1,
                    metadata={"source": source_type, "pattern": pattern}
                )
                entities.append(entity)
        
        # Extract topics (capitalized phrases)
        for pattern in self.entity_patterns["topic"]:
            for match in re.finditer(pattern, text):
                if len(match.group().split()) >= 2:  # At least 2 words
                    entity = Entity(
                        id=f"topic_{hash(match.group())}",
                        name=match.group(),
                        entity_type="topic",
                        confidence=0.6,
                        first_seen=timestamp,
                        last_seen=timestamp,
                        frequency=1,
                        metadata={"source": source_type, "pattern": pattern}
                    )
                    entities.append(entity)
        
        return entities
    
    def build_relationships(self, entities: List[Entity], context: str, timestamp: datetime) -> List[Relationship]:
        """Build relationships between entities based on co-occurrence and context."""
        relationships = []
        
        # Create co-occurrence relationships
        for i, entity1 in enumerate(entities):
            for entity2 in entities[i+1:]:
                if entity1.id != entity2.id:
                    # Determine relationship type based on entity types
                    rel_type = self._determine_relationship_type(entity1, entity2, context)
                    
                    relationship = Relationship(
                        id=f"rel_{hash(f'{entity1.id}_{entity2.id}_{rel_type}')}",
                        source_entity=entity1.id,
                        target_entity=entity2.id,
                        relationship_type=rel_type,
                        strength=0.5,  # Base strength
                        first_seen=timestamp,
                        last_seen=timestamp,
                        frequency=1,
                        context=context,
                        metadata={"source": "co_occurrence"}
                    )
                    relationships.append(relationship)
        
        return relationships
    
    def _determine_relationship_type(self, entity1: Entity, entity2: Entity, context: str) -> str:
        """Determine the type of relationship between two entities."""
        if entity1.entity_type == "person" and entity2.entity_type == "email":
            return "has_email"
        elif entity1.entity_type == "person" and entity2.entity_type == "topic":
            return "interested_in"
        elif entity1.entity_type == "email" and entity2.entity_type == "url":
            return "contains_link"
        elif entity1.entity_type == "action" and entity2.entity_type == "person":
            return "performed_by"
        else:
            return "related_to"
    
    def load_from_memory(self) -> Tuple[List[Entity], List[Relationship]]:
        """Load and build knowledge graph from memory database."""
        try:
            conn = sqlite3.connect(self.memory_db_path)
            cursor = conn.cursor()
            
            # Get all memory entries
            cursor.execute("""
                SELECT id, content, source_type, timestamp, metadata
                FROM memory_entries
                ORDER BY timestamp
            """)
            
            all_entities = []
            all_relationships = []
            
            for row in cursor.fetchall():
                entry_id, content, source_type, timestamp_str, metadata_str = row
                timestamp = datetime.fromisoformat(timestamp_str)
                metadata = json.loads(metadata_str) if metadata_str else {}
                
                # Extract entities from content
                entities = self.extract_entities(content, source_type, timestamp)
                all_entities.extend(entities)
                
                # Build relationships
                relationships = self.build_relationships(entities, content, timestamp)
                all_relationships.extend(relationships)
            
            # Merge duplicate entities and update frequencies
            merged_entities = self._merge_entities(all_entities)
            merged_relationships = self._merge_relationships(all_relationships)
            
            conn.close()
            return merged_entities, merged_relationships
            
        except Exception as e:
            print(f"Error loading from memory: {e}")
            return [], []
    
    def _merge_entities(self, entities: List[Entity]) -> List[Entity]:
        """Merge duplicate entities and update frequencies."""
        entity_map = {}
        
        for entity in entities:
            if entity.id in entity_map:
                # Update existing entity
                existing = entity_map[entity.id]
                existing.frequency += entity.frequency
                existing.last_seen = max(existing.last_seen, entity.last_seen)
                existing.confidence = max(existing.confidence, entity.confidence)
            else:
                entity_map[entity.id] = entity
        
        return list(entity_map.values())
    
    def _merge_relationships(self, relationships: List[Relationship]) -> List[Relationship]:
        """Merge duplicate relationships and update frequencies."""
        rel_map = {}
        
        for rel in relationships:
            key = f"{rel.source_entity}_{rel.target_entity}_{rel.relationship_type}"
            if key in rel_map:
                # Update existing relationship
                existing = rel_map[key]
                existing.frequency += rel.frequency
                existing.last_seen = max(existing.last_seen, rel.last_seen)
                existing.strength = min(1.0, existing.strength + 0.1)  # Strengthen with frequency
            else:
                rel_map[key] = rel
        
        return list(rel_map.values())
    
    def get_entity_graph(self) -> Dict:
        """Get the complete entity graph for visualization."""
        entities, relationships = self.load_from_memory()
        
        return {
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
                for e in entities
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
                for r in relationships
            ]
        }
    
    def get_entity_statistics(self) -> Dict:
        """Get statistics about the knowledge graph."""
        entities, relationships = self.load_from_memory()
        
        entity_types = defaultdict(int)
        relationship_types = defaultdict(int)
        
        for entity in entities:
            entity_types[entity.entity_type] += 1
        
        for rel in relationships:
            relationship_types[rel.relationship_type] += 1
        
        return {
            "total_entities": len(entities),
            "total_relationships": len(relationships),
            "entity_types": dict(entity_types),
            "relationship_types": dict(relationship_types),
            "most_frequent_entities": sorted(
                entities, 
                key=lambda x: x.frequency, 
                reverse=True
            )[:10],
            "strongest_relationships": sorted(
                relationships,
                key=lambda x: x.strength,
                reverse=True
            )[:10]
        }
