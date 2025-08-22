"""
Test script for Advanced Knowledge Graph System.

Validates the knowledge graph functionality and demonstrates
relationship mapping, pattern analysis, and insight generation.
"""

import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from knowledge.graph_builder import KnowledgeGraphBuilder
from knowledge.query_engine import QueryEngine
from knowledge.pattern_analyzer import PatternAnalyzer
from knowledge.insight_generator import InsightGenerator


def test_graph_builder():
    """Test knowledge graph builder functionality."""
    print("Testing Knowledge Graph Builder...")
    
    builder = KnowledgeGraphBuilder()
    
    # Test entity extraction
    test_text = "John Smith sent an email to jane@example.com about Project Alpha. Visit https://example.com for details."
    entities = builder.extract_entities(test_text, "email", datetime.now())
    
    assert len(entities) > 0, "Should extract entities from text"
    
    # Test relationship building
    relationships = builder.build_relationships(entities, test_text, datetime.now())
    assert len(relationships) > 0, "Should build relationships between entities"
    
    # Test entity graph generation
    graph = builder.get_entity_graph()
    assert "entities" in graph, "Should return entity graph structure"
    assert "relationships" in graph, "Should return relationship structure"
    
    # Test statistics
    stats = builder.get_entity_statistics()
    assert "total_entities" in stats, "Should return entity statistics"
    assert "total_relationships" in stats, "Should return relationship statistics"
    
    print("✓ Knowledge Graph Builder validated")


def test_query_engine():
    """Test query engine functionality."""
    print("Testing Query Engine...")
    
    builder = KnowledgeGraphBuilder()
    engine = QueryEngine(builder)
    
    # Test entity querying
    result = engine.query_entities(entity_type="email", limit=10)
    assert hasattr(result, 'entities'), "Should return query result with entities"
    assert hasattr(result, 'total_count'), "Should return total count"
    
    # Test relationship querying
    result = engine.query_relationships(limit=10)
    assert hasattr(result, 'relationships'), "Should return query result with relationships"
    
    # Test content search
    result = engine.search_by_content("email", entity_types=["email"])
    assert hasattr(result, 'entities'), "Should return search results"
    
    # Test temporal analysis
    analysis = engine.get_temporal_analysis()
    assert "total_entities" in analysis, "Should return temporal analysis"
    assert "activity_trend" in analysis, "Should return activity trend"
    
    print("✓ Query Engine validated")


def test_pattern_analyzer():
    """Test pattern analyzer functionality."""
    print("Testing Pattern Analyzer...")
    
    builder = KnowledgeGraphBuilder()
    analyzer = PatternAnalyzer(builder)
    
    # Test temporal patterns
    patterns = analyzer.find_temporal_patterns()
    assert isinstance(patterns, list), "Should return list of patterns"
    
    # Test relationship clusters
    clusters = analyzer.find_relationship_clusters()
    assert isinstance(clusters, list), "Should return list of clusters"
    
    # Test behavioral trends
    trends = analyzer.analyze_behavioral_trends()
    assert isinstance(trends, list), "Should return list of trends"
    
    # Test anomalies
    anomalies = analyzer.find_anomalies()
    assert isinstance(anomalies, list), "Should return list of anomalies"
    
    # Test comprehensive insights
    insights = analyzer.generate_insights()
    assert "temporal_patterns" in insights, "Should return temporal patterns"
    assert "relationship_clusters" in insights, "Should return relationship clusters"
    assert "behavioral_trends" in insights, "Should return behavioral trends"
    assert "anomalies" in insights, "Should return anomalies"
    assert "statistics" in insights, "Should return statistics"
    
    print("✓ Pattern Analyzer validated")


def test_insight_generator():
    """Test insight generator functionality."""
    print("Testing Insight Generator...")
    
    builder = KnowledgeGraphBuilder()
    analyzer = PatternAnalyzer(builder)
    generator = InsightGenerator(builder, analyzer)
    
    # Test insight generation
    insights = generator.generate_insights()
    assert isinstance(insights, list), "Should return list of insights"
    
    # Test recommendation generation
    recommendations = generator.generate_recommendations()
    assert isinstance(recommendations, list), "Should return list of recommendations"
    
    # Test insight summary
    summary = generator.get_insight_summary()
    assert "total_insights" in summary, "Should return insight summary"
    assert "total_recommendations" in summary, "Should return recommendation summary"
    
    # Test export functionality
    export = generator.export_insights(format="json")
    assert isinstance(export, str), "Should export insights as JSON"
    
    print("✓ Insight Generator validated")


def test_integration():
    """Test integration between all components."""
    print("Testing System Integration...")
    
    # Create all components
    builder = KnowledgeGraphBuilder()
    engine = QueryEngine(builder)
    analyzer = PatternAnalyzer(builder)
    generator = InsightGenerator(builder, analyzer)
    
    # Test end-to-end workflow
    # 1. Build graph
    entities, relationships = builder.load_from_memory()
    
    # 2. Query graph
    query_result = engine.query_entities(limit=5)
    
    # 3. Analyze patterns
    insights = analyzer.generate_insights()
    
    # 4. Generate recommendations
    recommendations = generator.generate_recommendations()
    
    # Verify all components work together
    assert isinstance(entities, list), "Should load entities from memory"
    assert isinstance(relationships, list), "Should load relationships from memory"
    assert hasattr(query_result, 'entities'), "Should return query results"
    assert isinstance(insights, dict), "Should return insights"
    assert isinstance(recommendations, list), "Should return recommendations"
    
    print("✓ System Integration validated")


def main():
    """Run all knowledge graph tests."""
    print("🧪 Testing Advanced Knowledge Graph System...\n")
    
    try:
        test_graph_builder()
        test_query_engine()
        test_pattern_analyzer()
        test_insight_generator()
        test_integration()
        
        print("\n🎉 All knowledge graph tests passed!")
        print("✅ Advanced Knowledge Graph System is ready for mission.")
        
    except Exception as e:
        print(f"\n❌ Knowledge graph test failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
