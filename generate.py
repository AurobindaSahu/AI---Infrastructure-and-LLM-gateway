import os
import time
import logging
import warnings
import litellm
from litellm import completion
from dotenv import load_dotenv


# the unnessary error and warnings are removed 
def warnings_error_removed():
    warnings.filterwarnings("ignore")
    litellm.set_verbose = False
    litellm.suppress_debug_info = True
    logging.getLogger("LiteLLM").setLevel(logging.CRITICAL)
    logging.getLogger("asyncio").setLevel(logging.CRITICAL)


def loading_api_and_model():
    load_dotenv()
    google_key = os.getenv("GOOGLE_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")

    if google_key:
        os.environ["GOOGLE_API_KEY"] = google_key
    if groq_key:
        os.environ["GROQ_API_KEY"] = groq_key




class llm_responce:
    warnings_error_removed()
    loading_api_and_model()

    def __init__(self,prompt,primary_model):
        self.prompt = prompt
        self.primary_model = primary_model

    def generate_route(self):
        user_query = self.prompt
        routing_response = completion(
            model="groq/openai/gpt-oss-120b",
            messages=[{"role":"user","content":(f"""
                                                    Classify the following query into exactly one word:
                                                        chat
                                                        summary
                                                        general

                                                        Query: {user_query}

                                                        Output only one word. Do not explain.
                                                    """)}],
                                                max_tokens=5,
                                                temperature=0
                                        )
        result = routing_response.choices[0].message.content
        return result

    def task_model(self):
        task = self.generate_route()
        routing  = {
                    "chat" : ["openai/gpt-4o","gemini/gemini-2.0-flash","groq/llama-3.1-8b-instant"],
                    "code" :["claude/claude-3-5-sonnet-20241022","groq/llama-3.3-70b-versatile"],
                    "summary" : ["openai/gpt-4o","gemini/gemini-2.0-flash","groq/llama-3.1-8b-instant"],
                    "general" : ["groq/openai/gpt-oss-20b"]
                    }
        model = routing.get(task,routing["general"])
        return model

    def generate_response(self):
        message = [{"role" : "user" , "content":self.prompt}]

        start_time = time.time()
        try:
            # FIX: wrap the upstream call so a provider error becomes a clean,
            # readable message instead of an unhandled 500 traceback.
            response = completion(
                model=self.primary_model,
                messages=message,
                fallbacks=self.task_model()
            )
        except Exception as e:
            end_time = time.time()
            latency = end_time - start_time
            return [f"Error generating response: {str(e)}", latency, 0, 0, self.primary_model, 500]
 
        end_time = time.time()
 
        generate_ans = response.choices[0].message.content
        latency = end_time - start_time
        completion_tokens = response.usage.completion_tokens
        prompt_token = response.usage.prompt_tokens
        used_model = response.model
        status_cod = 200
 
        return [generate_ans, latency, prompt_token, completion_tokens, used_model, status_cod]
 