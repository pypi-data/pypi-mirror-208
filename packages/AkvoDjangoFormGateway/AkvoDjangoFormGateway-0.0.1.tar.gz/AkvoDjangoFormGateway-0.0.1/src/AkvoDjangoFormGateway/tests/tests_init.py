from django.test import TestCase, Client
from django.conf import settings


class CheckInitialEndpointTestCase(TestCase):
    def test_check_endpoint(self):
        client = Client()

        # Allow GET
        response = client.get("/api/gateway/check/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(), {"message": settings.TWILIO_ACCOUNT_SID}
        )

        # Allow GET
        response = client.post("/api/gateway/check/")
        self.assertEqual(response.status_code, 405)
