from crewai import Agent, Task, Crew, LLM
from langchain_openai import ChatOpenAI
from es_custom_tool import ElasticsearchTool,ElasticsearchToolConfig
import os

llm = LLM(model="ollama/llama3.2", base_url="http://localhost:11434")



# Create the Elasticsearch tool
config = ElasticsearchToolConfig(
    es_host="https://canopy-internal-78a86546824bf249.elb.us-east-2.amazonaws.com:9200",
    user="elastic",
    passwd="03QIThxEN41T5Vv3UvU426J6"
)

es_tool = ElasticsearchTool.from_config(config)

# Create an agent with the tool
agent = Agent(
    role="Data Analyst",
    goal="Fetch the documents from an Elasticsearch {index} having documents with meta.image_class as {image_class}"
          "Use tool es_tool to perform the query",
    backstory="Expert in Elasticsearch and data analysis"
               "You fetch records from the Elasticsearch {index} having documents with meta.image_class as {image_class}"
               "Return list of objects with properties _id and short_name",
    tools=[es_tool],
    verbose=True,
    llm=llm,
    allow_delegation=False
)

# Create a task
task = Task(
    description="Fetch the documents from an Elasticsearch {index} having documents with meta.image_class as {image_class}",
    expected_output="List of document objects",
    agent=agent
)

# Example of tool usage in the agent
"""
The agent can use the tool with JSON input like:
{
    "operation": "count",
    "index": "my_index",
    "query": {
        "match": {
            "field": "value"
        }
    }
}
"""

# Create and run the crew
crew = Crew(
    agents=[agent],
    tasks=[task]
)
  
result = crew.kickoff(inputs={"index": "676d842baf744c86b4bb69d3","image_class": "Social Security Cards"})