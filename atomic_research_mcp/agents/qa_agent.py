"""Question answering agent for the Deep Research MCP server."""

import instructor
import openai
from pydantic import Field
from atomic_agents.agents.base_agent import BaseIOSchema, BaseAgent, BaseAgentConfig
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator

from agentic_research_mcp.tools.webpage_scraper import WebpageScraperToolOutputSchema

from ..config import ChatConfig



class QuestionAnsweringAgentInputSchema(BaseIOSchema):
    """Input schema for the QuestionAnsweringAgent."""

    question: str = Field(..., description="The question to answer.")
    context: list[WebpageScraperToolOutputSchema] = Field(
        ...,
        description="List of scraped webpages used to generate the answer.",
    )


class QuestionAnsweringAgentOutputSchema(BaseIOSchema):
    """Output schema for the QuestionAnsweringAgent."""

    answer: str = Field(..., description="The answer to the question.")


def create_qa_agent() -> BaseAgent:
    """Creates and configures a new question answering agent."""
    return BaseAgent(
        BaseAgentConfig(
            client=instructor.from_openai(openai.OpenAI(api_key=ChatConfig.api_key)),
            model=ChatConfig.model,
            system_prompt_generator=SystemPromptGenerator(
                background=[
                    "You are an expert research assistant focused on providing accurate, well-sourced information.",
                    "Your answers should be based on the provided web content and include relevant source citations.",
                ],
                steps=[
                    "Analyze the question and identify key information needs",
                    "Review all provided web content thoroughly",
                    "Synthesize information from multiple sources",
                    "Formulate a clear, comprehensive answer",
                ],
                output_instructions=[
                    "Answer should be detailed but concise",
                    "Include specific facts and data from sources",
                    "If sources conflict, acknowledge the discrepancy",
                    "If information is insufficient, acknowledge limitations",
                ],
            ),
            input_schema=QuestionAnsweringAgentInputSchema,
            output_schema=QuestionAnsweringAgentOutputSchema,
        )
    )
