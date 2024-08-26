# Import the required libraries
import streamlit as st
import time
import json
from scrapegraphai.graphs import SmartScraperGraph
from openai import RateLimitError
from transformers import GPT2TokenizerFast

# Set up the Streamlit app
st.title("Web Scraping AI Agent 🕵️‍♂️")
st.caption("This app allows you to scrape a website using OpenAI API")

# Get OpenAI API key from the user
openai_access_token = st.text_input("OpenAI API Key", type="password")

if openai_access_token:
    model = st.radio(
        "Select the model",
        ["gpt-3.5-turbo", "gpt-4"],
        index=0,
    )
    
    graph_config = {
        "llm": {
            "api_key": openai_access_token,
            "model": model,
        },
    }
 
    url = st.text_input("Enter the URL of the website you want to scrape")
    
    # Get the user prompt
    default_prompt = "Scrape procurement opportunities in Software, Tech, Digital, and IT. Extract name, description, and deadline."    
    # Initialize tokenizer
    tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")

    # Define the token limit (for example, 3000 tokens per chunk to stay well below the max)
    token_limit = 3000
    
    # Function to split content into chunks based on token count
    def chunk_text_by_tokens(text, tokenizer, token_limit):
        tokens = tokenizer.encode(text)
        chunks = []
        for i in range(0, len(tokens), token_limit):
            chunk_tokens = tokens[i:i + token_limit]
            chunk_text = tokenizer.decode(chunk_tokens)
            chunks.append(chunk_text)
        return chunks
    
    # Function to retrieve content from the URL (mock function)
    def retrieve_content_from_url(url):
        # Placeholder for actual content retrieval logic
        # Replace with your content extraction logic
        return "Sample content from the website..."  # Placeholder content
    
    # Scrape the website
    if st.button("Scrape"):
        try:
            # Start timing the scraping process
            start_time = time.time()

            # Retrieve the content from the URL
            full_content = retrieve_content_from_url(url)
            
            # Split the content into chunks based on tokens
            chunks = chunk_text_by_tokens(full_content, tokenizer, token_limit)

            # Process each chunk and store the results
            results = []
            for chunk in chunks:
                # Create a SmartScraperGraph object for each chunk
                smart_scraper_graph = SmartScraperGraph(
                    prompt=f"{default_prompt} Process this chunk: {chunk}",
                    source=url,
                    config=graph_config
                )
                result = smart_scraper_graph.run()
                # Assuming result is a dict, add it to the results list
                if isinstance(result, dict):
                    results.append(result)
                else:
                    st.error("Unexpected result format.")
                    results.append({"error": "Unexpected result format"})

            # Combine the results from all chunks into a single JSON
            combined_result = {"results": results}
            combined_result_json = json.dumps(combined_result, indent=2)
           
            # Stop timing the scraping process
            end_time = time.time()
            time_taken = end_time - start_time
            
            # Display the result and time taken
            st.json(combined_result)  # Streamlit provides a built-in method to display JSON
            st.write(f"Time taken to scrape: {time_taken:.2f} seconds")
        
        except RateLimitError:
            st.error("Rate limit exceeded. Please wait and try again later.")
            retry_seconds = 10  # Set a delay before retrying (e.g., 10 seconds)
            st.write(f"Retrying in {retry_seconds} seconds...")
            time.sleep(retry_seconds)  # Wait for the specified time before retrying
