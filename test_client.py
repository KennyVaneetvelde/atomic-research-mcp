import asyncio
import sys
import json
import logging
from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    # Connect to the server using the current Python interpreter
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "agentic_research_mcp.server"],
    )

    logger.info("\n📱 Starting MCP client...\n")

    try:
        # Connect to the server and create a session
        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                # Initialize the session and get available tools
                await session.initialize()
                tools = await session.list_tools()
                logger.info("🔧 Available tools: %s", ", ".join(tool.name for tool in tools.tools))

                # Call the hello tool
                logger.info("Testing hello tool...")
                response = await session.call_tool(
                    name="hello",
                    arguments={"args": {}},
                )
                logger.info("\n💬 Server response (hello): %s", response.content[0].text)

                # Test the web search pipeline
                logger.info("\n🔍 Testing web search pipeline...")
                search_question = "What are the latest advancements in quantum computing?"

                try:
                    logger.info("\n❓ Question: %s", search_question)
                    logger.info("Calling web_search_pipeline tool...")

                    response = await session.call_tool(
                        name="web_search_pipeline",
                        arguments={
                            "args": {
                                "instruction": search_question,
                                "num_queries": 3
                            }
                        },
                    )

                    logger.info("Received response from web_search_pipeline")
                    response_text = response.content[0].text
                    logger.info("Raw response: %s", response_text)

                    # Parse and display the JSON response
                    result = json.loads(response_text)

                    if "error" in result:
                        logger.error("Pipeline error: %s", result["error"])
                        if "traceback" in result:
                            logger.error("Traceback: %s", result["traceback"])
                        return

                    # Print generated queries
                    print("\n🔎 Generated Search Queries:")
                    for i, query in enumerate(result.get("queries_generated", [])):
                        print(f"  {i+1}. {query}")

                    # Print top search results
                    print("\n📊 Top Search Results:")
                    for i, result_item in enumerate(result.get("search_results", [])[:5]):  # Show top 5
                        print(f"  {i+1}. {result_item['title']} ({result_item['score']:.4f})")
                        print(f"     URL: {result_item['url']}")

                    # Print the generated answer
                    print("\n📝 Generated Answer:")
                    print(result.get("answer", "No answer generated"))

                    # Print references if available
                    if result.get("references"):
                        print("\n📚 References:")
                        for i, ref in enumerate(result["references"]):
                            print(f"  {i+1}. {ref}")

                    # Print follow-up questions if available
                    if result.get("followup_questions"):
                        print("\n❓ Suggested Follow-up Questions:")
                        for i, question in enumerate(result["followup_questions"]):
                            print(f"  {i+1}. {question}")

                except json.JSONDecodeError as e:
                    logger.error("Failed to parse JSON response: %s", str(e))
                    logger.error("Raw response content: %s", response.content[0].text if response and response.content else "No content")
                except Exception as e:
                    logger.error("Error in web search pipeline: %s", str(e))
                    import traceback
                    logger.error("Traceback: %s", traceback.format_exc())

    except Exception as e:
        logger.error("Error connecting to server: %s", str(e))
        import traceback
        logger.error("Traceback: %s", traceback.format_exc())


if __name__ == "__main__":
    asyncio.run(main())
