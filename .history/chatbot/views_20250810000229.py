import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Complaint

@csrf_exempt
def submit_complaint(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            complaint_text = data.get("complaint", "").strip()

            if not complaint_text:
                return JsonResponse({"status": "error", "message": "Complaint cannot be empty."}, status=400)

            Complaint.objects.create(message=complaint_text)

            return JsonResponse({"status": "success", "message": "Complaint saved successfully."})
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON."}, status=400)

    return JsonResponse({"status": "error", "message": "Only POST method allowed."}, status=405)
