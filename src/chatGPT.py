from openai import OpenAI

class AIAssistant:
    
    def __init__(self, key_path):
        with open(key_path, "r") as file:
            self.key = file.read()
        
        self.client = OpenAI(api_key=self.key)
    
        self.max_tokens = 8192   # maximum tokens
        
    def JsonFormatSummary(self, text):
        text_to_send = text[:self.max_tokens - 50]  # leave some space before the end
        
        completion = self.client.chat.completions.create(
            model="ft:gpt-4o-mini-2024-07-18:personal::ADQS8DsH",
            messages=[
                {"role": "system", "content": "You are a helpful home assistant."},
                {"role": "user", "content": f"{text_to_send}"}
            ]
        )
        
        return completion.choices[0].message.content