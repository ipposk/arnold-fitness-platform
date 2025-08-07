# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Arnold is a cloud-native RAG (Retrieval Augmented Generation) platform for fitness coaching and nutrition guidance. Originally evolved from Penelope (a penetration testing platform), it maintains the same robust architecture while focusing on personalized fitness and wellness coaching using AI-driven guidance.

## Key Commands

### Backend Development
```bash
cd arnold-fitness/arnold-fitness-backend

# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies for serverless framework
npm install

# Local development with mocked AWS services (modern interface)
python arnold_cli_modern.py

# Local development (legacy interface for debugging)
python arnold_main_local.py

# Deploy to AWS (requires proper AWS credentials and environment variables)
serverless deploy

# Run individual scripts
python Scripts/test_embedding.py
python Scripts/verify_qdrant.py
python Scripts/compare_retrieval.py
python Scripts/create_demo_sessions.py
python Scripts/load_fitness_knowledge.py
```

### Environment Setup
Required environment variables (create `.env` file in `arnold-fitness/arnold-fitness-backend/`):
```
GEMINI_API_KEY=your_gemini_api_key
QDRANT_URL=your_qdrant_cloud_url
QDRANT_API_KEY=your_qdrant_api_key
QDRANT_COLLECTION=arnold_fitness_chunks
```

### Testing
No specific test framework is configured. Use the local development environment (`arnold_main_local.py`) for testing backend components.

## Architecture

### High-Level Structure
The project consists of two main parts:
- **Backend**: AWS Lambda-based serverless backend (`arnold-fitness/arnold-fitness-backend/`)
- **Frontend**: React-based UI (currently not implemented, but infrastructure exists for future development)

### Backend Architecture

#### Core Components
1. **Orchestrator** (`src/orchestrator/orchestrator.py`): Main workflow coordination
2. **LLM Interfaces** (`src/llm_interfaces/`): Multiple specialized LLM clients for different tasks:
   - `task_guidance_llm`: Generates step-by-step guidance
   - `user_input_interpreter_llm`: Processes user input and updates context
   - `query_generator_llm`: Creates search queries
   - `troubleshooting_llm`: Handles error analysis
   - `error_classifier_llm`: Classifies and categorizes errors

3. **Context Management** (`src/db_context_manager/`): Handles session state and context persistence
4. **Validation** (`src/context_validator/`): Validates context against JSON schemas
5. **Database Interface** (`src/db_fitness_interface/`): Retrieval interface for fitness knowledge base

#### AWS Services Used
- **Lambda Functions**: Serverless compute (defined in `serverless.yml`)
- **DynamoDB Tables**:
  - `ArnoldSessions`: Main session data
  - `ArnoldMessages`: Chat messages
  - `ArnoldClients`: Client information  
  - `ArnoldSessionVersions`: Session versioning
  - `Organizations` & `OrganizationMembers`: Multi-tenancy
- **S3**: Checklist storage
- **Qdrant Cloud**: Vector database for knowledge retrieval
- **Cognito**: Authentication and authorization

#### Key Lambda Functions
- `createSession`: Initialize new fitness coaching sessions
- `processChatMessage`: Main chat processing pipeline  
- `getSessionContext`: Retrieve session state
- `updateChecklist`: Update checklist progress
- `addMessage`/`listMessages`: Message management
- Client management endpoints (`createClient`, `getClients`, etc.)

### Local Development
Two CLI interfaces are available for local development:

**Modern Interface (`arnold_cli_modern.py`)**: 
- Clean, colorful interface optimized for Windows compatibility
- Beautiful formatting without problematic Unicode characters
- Recommended for daily development work

**Legacy Interface (`arnold_main_local.py`)**:
- Original testing interface with detailed debug output
- Useful for troubleshooting and development debugging
- More verbose logging for technical analysis

Both interfaces:
- Mock DynamoDB and S3 services locally
- Use actual Lambda handlers for accurate testing
- Include context change tracking and token usage monitoring

## Checklist System

The platform uses a structured checklist system for fitness coaching workflows:
- **Phases**: High-level coaching phases (Assessment, Planning, Implementation, Monitoring)
- **Tasks**: Grouped coaching activities  
- **Checks**: Individual verification steps
- **Threaded Checks**: Complex checks with sub-steps (referenced in documentation)

Checklists are stored as JSON files in `data/checklists/` and loaded from S3 in production.

## Development Notes

### Context Management
The system maintains a complex context object that includes:
- Session metadata and goals
- Current checklist state and progress
- Findings and evidence
- LLM interaction history
- Token usage tracking

### Token Usage Tracking
The platform includes comprehensive token usage monitoring with:
- Per-operation token counting
- Session-level aggregation
- Cost estimation
- Performance metrics

### Error Handling
Multi-layered error handling with specialized LLM-based troubleshooting that can:
- Classify errors by type
- Provide contextual troubleshooting steps
- Auto-retry failed operations

## Key Files to Understand

- `serverless.yml`: AWS infrastructure definition and environment variables
- `backend/lambda_handlers.py`: All Lambda function implementations
- `src/orchestrator/orchestrator.py`: Main workflow coordination logic
- `arnold_cli_modern.py`: Modern CLI interface for local development
- `arnold_main_local.py`: Legacy CLI interface for debugging
- `requirements.txt`: Python dependencies
- `package.json`: Node.js dependencies for serverless framework
- `data/checklists/`: Fitness coaching checklist definitions
- `data/fitness_knowledge/`: Structured fitness knowledge base for RAG
- `Scripts/`: Utility scripts for testing and setup

## Data Privacy and Security Considerations

This is a fitness coaching platform that handles personal health and wellness data. When working with this codebase:
- Protect user health and fitness data with appropriate security measures
- Follow health data privacy regulations (HIPAA, GDPR where applicable)
- Ensure secure handling of personal metrics and progress data
- Only use for legitimate fitness and wellness coaching purposes