import json
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import urllib.request
import urllib.error

SYSTEM_PROMPT = """Tu es l'assistant virtuel officiel de l'application de Gestion de Matériel 2026. 
Tu es professionnel, courtois, précis et toujours utile. Tu réponds en français.

Ton rôle est double :
1. Expliquer comment utiliser l'application (navigation, fonctionnalités, workflows)
2. Expliquer comment utiliser les matériels gérés dans l'application

== FONCTIONNALITÉS DE L'APPLICATION ==

📦 MATÉRIELS
- Consulter la liste des matériels disponibles (menu "Matériels")
- Voir les détails d'un matériel : nom, description, photo, quantité, état
- Ajouter un nouveau matériel (admin uniquement)
- Modifier ou supprimer un matériel existant

📋 EMPRUNTS
- Faire une demande d'emprunt d'un matériel
- Suivre l'état de sa demande (en attente, approuvé, refusé, retourné)
- Voir l'historique de ses emprunts
- Retourner un matériel emprunté

🏛️ CLUBS
- Consulter la liste des clubs
- Voir les matériels associés à un club
- Gérer les membres d'un club (responsable de club)

👤 COMPTES
- Créer un compte utilisateur
- Se connecter / se déconnecter
- Modifier son profil

📊 TABLEAU DE BORD (DASHBOARD)
- Vue d'ensemble des emprunts en cours
- Statistiques sur les matériels
- Alertes et notifications

Réponds toujours de façon concise, claire et bienveillante."""


@csrf_exempt
@require_http_methods(["POST"])
def chat(request):
    try:
        body = json.loads(request.body)
        messages = body.get("messages", [])

        if not messages:
            return JsonResponse({"error": "Aucun message fourni."}, status=400)

        api_key = os.environ.get("GROQ_API_KEY", "")
        if not api_key:
            return JsonResponse({"error": "Clé API non configurée."}, status=500)

        payload = json.dumps({
            "model": "llama-3.3-70b-versatile",
            "max_tokens": 1024,
            "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + messages
        }).encode("utf-8")

        req = urllib.request.Request(
            "https://api.groq.com/openai/v1/chat/completions",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            },
            method="POST"
        )

        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode("utf-8"))
            reply = data["choices"][0]["message"]["content"]
            return JsonResponse({"reply": reply})

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        return JsonResponse({"error": f"Erreur API: {error_body}"}, status=500)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)