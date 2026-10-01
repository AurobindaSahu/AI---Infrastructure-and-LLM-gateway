import sqlite3
from curd import api_logs, prompt
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from generate import llm_responce
from pydantic import BaseModel
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()


def get_prompt_from_db(name: str, version: str | None = None):
  conn = sqlite3.connect("database.db")
  cursor = conn.cursor()

  if version:
    cursor.execute(
        """
            SELECT id, name, version, template_text, created_at 
            FROM prompts 
            WHERE name = ? AND version = ?
        """,
        (name, version),
    )
  else:
    cursor.execute(
        """
            SELECT id, name, version, template_text, created_at 
            FROM prompts 
            WHERE name = ? 
            ORDER BY id DESC 
            LIMIT 1
        """,
        (name,),
    )

  row = cursor.fetchone()
  conn.close()
  return row


def get_next_version(name: str) -> str:
  conn = sqlite3.connect("database.db")
  cursor = conn.cursor()
  cursor.execute(
      "SELECT version FROM prompts WHERE name = ? ORDER BY id DESC LIMIT 1",
      (name,),
  )
  row = cursor.fetchone()
  conn.close()

  if not row:
    return "v1"

  last_version = row[0]
  if last_version.startswith("v") and last_version[1:].isdigit():
    num = int(last_version[1:]) + 1
    return f"v{num}"
  else:
    return "v2"


@app.get("/prompts")
async def get_all_prompts():
  conn = sqlite3.connect("database.db")
  cursor = conn.cursor()
  cursor.execute(
      "SELECT id, name, version, template_text, created_at FROM prompts ORDER"
      " BY id DESC"
  )
  rows = cursor.fetchall()
  conn.close()

  prompts_list = [
      {
          "id": r[0],
          "name": r[1],
          "version": r[2],
          "template_text": r[3],
          "created_at": r[4],
      }
      for r in rows
  ]
  return {"status": "success", "data": prompts_list}


@app.get("/analytics/logs")
async def get_api_logs():
  conn = sqlite3.connect("database.db")
  cursor = conn.cursor()
  cursor.execute(
      "SELECT id, timestamp, requested_model, actual_model_used,"
      " prompt_tokens, completion_tokens, latency_ms, status_code FROM api_logs"
      " ORDER BY id DESC LIMIT 50"
  )
  rows = cursor.fetchall()
  conn.close()

  logs_list = [
      {
          "id": r[0],
          "timestamp": r[1],
          "requested_model": r[2],
          "actual_model_used": r[3],
          "prompt_tokens": r[4],
          "completion_tokens": r[5],
          "latency_ms": r[6],
          "status_code": r[7],
      }
      for r in rows
  ]
  return {"status": "success", "data": logs_list}


@app.get("/prompt/{name}")
async def get_prompt(name: str, version: str | None = Query(default=None)):
  result = get_prompt_from_db(name=name, version=version)
  if not result:
    raise HTTPException(
        status_code=404, detail=f"Prompt '{name}' version '{version}' not found"
    )

  prompt_id, prompt_name, prompt_version, prompt_template, create_at = result
  return {
      "status": "success",
      "data": {
          "id": prompt_id,
          "name": prompt_name,
          "version": prompt_version,
          "prompt": prompt_template,
      },
  }


@app.post("/prompts/create")
async def receive_query_input(name: str, template_text: str):
  # Calculate auto-incremented version (v1, v2, v3...)
  next_ver = get_next_version(name)

  new_prompt = prompt(name=name, version=next_ver, template_text=template_text)
  new_prompt.save()
  return {
      "status": "success",
      "message": f"Prompt saved as {name} with version {next_ver}",
      "version": next_ver,
  }


@app.post("/{name}/chat")
async def requive_query_input(requested_model: str, prompt: str):
  query_input = llm_responce(prompt=prompt, primary_model=requested_model)
  query_output = query_input.generate_response()
  generate_ans, latency, prompt_token, completion_tokens, used_model, status_cod = (
      query_output
  )

  new_api_input = api_logs(
      requested_model=requested_model,
      actual_model_used=used_model,
      prompt_tokens=prompt_token,
      completion_tokens=completion_tokens,
      latency_ms=round(latency, 3),
      status_cod=status_cod,
  )
  new_api_input.save()

  return {
      "status": "success",
      "data": {
          "message": generate_ans,
          "time": round(latency, 3),
          "prompt tokens": prompt_token,
          "complection": completion_tokens,
          "model": used_model,
      },
  }


if __name__ == "__main__":
  uvicorn.run(app, host="127.0.0.1", port=8000)