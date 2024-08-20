from scrapegraphai.graphs import SmartScraperGraph
import nest_asyncio
import json
import psycopg2
from datetime import datetime

# Apply nest_asyncio to resolve any issues with asyncio event loop
nest_asyncio.apply()

# Configuration dictionary for the graph
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

# URL of the procurement page
url = "https://www.dbsa.org/procurement"

# Initialize SmartScraperGraph with prompt and source URL
smart_scraper_graph = SmartScraperGraph(
    prompt="Extract all procurement notices with related information.",
    source=url,
    config=graph_config
)

# Run the SmartScraperGraph and store the result
result = smart_scraper_graph.run()

# Debug: Print the raw result to inspect its structure
print("Raw Result:", result)

# Ensure the result is a list or a JSON-like structure
if isinstance(result, str):
    try:
        result = json.loads(result)  # Try parsing if it's a JSON string
    except json.JSONDecodeError:
        print("Error: Result is not valid JSON.")
        result = {}

# Extract the procurement notices
procurement_notices = result.get("procurement_notices", [])
if procurement_notices:
    details_list = procurement_notices[0].get("details", [])
else:
    details_list = []

# PostgreSQL connection settings
conn = psycopg2.connect(
    dbname="RFPs",
    user="postgres",
    password="076642",
    host="127.0.0.1",
    port="5432"
)
cursor = conn.cursor()

# Create the table if it doesn't exist
create_table_query = """
CREATE TABLE IF NOT EXISTS procurement_notices (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT,
    country TEXT,
    deadline DATE,
    posting_date DATE,
    source_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
cursor.execute(create_table_query)

# Alter the table to add the price column if it doesn't exist
alter_table_query = """
ALTER TABLE procurement_notices
ADD COLUMN IF NOT EXISTS price TEXT;
"""
cursor.execute(alter_table_query)

# Prepare insert statement
insert_query = """
INSERT INTO procurement_notices (title, description, category, country, deadline, posting_date, source_url, price)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""

# Extract and format the result from details
for item in details_list:
    title = item.get("summary", "N/A")
    description = item.get("notice_type", "N/A")  # Assuming "notice_type" as description
    category = "N/A"  # Category isn't provided in the current result, so use N/A
    country = item.get("country", "N/A")
    deadline = item.get("deadline", "N/A")
    posting_date = item.get("posting_date", "N/A")
    price = "N/A"  # Price isn't provided, so use N/A
    source_url = url

    # Convert dates to proper format if available
    try:
        deadline = datetime.strptime(deadline, '%d %b %Y').date() if deadline != "N/A" else None
        posting_date = datetime.strptime(posting_date, '%d %b %Y').date() if posting_date != "N/A" else None
    except ValueError:
        deadline = None
        posting_date = None

    # Insert data into PostgreSQL
    cursor.execute(insert_query, (title, description, category, country, deadline, posting_date, source_url, price))

# Commit changes and close the connection
conn.commit()
cursor.close()
conn.close()

# Prettify the result and display the JSON
output = json.dumps(details_list, indent=2)
print(output)
