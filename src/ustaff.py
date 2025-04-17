import json
from openai import OpenAI
from .env import *
from .colors import *
from .ChromaDataBase import ChromaDB
from .tools.web_search import web_search, web_search_tool
MAX_MESSAGE_COUNT = 15


TOOLS_DATA_RETRIEVAL = [
    web_search_tool,
    # database_request.database_query_tool
    ]

class ustaff:
    def __init__(self):
        self.client = client = OpenAI(
            api_key=GEMINI_API_KEY,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        self.conversation = []
        self.db = ChromaDB()
        self.prev_sources = ""
    def get_contextual_response(self, query: str) -> str:
        """
        Get a contextual response from the assistant.
        """
        
        response = ""
        intent, additional_data = self.get_users_intent(query)
        RAG_processed = self.cut_off_unrelated(intent, additional_data)
        contents = self.conversation
        combined_prompt = f"[approximated user's query] {intent} [data you may need for answer] {RAG_processed} [original users query] {query}"
        new_request = {
            "role": "user",
            "content": combined_prompt
        }
        print(GREEN, combined_prompt, RESET)
        contents.append(new_request)
        response = self.client.chat.completions.create(
            model=GEMINI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_INSTRUCTION
                },
                *contents
            ],
        ).choices[0].message.content
        
        new_response = {
            "role": "assistant",
            "content": response
        }
        new_response = {
            "role": "assistant",
            "content": response,
        }
        self.conversation = contents
        self.conversation.append(new_response)
        if len(self.conversation) > MAX_MESSAGE_COUNT:
            self.conversation = self.conversation[-MAX_MESSAGE_COUNT:]
        self.prev_sources = RAG_processed
        return response
    
    def get_users_intent(self, query: str) -> str:        
        context = ""
        for turn in self.conversation:
            context += str(turn)
            
        print(f"{YELLOW}starting intent processing{RESET}")
        response = self.client.chat.completions.create(
            model=GEMINI_MODEL,
            # tools=TOOLS_DATA_RETRIEVAL,
            # tool_choice='required',
            messages=[
            {"role": "system", "content": "Ты должен определить намерение пользователя на основе его запроса и истории чата. Используй язык, кторый использует пользователь или язык, который подходит для данной задачи."},
            {"role": "user", "content": f"""
    Тебе нужно исходя из истории переписки и запрса пользователя определить, обобщить и развернуто описать запрос пользователя.```{context}```
    Запрос пользователя: ```{query}```
    Используй функции для получения необходимой пользователю информации.
    """}
            ],
        )
        
        additional_info = ""
        intent = response.choices[0].message.content
        # Check if function was called
        print(f"{GREEN}Intent: {intent}{RESET}")
        additional_info = self.additional_info_request(intent)
        additional_info += self.prettyfy(self.RAG(intent))
        # print(additional_info)
        return intent, additional_info
    
    
    def additional_info_request(self, intent):
        response = self.client.chat.completions.create(
            model=GEMINI_MODEL,
            tools=TOOLS_DATA_RETRIEVAL,
            tool_choice='required',
            messages=[
            {"role": "system", "content": "Тебе нужно использовать функции для получения информации, которая поможет ответить на запрос пользователя."},
            {"role": "user", "content": f"""Запрос пользователя {intent}"""}
            ],
        )
        additional_info = ""
        if response.choices[0].message.tool_calls:
            # Handle each tool call
            for tool_call in response.choices[0].message.tool_calls:
                # Get the function name and arguments
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                print(MAGENTA, function_name, function_args, RESET )
                if function_name == "qet_local_data_from_database":
                    function_response = self.prettyfy(self.RAG(intent))
                else:
                    function_response = globals()[function_name](**function_args)
                additional_info += function_response
        return additional_info        
        
    def RAG(self, query) -> list:
        """
        Perform Retrieval-Augmented Generation (RAG) to get relevant documents.
        """
        results = self.db.search(query, n=5)

        return results
        
    def prettyfy(self, items: list) -> str:
        """
        Format a list into a numbered string.
        Args:
            items: List of items to format
        Returns:
            Formatted string with numbered items
        """
        if not items:
            return ""
        result = ""
        for i in range(len(items["documents"][0])):
            result += f"   Filename: {items['metadatas'][0][i]['filesrc']}\n"
            result += f"   Distance: {items['distances'][0][i]}\n"
            result += f"{i+1}. Document content: {items['documents'][0][i]}\n"
        return result

    def cut_off_unrelated(self, intent:str, data:str) -> str:
        """
        Cut off unrelated parts of the data based on the intent.
        """
        response = self.client.chat.completions.create(
            model=GEMINI_MODEL,
            messages=[
                {"role": "system", "content": "Ты должен удалить из текста все части, которые не относятся к запросу пользователя и не имеют смысла. Если удаляешь документ, оставь зпись о том, какой документ был удален (включи документ и distance). Оставляй названия файлов и показатель расстояния. Преобразуй в markdown форматирование"},
                {"role": "user", "content": f"""[user's intent]{intent} [recieved data]{data}"""}     
            ]
        )
        print(data)
        print(f"{RED}Cut off unrelated: \n{GREEN}{response.choices[0].message.content}{RESET}")
        return response.choices[0].message.content