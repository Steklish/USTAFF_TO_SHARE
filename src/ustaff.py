import json
import time
from openai import OpenAI
from .env import *
from .colors import *
from .ChromaDataBase import ChromaDB
from .tools.web_search import web_search, web_search_tool
from .tools.database_request import database_query_tool

MAX_MESSAGE_COUNT = 15


TOOLS_DATA_RETRIEVAL = [
    web_search_tool,
    database_query_tool
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
    
    def get_local_data_from_database(self, query:str):
        return self.prettyfy(self.RAG(query))
    
    def get_contextual_response_stream(self, query: str):
        """
        Get a contextual response from the assistant.
        """
        
        yield "Started *user's intent* processing..."
        print("started stream processing")
        intent, additional_data = self.get_users_intent(query)
        yield "Started *data* processing..."
        RAG_processed = self.cut_off_unrelated(intent, additional_data)
        contents = self.conversation
        combined_prompt = f"[approximated user's query] {intent} [data you may need for answer] {RAG_processed} [original users query] {query}"
        # combined_prompt = query
        new_request = {
            "role": "user",
            "content": combined_prompt
        }
        print(GREEN, combined_prompt, RESET)
        contents.append(new_request)
        yield "summing up..."
        stream = self.client.chat.completions.create(
            model=GEMINI_MODEL,
            messages=[
                {"role": "system", "content": f'[current date and time] {get_current_time()}' + SYSTEM_INSTRUCTION},
                *contents
            ],
            stream=True  # Enable streaming
        )
        
        full_response = []
        time.sleep(0.1)
        yield "answering..."
        time.sleep(0.1)
        yield "answering..."
        time.sleep(0.1)
        for chunk in stream:
            content = chunk.choices[0].delta.content
            print(content)
            if content is not None:
                print(f"Yielding chunk: {repr(content)}")  # Debug output
                yield content  # Yield each chunk as it arrives
                full_response.append(content)
        
        # Store complete response in conversation history
        new_response = {
            "role": "assistant",
            "content": "".join(full_response)
        }
        self.conversation.append(new_response)
        
        if len(self.conversation) > MAX_MESSAGE_COUNT:
            self.conversation = self.conversation[-MAX_MESSAGE_COUNT:]
        
        self.prev_sources = RAG_processed
        
        
    def get_users_intent(self, query: str) -> str:        
        context = ""
        for turn in self.conversation:
            context += str(turn)
            
        print(f"{YELLOW}starting intent processing{RESET}")
        response = self.client.chat.completions.create(
            model=FAST_AND_DUMB_ASS_MODEL,
            max_completion_tokens=500,
            tools=TOOLS_DATA_RETRIEVAL,
            tool_choice='auto',
            messages=[
            {"role": "system", "content": f"You need to determine the user's intent based on their query and chat history. Use the language the user is employing or the language most appropriate for the task. [current dat and time] {get_current_time()}"},
            {
                "role": "user",
                "content": f"""
                Based on the chat history and user's request, you need to analyze, summarize, and thoroughly describe the user's query without answering it.  
                Chat history: ```{context}```  
                User's request: ```{query}```  
                Additionally, use functions (tools) to retrieve the information the user needs.
                """
            }

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
                if function_name == "get_local_data_from_database":
                    function_response = self.get_local_data_from_database(**function_args)
                else:
                    function_response = globals()[function_name](**function_args)
                additional_info += function_response
                # Handle potential missing data
        if not getattr(response, 'choices', None):
            intent = query  # Fallback to original query
        else:
            message = response.choices[0].message if len(response.choices) > 0 else None
            intent = message.content if message and hasattr(message, 'content') else query

        # Check if function was called
        print(f"{GREEN}Intent: {intent}{RESET}")
        additional_info += self.additional_info_request(intent)
        additional_info += self.prettyfy(self.RAG(intent))
        # print(additional_info)
        return intent, additional_info
    
    
    def additional_info_request(self, intent):
        response = self.client.chat.completions.create(
            model=FAST_AND_DUMB_ASS_MODEL,
            tools=TOOLS_DATA_RETRIEVAL,
            tool_choice='auto',
            messages=[
                {"role": "system", "content": f"Ты помощник для поиска ниформации. [current dat and time] {get_current_time()}"},
                {"role": "user", "content": f"""Нужно найти информацию, которая поможет ответить на запрос пользователя. Запрос пользователя {intent}"""}
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
                if function_name == "get_local_data_from_database":
                    function_response = self.get_local_data_from_database(**function_args)
                else:
                    function_response = globals()[function_name](**function_args)
                additional_info += function_response
        return additional_info        
        
    def RAG(self, query, n = 5) -> list:
        """
        Perform Retrieval-Augmented Generation (RAG) to get relevant documents.
        """
        results = self.db.search(query, n)

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
            model=FAST_AND_DUMB_ASS_MODEL,
            messages=[
                {"role": "system", "content": "Ты сортируешь информацию и выделяешь полезные части."},
                {"role": "user", "content": f"""Ты должен удалить из текста все части, которые не относятся к запросу пользователя или не имеют смысла. ОСтальное тебе нудно подытожить и сдалать развернутые выводы исходя из запроса пользователя. Если удаляешь документ, оставь зпись о том, какой документ был удален (включи документ и distance). Оставляй названия файлов и показатель расстояния. Преобразуй в markdown форматирование. !не !отвечай на запрос [user's intent]{intent} [recieved data]{data}"""}     
            ]
        )
        print(data)
        print(f"{RED}Cut off unrelated: \n{GREEN}{response.choices[0].message.content}{RESET}")
        return response.choices[0].message.content