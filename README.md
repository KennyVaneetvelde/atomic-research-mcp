# Atomic Research MCP

A powerful web research pipeline MCP built using the [Atomic Agents framework](https://github.com/BrainBlend-AI/atomic-agents).

For a full breakdown of the code, please [check out this article](https://medium.com/ai-advances/using-custom-agents-in-cursor-windsurf-copilot-and-others-to-supercharge-your-workflow-f936b630c5e5?sk=30cd72ee79ef8333d5935d556f79471e) 

For now, this requires an API key for [Tavily](https://tavily.com/) and also [an OpenAI API key ](https://platform.openai.com/api-keys). In the future, I plan to make this more configurable so you can use SearxNG instead of Tavily or use Groq or Anthropic instead of OpenAI, thanks to the Atomic Agents framework this is all easy and possible, it just requires a bit of time and I wanted to get the initial project out there. **Feel free to contribute, though!**

## Support

Do you like this project? [Please consider a small donation](https://www.paypal.com/paypalme/KennyVaneetvelde), it means the world to me!

## Overview

This project implements an advanced web research pipeline that leverages the Model Context Protocol (MCP) and Atomic Agents to provide comprehensive answers to research questions. The pipeline automates the entire research process:

1. Generating optimized search queries
2. Performing web searches using Tavily
3. Scraping and processing relevant web pages
4. Synthesizing information into coherent answers

## Architecture

The system follows a modular architecture based on the MCP client-server model:

### Core Components

- **MCP Server**: Implements the Model Context Protocol to expose tools and manage client connections
- **Web Search Pipeline**: Orchestrates the research workflow through multiple stages
- **Atomic Agents**: Specialized AI agents for query generation and question answering
- **Tools**: Reusable components for web search (Tavily) and web page scraping

### Pipeline Flow

```
User Question → Query Generation → Web Search → Content Scraping → Answer Synthesis → Formatted Response
```

## Technologies

- **Model Context Protocol (MCP)**: An open standard for AI applications to access contextual information
- **Atomic Agents**: A modular framework for building AI agents with well-defined input/output schemas
- **Tavily API**: A specialized search engine for AI applications
- **OpenAI**: Powers the underlying language models for query generation and answer synthesis
- **Python 3.12+**: The foundation of the application

## Setup

### Prerequisites

- Python 3.12 or higher
- Tavily API key
- OpenAI API key

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/agentic-research-mcp.git
   cd agentic-research-mcp
   ```

2. Install dependencies:
   ```bash
   pip install -e .
   ```

3. Set up environment variables:
   ```bash
   # Create a .env file in the project root
   echo "TAVILY_API_KEY=your_tavily_api_key" > .env
   echo "OPENAI_API_KEY=your_openai_api_key" >> .env
   ```

## Usage

### Running the Server

Start the MCP server:

```bash
python -m atomic_research_mcp.server
```

OR
```bash
[rootfolder]\atomic-reseearch-mcp\.venv\Scripts\atomic-research
```

OR configure it in, for example, Cursor

![image](https://github.com/user-attachments/assets/8b04863a-a5ed-4f90-8f56-723c9bd388ab)


### Testing with the Client

Run the test client to verify functionality:

```bash
python test_client.py
```

### Example Output

The system returns comprehensive research results including:

- Generated search queries
- Top search results with relevance scores
- A detailed answer synthesized from multiple sources
- References to source materials
- Suggested follow-up questions

## Project Structure

```
atomic_research_mcp/
├── agents/
│   ├── query_agent.py    # Generates optimized search queries
│   └── qa_agent.py       # Synthesizes answers from scraped content
├── tools/
│   ├── tavily_search.py  # Interface to Tavily search API
│   └── webpage_scraper.py # Extracts and processes web content
├── server.py             # MCP server implementation
└── config.py             # Configuration settings
```

## Configuration

The system can be configured through environment variables:

- `TAVILY_API_KEY`: Required for web search functionality
- `OPENAI_API_KEY`: Required for AI agent operations
- `OPENAI_MODEL`: Optional, defaults to "gpt-4o-mini"

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[MIT License](LICENSE)
