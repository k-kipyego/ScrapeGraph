import time
from scrapegraphai.graphs import SmartScraperGraph
from scrapegraphai.utils import prettify_exec_info

# ************************************************
# Define the configuration for the graph
# ************************************************


graph_config = {
    "llm": {
        "model": "ollama/mistral",
        "temperature": 0,
        "format": "json",
        "base_url": "http://localhost:11434",
    },
    "embeddings": {
        "model": "ollama/nomic-embed-text",
        "base_url": "http://localhost:11434",
    },
    "verbose": True,
}
# ************************************************
# Create the SmartScraperGraph instance and run it
# ************************************************
smart_scraper_graph = SmartScraperGraph(
    prompt="List me all procurements posted in this page with their relevant information",
    source="https://procurement-notices.undp.org/",
    config=graph_config
)

# Record start time
start_time = time.time()

# Run the scraper
result = smart_scraper_graph.run()

# Record end time
end_time = time.time()

# Calculate the time taken
time_taken = end_time - start_time
print(f"Time taken to scrape the website: {time_taken:.2f} seconds")

# Print the scraping result
print(result)

# ************************************************
# Get graph execution info
# ************************************************
graph_exec_info = smart_scraper_graph.get_execution_info()
print(prettify_exec_info(graph_exec_info))
