import sqlite3



class prompt:
  def __init__(self,name, version, template_text):
    self.name = name
    self.version = version
    self.template_text = template_text

  def save(self):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor() 

    cursor.execute('''
        INSERT INTO prompts (name, version, template_text)
        VALUES (?, ?, ?)
    ''', (self.name, self.version, self.template_text))
    conn.commit()

class api_logs:
  def __init__(self,requested_model, actual_model_used, prompt_tokens, completion_tokens, latency_ms, status_cod):
    self.requested_model = requested_model
    self.actual_model_used = actual_model_used
    self.prompt_tokens = prompt_tokens
    self.completion_tokens = completion_tokens
    self.latency_ms = latency_ms
    self.status_cod = status_cod    
  
  def save(self):
    
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor() 

    cursor.execute('''
        INSERT INTO api_logs (requested_model, actual_model_used, prompt_tokens, completion_tokens, latency_ms, status_code)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (self.requested_model, self.actual_model_used, self.prompt_tokens, self.completion_tokens, self.latency_ms, self.status_cod))
    conn.commit()