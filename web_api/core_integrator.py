import yaml
from typing import Dict, Any, Optional

# Adjust these import paths based on your project structure
# Assuming 'editorial_agents_project' is a sibling to 'web_api' or in PYTHONPATH
from agents.initial_analysis_agent import InitialAnalysisAgent, ArticleOutline
from agents.unified_retrieval_agent import UnifiedRetrievalAgent
from agents.comprehensive_answer_agent import ComprehensiveAnswerAgent

# Configuration loading - adjust path as necessary
CONFIG_PATH = 'config/config.yaml' # Relative to the root of where the FastAPI app might run from

_config_cache: Optional[Dict[str, Any]] = None

def load_app_config() -> Dict[str, Any]:
    global _config_cache
    if _config_cache is None:
        try:
            # Try to load relative to where web_api might be launched from (e.g., project root)
            with open(CONFIG_PATH, 'r') as file:
                _config_cache = yaml.safe_load(file)
        except FileNotFoundError:
            # Fallback if running from within web_api directory (adjust as needed)
            try:
                with open(f'../{CONFIG_PATH}', 'r') as file:
                    _config_cache = yaml.safe_load(file)
            except FileNotFoundError:
                raise Exception(f"Configuration file {CONFIG_PATH} not found.")
    return _config_cache

class AgentIntegrator:
    def __init__(self):
        self.config = load_app_config()
        self.initial_analysis_agent = InitialAnalysisAgent(self.config['initial_analysis'])
        # UnifiedRetrievalAgent and ComprehensiveAnswerAgent might be better instantiated on-demand 
        # if they hold significant state or resources, or if their configs can change per process.
        # For now, let's assume they can be initialized once if configs are static for them.
        self.unified_retrieval_config_web = self.config['web_search']
        self.unified_retrieval_config_kb = self.config['local_kb']
        self.comprehensive_answer_config = self.config['comprehensive_answer']

    def generate_initial_outline(self, topic: str, description: str, problem: str) -> ArticleOutline:
        return self.initial_analysis_agent.get_framework(topic=topic, description=description, problem=problem)

    def get_unified_retrieval_agent(self) -> UnifiedRetrievalAgent:
        # Instantiate fresh to ensure no state crossover if it holds per-run state
        # Or ensure its methods are stateless regarding prior calls if reused.
        return UnifiedRetrievalAgent(
            web_config=self.unified_retrieval_config_web, 
            kb_config=self.unified_retrieval_config_kb
        )

    def get_comprehensive_answer_agent(self) -> ComprehensiveAnswerAgent:
        return ComprehensiveAnswerAgent(self.config['comprehensive_answer'])

# Singleton instance of the integrator
agent_integrator_instance = AgentIntegrator()

def get_agent_integrator() -> AgentIntegrator:
    return agent_integrator_instance 