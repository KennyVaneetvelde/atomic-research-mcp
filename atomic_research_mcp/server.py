import logging
import os
import json
import traceback
from mcp.server.fastmcp import FastMCP

# Import required components for the web search pipeline
from atomic_research_mcp.agents.query_agent import create_query_agent, QueryAgentInputSchema
from atomic_research_mcp.agents.qa_agent import create_qa_agent, QuestionAnsweringAgentInputSchema
from atomic_research_mcp.tools.tavily_search import (
    TavilySearchTool,
    TavilySearchToolConfig,
    TavilySearchToolInputSchema
)
from atomic_research_mcp.tools.webpage_scraper import (
    WebpageScraperTool,
    WebpageScraperToolInputSchema
)

# Set up logging to show INFO level messages
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    # Create a new MCP server with the identifier "tutorial"
    mcp = FastMCP("research_pipeline")
    logger.info("Starting research pipeline server...")

    try:
        # Initialize the components
        logger.info("Initializing query agent...")
        query_agent = create_query_agent()

        logger.info("Initializing QA agent...")
        qa_agent = create_qa_agent()

        # Initialize Tavily search tool with API key from environment
        tavily_api_key = os.getenv("TAVILY_API_KEY", "")
        if not tavily_api_key:
            logger.error("TAVILY_API_KEY environment variable is not set. Web search will not work properly.")
            raise ValueError("TAVILY_API_KEY environment variable must be set")

        logger.info("Initializing Tavily search tool...")
        tavily_tool = TavilySearchTool(
            config=TavilySearchToolConfig(
                api_key=tavily_api_key,
                max_results=5,  # Limiting to top 5 results per query
                include_answer=True
            )
        )

        logger.info("Initializing web scraper tool...")
        scraper_tool = WebpageScraperTool()

        @mcp.tool(
            name="web_search_pipeline",
            description="Performs a web search pipeline: generates queries, searches web, sorts results, scrapes pages, and answers questions."
        )
        async def web_search_pipeline(args: dict) -> str:
            # Extract the instruction and question
            instruction = args.get("instruction", "")
            question = args.get("question", instruction)  # Use instruction as question if not provided
            num_queries = args.get("num_queries", 3)

            logger.info(f"Starting web search pipeline for question: {question}")

            try:
                # Step 1: Generate search queries using query agent
                logger.info(f"Step 1: Generating {num_queries} search queries...")
                query_input = QueryAgentInputSchema(instruction=instruction, num_queries=num_queries)
                query_result = query_agent.run(query_input)
                queries = query_result.queries
                logger.info(f"Generated queries: {queries}")

                # Step 2: Perform web search using Tavily
                logger.info(f"Step 2: Performing web search with {len(queries)} queries...")
                search_input = TavilySearchToolInputSchema(queries=queries)
                search_results = tavily_tool.run(search_input)
                logger.info(f"Received {len(search_results.results)} search results")

                # Step 3: Sort results by score in descending order
                logger.info("Step 3: Sorting results by score...")
                sorted_results = sorted(search_results.results, key=lambda x: x.score, reverse=True)
                logger.info(f"Top result score: {sorted_results[0].score if sorted_results else 'No results'}")

                # Step 4: Take top results and scrape their content
                top_results = sorted_results[:5]  # Limit to top 5 results
                scraped_pages = []
                logger.info(f"Step 4: Scraping content from top {len(top_results)} results...")

                for i, result in enumerate(top_results):
                    try:
                        logger.info(f"Scraping {i+1}/{len(top_results)}: {result.url}")
                        scrape_input = WebpageScraperToolInputSchema(url=result.url)
                        scrape_result = scraper_tool.run(scrape_input)
                        scraped_pages.append(scrape_result)
                        logger.info(f"Successfully scraped {result.url}")
                    except Exception as e:
                        logger.error(f"Error scraping {result.url}: {str(e)}")
                        logger.error(traceback.format_exc())

                # Step 5: Generate answer using QA agent
                logger.info("Step 5: Generating answer using QA agent...")
                qa_input = QuestionAnsweringAgentInputSchema(question=question, context=scraped_pages)
                qa_result = qa_agent.run(qa_input)
                logger.info("Answer generated successfully")

                # Return comprehensive result as JSON string
                result = {
                    "question": question,
                    "queries_generated": queries,
                    "search_results": [
                        {
                            "title": result.title,
                            "url": result.url,
                            "score": float(result.score)  # Ensure score is serializable
                        } for result in sorted_results[:10]  # Include top 10 search results in response
                    ],
                    "answer": qa_result.markdown_output if hasattr(qa_result, 'markdown_output') else qa_result.answer,
                    "references": qa_result.references if hasattr(qa_result, 'references') else [],
                    "followup_questions": qa_result.followup_questions if hasattr(qa_result, 'followup_questions') else []
                }
                logger.info("Pipeline completed successfully")
                return json.dumps(result)  # Return JSON string

            except Exception as e:
                logger.error(f"Error in pipeline execution: {str(e)}")
                logger.error(traceback.format_exc())
                error_response = {
                    "error": str(e),
                    "question": question,
                    "stage": "pipeline execution",
                    "traceback": traceback.format_exc()
                }
                return json.dumps(error_response)  # Return error as JSON string

        logger.info("All components initialized successfully. Starting server...")
        # Start the server
        mcp.run()

    except Exception as e:
        logger.error(f"Error during server initialization: {str(e)}")
        logger.error(traceback.format_exc())
        raise


if __name__ == "__main__":
    main()
