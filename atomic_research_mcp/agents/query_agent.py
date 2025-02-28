"""Query generation agent for the Deep Research MCP server."""

import instructor
import openai
from pydantic import Field
from atomic_agents.agents.base_agent import BaseIOSchema, BaseAgent, BaseAgentConfig
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator

from ..tools.tavily_search import TavilySearchToolInputSchema
from ..config import ChatConfig


class QueryAgentInputSchema(BaseIOSchema):
    """Input schema for the QueryAgent."""

    instruction: str = Field(
        ...,
        description="A detailed instruction or request to generate search engine queries for.",
    )
    num_queries: int = Field(
        ..., description="The number of search queries to generate."
    )


def create_query_agent() -> BaseAgent:
    """Creates and configures a new query generation agent."""
    return BaseAgent(
        BaseAgentConfig(
            client=instructor.from_openai(openai.OpenAI(api_key=ChatConfig.api_key)),
            model=ChatConfig.model,
            system_prompt_generator=SystemPromptGenerator(
                background=[
                    "You are an expert search engine query generator with a deep understanding of which queries will maximize relevant results."
                ],
                steps=[
                    "Analyze the given instruction to identify key concepts",
                    "For each aspect, craft a search query using appropriate operators",
                    "Ensure queries cover different angles (technical, practical, etc.)",
                ],
                output_instructions=[
                    "Return exactly the requested number of queries",
                    "Format each query like a search engine query, not a question",
                    "Each query should be concise and use relevant keywords",
                ],
            ),
            input_schema=QueryAgentInputSchema,
            output_schema=TavilySearchToolInputSchema,
        )
    )
