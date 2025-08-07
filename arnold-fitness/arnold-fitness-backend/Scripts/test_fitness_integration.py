#!/usr/bin/env python3
"""
Integration test for the fitness knowledge system.
This tests the QueryGenerator, TaskGuidance and Fitness Retriever working together.
Since Qdrant is inaccessible, we'll test the knowledge loading and mock retrieval.
"""

import os
import sys
import json
from pathlib import Path

# Setup path like arnold_main_local.py
current_dir = Path(__file__).parent
backend_dir = current_dir.parent
sys.path.insert(0, str(backend_dir))

# Load environment
from dotenv import load_dotenv
load_dotenv()

# Import our components
from src.llm_interfaces.query_generator_llm.query_generator_llm import QueryGeneratorLLM
from src.llm_interfaces.task_guidance_llm.task_guidance_llm import TaskGuidanceLLM

def setup_environment():
    """Load environment variables from .env file."""
    env_path = backend_dir / '.env'
    
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value.strip().strip('"').strip("'")

def load_sample_fitness_knowledge():
    """Load sample fitness knowledge for testing."""
    knowledge_dir = backend_dir / "data" / "fitness_knowledge"
    sample_docs = []
    
    # Load a few sample documents from each category
    for category_dir in knowledge_dir.iterdir():
        if not category_dir.is_dir():
            continue
            
        for json_file in list(category_dir.glob("*.json"))[:1]:  # Just first file from each category
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                
                for item in content[:2]:  # Just first 2 items from each file
                    sample_docs.append({
                        "question": item["question"],
                        "answer": item["answer"],
                        "metadata": item["metadata"]
                    })
            except Exception as e:
                print(f"Error loading {json_file}: {e}")
    
    return sample_docs

def mock_fitness_retrieval(query: str, sample_docs: list, limit: int = 3) -> list:
    """Mock fitness knowledge retrieval based on keyword matching."""
    # Simple keyword-based matching for testing
    query_lower = query.lower()
    query_words = set(query_lower.split())
    
    results = []
    
    for doc in sample_docs:
        # Score based on keyword matches
        text = (doc["question"] + " " + doc["answer"]).lower()
        tags = doc["metadata"].get("tags", [])
        tag_text = " ".join(tags).lower()
        
        matches = sum(1 for word in query_words if word in text or word in tag_text)
        
        if matches > 0:
            results.append({
                "score": matches / len(query_words),
                "payload": {
                    "question": doc["question"],
                    "answer": doc["answer"],
                    "category": doc["metadata"].get("category", ""),
                    "tags": tags
                }
            })
    
    # Sort by score and return top results
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:limit]

def test_fitness_integration():
    """Test integration of fitness components."""
    print("=== Arnold Fitness Integration Test ===\\n")
    
    setup_environment()
    
    # Load sample knowledge
    print("Loading sample fitness knowledge...")
    sample_docs = load_sample_fitness_knowledge()
    print(f"Loaded {len(sample_docs)} sample documents\\n")
    
    # Initialize LLMs
    print("Initializing LLM components...")
    query_generator = QueryGeneratorLLM()
    task_guidance = TaskGuidanceLLM()
    print("LLM components initialized\\n")
    
    # Test scenarios
    test_scenarios = [
        {
            "user_input": "Help me lose 10kg in a healthy way",
            "context": {"fitness_goal": "weight_loss", "current_weight": 80, "target_weight": 70}
        },
        {
            "user_input": "I want to build muscle, what should my protein intake be?",
            "context": {"fitness_goal": "muscle_gain", "current_weight": 75, "activity_level": "moderate"}
        },
        {
            "user_input": "I'm not losing weight despite being in a caloric deficit",
            "context": {"fitness_goal": "weight_loss", "current_issue": "plateau", "deficit_duration": "4_weeks"}
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"--- Test Scenario {i}: {scenario['user_input'][:50]}... ---")
        
        try:
            # 1. Generate search query
            print("\\n1. Query Generation:")
            query = query_generator.generate_search_query(
                scenario["user_input"],
                scenario["context"]
            )
            print(f"Generated query: '{query}'")
            
            # 2. Mock retrieval
            print("\\n2. Knowledge Retrieval (Mock):")
            retrieved_docs = mock_fitness_retrieval(query, sample_docs)
            print(f"Retrieved {len(retrieved_docs)} relevant documents")
            for j, doc in enumerate(retrieved_docs):
                print(f"   {j+1}. [{doc['payload']['category']}] {doc['payload']['question'][:60]}...")
            
            # 3. Generate task guidance
            print("\\n3. Task Guidance Generation:")
            if retrieved_docs:
                knowledge_context = "\\n".join([
                    f"Q: {doc['payload']['question']}\\nA: {doc['payload']['answer']}"
                    for doc in retrieved_docs
                ])
            else:
                knowledge_context = "No specific knowledge retrieved for this query."
            
            guidance = task_guidance.generate_guidance(
                scenario["user_input"],
                scenario["context"],
                knowledge_context
            )
            print("Generated guidance:")
            print(guidance[:300] + "..." if len(guidance) > 300 else guidance)
            
        except Exception as e:
            print(f"Error in scenario {i}: {e}")
        
        print("\\n" + "="*80 + "\\n")
    
    print("Integration test completed!")

if __name__ == "__main__":
    test_fitness_integration()