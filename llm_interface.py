# llm_interface.py
import json

from openai import OpenAI
from config import OPENAI_API_KEY, MODEL_NAME, TEMPERATURE, MAX_TOKENS

class LLMInterface:
    def __init__(self):
        # Instantiate an OpenAI client with the API key
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = MODEL_NAME
        self.temperature = TEMPERATURE
        self.max_tokens = MAX_TOKENS


    def get_response(self, prompt):
        try:
            # Use the instantiated client to create a chat completion
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful jobs-to-be-done job mapping research expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            # Updated way to access the content of the response
            content = response.choices[0].message.content.strip()
            return content
        except Exception as e:
            print(f"Error communicating with LLM: {e}")
            return ""
            
    # def get_response(self, prompt, tools=None):
    #     try:
    #         # Construct the messages array
    #         messages = [
    #             {"role": "system", "content": "You are a helpful jobs-to-be-done job mapping research expert."},
    #             {"role": "user", "content": prompt}
    #         ]

    #         # # Define tool call based on function schema provided
    #         # function_call_argument = {"name": function_schema["name"]} if function_schema else None

            
    #         # Create chat completion with function calling
    #         response = self.client.chat.completions.create(
    #             model=self.model,
    #             messages=messages,
    #             temperature=self.temperature,
    #             max_tokens=self.max_tokens,
    #             tools=tools,  # Pass tools parameter here
    #             tool_choice="required"  # Specify that we require the function call
    #             # functions=[function_schema] if function_schema else [],  # Pass schema list
    #             # function_call=function_call_argument
    #         )

    #         # If function_call is triggered, return structured arguments
    #         if tools: # and "function_call" in response.choices[0].message:
    #             tool_call = response.choices[0].message.tool_calls[0]
    #             print(response.choices[0].message.tool_calls[0].function)
    #             arguments = json.loads(tool_call['function']['arguments'])  # Directly return parsed arguments

    #         # if tools and "tool_calls" in response.choices[0].message:
    #         #     tool_call = response.choices[0].message["tool_calls"][0]
    #         #     return json.loads(tool_call["function"]["arguments"])  # Directly return parsed arguments


    #         # Otherwise, return plain text content
    #         content = response.choices[0].message.content.strip()
    #         return content
    #     except Exception as e:
    #         print(f"Error communicating with LLM: {e}")
    #         return ""
