from django.conf import settings
from rest_framework.decorators import permission_classes
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import AkvoGatewayForm
from .serializers import ListFormSerializer


@permission_classes([AllowAny])
class CheckView(APIView):
    def get(self, request):
        return Response({"message": settings.TWILIO_ACCOUNT_SID})


class AkvoFormViewSet(ModelViewSet):
    serializer_class = ListFormSerializer
    queryset = AkvoGatewayForm.objects.all()
