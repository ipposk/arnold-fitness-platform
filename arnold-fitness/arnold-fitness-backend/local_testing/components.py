"""
Component initialization for local testing
This uses the EXACT same components as the AWS deployment
"""
from src.db_context_manager.db_manager import DbContextManager
from src.context_validator.context_validator import ContextValidator
from src.llm_interfaces.clients.gemini_client import GeminiClient
from src.llm_interfaces.user_input_interpreter_llm.user_input_interpreter_llm import UserInputInterpreterLLM
from src.llm_interfaces.query_generator_llm.query_generator_llm import QueryGeneratorLLM
from src.llm_interfaces.task_guidance_llm.task_guidance_llm import TaskGuidanceLLM
from src.llm_interfaces.troubleshooting_llm.troubleshooting_llm import TroubleshootingLLM
from src.llm_interfaces.error_classifier_llm.error_classifier_llm import ErrorClassifierLLM
from src.db_fitness_interface.mock_fitness_retriever import MockFitnessRetriever as FitnessRetriever
from src.orchestrator.orchestrator import Orchestrator

from .config import (
    SCHEMA_PATH, INTERPRETER_PROMPTS_DIR, GENERATOR_PROMPTS_DIR,
    TASK_GUIDANCE_PROMPT_PATH, TROUBLESHOOTER_PROMPT_PATH, ERROR_CLASSIFIER_PROMPT_PATH
)


def initialize_components():
    """
    Initialize all components exactly as they are used in AWS Lambda
    Returns a dict with all initialized components
    """
    print("Initializing components...")

    # Initialize base components
    db_manager = DbContextManager()
    validator = ContextValidator(SCHEMA_PATH)
    gemini_client = GeminiClient()

    # Initialize LLM components
    interpreter_llm = UserInputInterpreterLLM(
        llm_client=gemini_client,
        prompt_templates_dir=INTERPRETER_PROMPTS_DIR
    )

    query_generator_llm = QueryGeneratorLLM(
        llm_client=gemini_client,
        prompt_templates_dir=GENERATOR_PROMPTS_DIR
    )

    retriever = FitnessRetriever()

    task_guidance_llm = TaskGuidanceLLM(
        llm_client=gemini_client,
        retriever=retriever,
        prompt_template_path=TASK_GUIDANCE_PROMPT_PATH
    )

    troubleshooting_llm = TroubleshootingLLM(
        client=gemini_client,
        prompt_template_path=TROUBLESHOOTER_PROMPT_PATH
    )

    error_classifier_llm = ErrorClassifierLLM(
        client=gemini_client,
        prompt_template_path=ERROR_CLASSIFIER_PROMPT_PATH
    )

    # Initialize orchestrator
    orchestrator = Orchestrator(
        db_manager=db_manager,
        validator=validator,
        interpreter=interpreter_llm,
        query_generator_llm=query_generator_llm,
        task_guidance_llm=task_guidance_llm,
        troubleshooter_llm=troubleshooting_llm,
        error_classifier_llm=error_classifier_llm,
        client=gemini_client
    )

    print("✅ All components initialized successfully!")

    return {
        'db_manager': db_manager,
        'validator': validator,
        'orchestrator': orchestrator,
        'gemini_client': gemini_client
    }