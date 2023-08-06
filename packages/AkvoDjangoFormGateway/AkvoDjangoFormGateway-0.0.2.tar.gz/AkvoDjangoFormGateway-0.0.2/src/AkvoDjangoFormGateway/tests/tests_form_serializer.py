from django.test import TestCase
from AkvoDjangoFormGateway.models import AkvoGatewayForm as Forms
from AkvoDjangoFormGateway.serializers import ListFormSerializer


class ListFormSerializerTestCase(TestCase):
    def setUp(self):
        self.form_attributes = {
            'id': 1,
            'name': 'Form #1',
            'description': 'Form #1 description',
        }
        self.form = Forms.objects.create(**self.form_attributes)
        self.serializers = ListFormSerializer(instance=self.form)

    def test_contains_expected_fields(self):
        data = self.serializers.data
        self.assertCountEqual(
            set(data.keys()), set(['id', 'name', 'description', 'version'])
        )

    def test_version_content(self):
        data = self.serializers.data
        self.assertEqual(data['version'], self.form.version)
        self.assertEqual(str(self.form), self.form.name)

    def test_forms_api(self):
        res = self.client.get("/api/gateway/forms/1/?format=json")
        res = res.json()
        self.assertEqual(res["name"], "Form #1")
