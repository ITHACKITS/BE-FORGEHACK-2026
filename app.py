"""
app.py - Entrypoint untuk Hugging Face Spaces (Gradio + FastAPI).
Menjalankan seluruh REST API UdaraSiaga / StandbAI di port 7860.
"""

import sys
import os
from pathlib import Path

# Pastikan path modul terbaca dengan benar
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

import gradio as gr
import uvicorn
from app.main import app

# Buat antarmuka status interaktif sederhana dengan Gradio
with gr.Blocks(title="StandbAI Indonesia API") as demo:
    gr.Markdown("# 🌋 StandbAI Indonesia (UdaraSiaga) Backend API")
    gr.Markdown("""
    **Backend Server is LIVE & OPERATIONAL (24/7 on Hugging Face Spaces)**
    
    - 📖 **Interactive API Documentation:** [/docs](/docs)
    - ⚡ **Health Check Endpoint:** [/api/v1/health](/api/v1/health)
    - 🔍 **OpenAPI JSON Schema:** [/openapi.json](/openapi.json)
    - 🌐 **Frontend App:** [https://fe-forgehack-2026.vercel.app](https://fe-forgehack-2026.vercel.app)
    """)
    with gr.Row():
        status_btn = gr.Button("Check API Status", variant="primary")
        status_output = gr.Textbox(label="Status Response", interactive=False)
        
    def check_status():
        return f"StandbAI API is active! Ready for requests from Frontend."
        
    status_btn.click(check_status, outputs=status_output)

# Pasang demo Gradio ke root FastAPI tanpa mengganggu endpoint REST API lainnya
app = gr.mount_gradio_app(app, demo, path="/")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
