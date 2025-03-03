import requests
from bs4 import BeautifulSoup
from django.shortcuts import render
from django.http import JsonResponse
from openai import OpenAI
import os

from dotenv import load_dotenv

# Cargar variables de entorno desde .env
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path,override=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY").strip()

client = OpenAI(api_key=str(OPENAI_API_KEY))

def extract_text_from_url(url):
    print("extract text")
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        text = '\n'.join([p.get_text() for p in paragraphs])
        return text
    
    return "Error al obtener contenido"


def summarize_text(text):
    """Resume el texto en fragmentos y los une en un solo resumen."""
    summaries = []
    print(f"API Key: {OPENAI_API_KEY}, Tipo: {type(OPENAI_API_KEY)}")
    mensaje = [{"role": "system", "content": "Summarize the following text concisely."}]
    mensaje.append({"role": "user", "content": text})
    response = client.chat.completions.create(
                model = "gpt-4o-mini",
                messages=mensaje,
                #temperature = 0 
                )
    summaries.append(response.choices[0].message.content)
    return summaries

def summarize(request):
    if request.method == 'POST':
        print("intentando")
        url = request.POST.get('url')
        if not url:
            return JsonResponse({'error': 'No URL provided'}, status=400)
        
        text = extract_text_from_url(url)
        if text.startswith("Error"):
            return JsonResponse({'error': text}, status=400)
        summary = summarize_text(text)
        return JsonResponse({'summary': summary})
    
    return render(request, 'summarizer_app/index.html')