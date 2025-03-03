from typing import Dict, List, Any, Optional
from crewai.tools import BaseTool
from elasticsearch import Elasticsearch
import json
from pydantic import BaseModel, Field, ConfigDict

class ElasticsearchToolConfig(BaseModel):
    es_host: str
    user: str
    passwd: str

class ElasticsearchTool(BaseTool):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    name: str = Field(default="elasticsearch_tool")
    description: str = Field(default="""
    Tool for interacting with Elasticsearch. Useful for searching and analyzing data.
    input should be 2 parameters: index and image_class
    """)
    es_client: Optional[Elasticsearch] = Field(default=None, exclude=True)

    @classmethod
    def from_config(cls, config: ElasticsearchToolConfig) -> "ElasticsearchTool":
        tool = cls()
        tool.es_client = Elasticsearch(
            hosts=config.es_host,
            verify_certs=False,
            basic_auth=(config.user, config.passwd),
            request_timeout=300,
            retry_on_timeout=True,
            max_retries=5,
            http_compress=True,
        )
        return tool

    def _run(self, index: str,image_class:str) -> str:
        """Execute the Elasticsearch operation"""
        try:
            print(index,image_class)

            query ={
                "_source":["_id","meta.short_name"],
                "query": {
                    "bool": {
                        "must": [
                            {
                                "nested": {
                                    "path": "meta.image_classification",
                                    "query": {
                                    "bool": {
                                        "must": [
                                        {
                                            "match": { "meta.image_classification.image_class": image_class }
                                        }
                                        ]
                                    }
                                    }
                                }
                            },
                            { "match": { "doc_relations": "document" } }
                        ]
                    }
                }
            }
            

            return json.dumps(self._execute_search(index, query))

            #return ["1","2","3"]
            # Parse the input JSON
            # params = json.loads(tool_input)
            # operation = params.get('operation', 'search')
            # index = params.get('index')
            # query = params.get('query', {"match_all": {}})

            # if not index:
            #     return "Error: No index specified"

            # if operation == "search":
            #     return self._execute_search(index, query)
            # elif operation == "count":
            #     return self._execute_count(index, query)
            # else:
            #     return f"Error: Unknown operation {operation}"
            
            return self._execute_count(index, query)
        except json.JSONDecodeError:
            return "Error: Invalid JSON input"
        except Exception as e:
            return f"Error: {str(e)}"
        
    def _execute_search(self, index: str, query: Dict[str, Any]) -> str:
        """Execute search operation"""
        try:
            response = self.es_client.search(
                index=index,
                body=query
            )
            print(response)
            ids=[]
            for hit in response['hits']['hits']:
                ids.append({"_id":hit['_id'],"short_name":hit['_source']['meta']['short_name']})
            return ids
            #return json.dumps(response['hits']['hits'], indent=2)
        except Exception as e:
            return f"Search error: {str(e)}"

    def _execute_count(self, index: str, query: Dict[str, Any]) -> str:
        """Execute count operation"""
        try:
            response = self.es_client.count(
                index=index,
                body=query
            )
            return str(response['count'])
        except Exception as e:
            return f"Count error: {str(e)}"

    async def _arun(self, tool_input: str) -> str:
        """Async implementation of the tool"""
        return self._run(tool_input)