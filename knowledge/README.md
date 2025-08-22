# Advanced Knowledge Graph System

Intelligent relationship mapping and pattern recognition for the persistent memory system.

## Overview

The Advanced Knowledge Graph System extends the memory infrastructure with sophisticated entity extraction, relationship mapping, pattern analysis, and predictive insights. It transforms raw memory data into actionable intelligence.

## Architecture

### Core Components

1. **KnowledgeGraphBuilder** (`graph_builder.py`)
   - Entity extraction using pattern matching and NLP techniques
   - Relationship mapping based on co-occurrence and context
   - Graph construction with confidence scoring
   - Memory integration and data persistence

2. **QueryEngine** (`query_engine.py`)
   - Complex entity and relationship queries
   - Time-based filtering and analysis
   - Network traversal and clustering
   - Content search and temporal analysis
   - Export capabilities (JSON, CSV)

3. **PatternAnalyzer** (`pattern_analyzer.py`)
   - Temporal pattern detection
   - Relationship cluster analysis
   - Behavioral trend identification
   - Anomaly detection with statistical analysis
   - Pattern export and visualization

4. **InsightGenerator** (`insight_generator.py`)
   - Actionable insight generation
   - Predictive analysis and recommendations
   - Priority-based action suggestions
   - System-level optimization recommendations

## Features

### Entity Extraction
- **Email Detection**: Regex-based email address extraction
- **URL Recognition**: Web link and domain identification
- **Person Names**: First/Last name pattern matching
- **Topic Identification**: Capitalized phrase detection
- **Action Recognition**: Verb and action word identification

### Relationship Mapping
- **Co-occurrence Analysis**: Entities appearing together
- **Context-Based Relationships**: Type-specific relationship detection
- **Strength Scoring**: Relationship confidence calculation
- **Temporal Tracking**: Relationship evolution over time

### Advanced Querying
- **Entity Queries**: Filter by type, confidence, frequency
- **Relationship Queries**: Source, target, type filtering
- **Network Analysis**: Entity connectivity and clustering
- **Temporal Analysis**: Time-based pattern recognition
- **Content Search**: Text-based entity discovery

### Pattern Recognition
- **Daily Patterns**: Activity concentration analysis
- **Relationship Clusters**: Strongly connected entity groups
- **Behavioral Trends**: Activity direction and magnitude
- **Anomaly Detection**: Statistical outlier identification

### Insight Generation
- **Actionable Insights**: Priority-ranked recommendations
- **Predictive Analysis**: Trend-based future predictions
- **System Optimization**: Performance and efficiency suggestions
- **Export Capabilities**: JSON and text format support

## Usage

### Basic Entity Extraction

```python
from knowledge import KnowledgeGraphBuilder

builder = KnowledgeGraphBuilder()

# Extract entities from text
text = "John Smith sent an email to jane@example.com about Project Alpha"
entities = builder.extract_entities(text, "email", datetime.now())

# Build relationships
relationships = builder.build_relationships(entities, text, datetime.now())

# Get complete graph
graph = builder.get_entity_graph()
```

### Advanced Querying

```python
from knowledge import QueryEngine

engine = QueryEngine(builder)

# Query entities by type
result = engine.query_entities(
    entity_type="person",
    min_confidence=0.7,
    limit=10
)

# Find entity network
network = engine.find_entity_network(
    entity_id="person_123",
    max_depth=2,
    min_strength=0.5
)

# Temporal analysis
analysis = engine.get_temporal_analysis(
    entity_id="person_123",
    time_window=timedelta(days=30)
)
```

### Pattern Analysis

```python
from knowledge import PatternAnalyzer

analyzer = PatternAnalyzer(builder)

# Find temporal patterns
patterns = analyzer.find_temporal_patterns(
    time_window=timedelta(days=30),
    min_frequency=3
)

# Analyze behavioral trends
trends = analyzer.analyze_behavioral_trends(
    time_window=timedelta(days=7)
)

# Detect anomalies
anomalies = analyzer.find_anomalies(
    time_window=timedelta(days=1),
    threshold=2.0
)
```

### Insight Generation

```python
from knowledge import InsightGenerator

generator = InsightGenerator(builder, analyzer)

# Generate insights
insights = generator.generate_insights()

# Get recommendations
recommendations = generator.generate_recommendations()

# Export insights
export = generator.export_insights(format="json")
```

## Integration

### Memory System Integration
- Automatically loads from memory database
- Extracts entities from all memory entries
- Builds relationships across time and sources
- Persists graph data for analysis

### UI Integration
- Graph visualization support
- Interactive query interface
- Real-time pattern updates
- Insight dashboard integration

### External Systems
- Export capabilities for external tools
- API endpoints for graph queries
- Webhook support for real-time updates
- Integration with analytics platforms

## Performance

### Optimization Features
- **Caching**: Frequently accessed data caching
- **Indexing**: Database indexing for fast queries
- **Batch Processing**: Efficient bulk operations
- **Memory Management**: Optimized memory usage

### Scalability
- **Modular Design**: Component-based architecture
- **Database Integration**: SQLite with future scaling
- **Async Support**: Non-blocking operations
- **Resource Management**: Efficient resource utilization

## Testing

Run comprehensive tests:

```bash
python3 knowledge/test_knowledge_system.py
```

Tests validate:
- ✅ Entity extraction accuracy
- ✅ Relationship mapping correctness
- ✅ Query performance and accuracy
- ✅ Pattern detection reliability
- ✅ Insight generation quality
- ✅ System integration stability

## Configuration

### Entity Patterns
Customize entity extraction patterns in `graph_builder.py`:

```python
entity_patterns = {
    "email": [r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'],
    "url": [r'https?://[^\s]+', r'www\.[^\s]+'],
    "person": [r'\b[A-Z][a-z]+ [A-Z][a-z]+\b'],
    # Add custom patterns...
}
```

### Query Parameters
Adjust query performance and accuracy:

```python
# Query engine settings
min_confidence = 0.6
max_depth = 3
time_window = timedelta(days=30)
```

## Mission Integration

This knowledge graph system provides:
- **Intelligence Layer**: Advanced pattern recognition
- **Predictive Capabilities**: Future trend analysis
- **Actionable Insights**: Priority-based recommendations
- **Semantic Understanding**: Relationship-based knowledge
- **Scalable Architecture**: Foundation for advanced AI features

The system transforms raw data into intelligent insights, enabling the galleon to navigate with wisdom and foresight! 🧠⚡
