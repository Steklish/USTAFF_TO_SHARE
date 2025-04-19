database_query_tool = {
    "type": "function",
    "function": {
        "name": "get_local_data_from_database",
        "description": "Retrieves relevant information from a local database. Local database stores information about buisness, banks, computer networks, bible and so on",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to look up in the local database."
                }
            },
            "required": ["query"]
        }
    }
}