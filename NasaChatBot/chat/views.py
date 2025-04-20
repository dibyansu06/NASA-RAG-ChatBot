from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .models import ChatMessage, ChatSession, UploadedDocument
from .forms import UploadedPDFForm
from .rag_utils import embed_pdf

from django.http import JsonResponse
import requests
from .rag_utils import get_rag_response
from .tasks import delete_uploaded_file
from .nasa_api_handler import handler
# Create your views here.
@login_required
def chat_view(request):

    session, _ = ChatSession.objects.get_or_create(user=request.user)
    user_documents = UploadedDocument.objects.filter(user=request.user)
    upload_form = UploadedPDFForm()
    query = ""
    response_text = None

    context_text = None
    handler_output = {
        "apod_title": None,
        "apod_image": None,
        "explanation": None,
        "neows_asteroids": None,
        "earth_image_url": None,
    }

    if request.method == "POST" and request.POST.get("query"):
        query = request.POST.get('query').strip()

        if query:
            ChatMessage.objects.create(session=session, role="user", content=query)
            last_msgs = session.messages.all().order_by("-timestamp")[:6]
            memory = "\n".join(f"{m.role}: {m.content}" for m in reversed(last_msgs))
            
            result = get_rag_response(query, memory=memory, user_id=request.user.id)
            response_text = result.get("response", "")
            context_text = result.get("context", None)

            api_name = result.get('api')
            params = result.get("params", {})
            

            if api_name:
                handler_output = handler(api_name, params)

            ChatMessage.objects.create(session=session, role="bot", content=response_text)

    return render(request, "chat/index.html", {
        "query": query,
        "response": response_text,
        "context": context_text,
        "upload_form": upload_form,
        **handler_output
    })


@login_required
def upload_pdf(request):
    if request.method == "POST":
        form = UploadedPDFForm(request.POST, request.FILES)
        if form.is_valid():
            pdf = form.save(commit=False)
            pdf.user = request.user
            pdf.title = pdf.file.name
            pdf.save()

            embed_pdf(pdf.file.path, user_id=request.user.id)
            delete_uploaded_file.apply_async((pdf.file.path,), countdown=300)
            
            return JsonResponse({"message" : "PDF upload and processed successfully!"})
        return JsonResponse({"message" : "Invalid file."}, status=400)
    
    return JsonResponse({"message" : "Invalid request."}, status=400)
