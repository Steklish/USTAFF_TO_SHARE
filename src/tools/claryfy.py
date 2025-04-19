claryfy_tool = {
    "type": "function",
    "function": {
        "name": "clarylying_question",
        "description": "Use if additional information from a user is required.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The question for a user or a request for additional info."
                }
            },
            "required": ["query"]
        }
    }
}
