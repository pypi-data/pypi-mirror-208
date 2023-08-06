from django.http import JsonResponse
from django.conf import settings


def check_view(request):
    if request.method == 'GET':
        return JsonResponse({'message': settings.TWILIO_ACCOUNT_SID})
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
