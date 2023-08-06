from django.test import TestCase
from AkvoDjangoFormGateway.models import AkvoGatewayForm as Forms
from AkvoDjangoFormGateway.models import AkvoGatewayQuestion as Questions
from AkvoDjangoFormGateway.models import AkvoGatewayQuestionOption as QO
from AkvoDjangoFormGateway.serializers import (
    ListQuestionSerializer,
    ListOptionSerializer,
    QuestionDefinitionSerializer,
)
from AkvoDjangoFormGateway.constants import QuestionTypes


class QuestionSerializerTestCase(TestCase):
    def setUp(self):
        form = Forms.objects.create(
            name='Test form', description='Test description'
        )
        self.question_attributes = {
            'form': form,
            'text': 'Question #1',
            'type': QuestionTypes.text,
        }

        self.question = Questions.objects.create(**self.question_attributes)
        self.serializer = ListQuestionSerializer(instance=self.question)

    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertCountEqual(
            set(data.keys()),
            set(['id', 'form', 'order', 'text']),
        )

    def test_text_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['text'], self.question_attributes['text'])
        self.assertEqual(str(self.question), self.question.text)

    def test_option_field_content(self):
        self.question_attributes['type'] = QuestionTypes.option
        for opt in ['Yes', 'No']:
            QO.objects.create(question=self.question, name=opt)
        serializer = QuestionDefinitionSerializer(
            instance=self.question,
            data=self.question_attributes,
        )
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.assertEqual('Yes' in serializer.data['options'], True)

        option = QO.objects.get(name="Yes")
        self.assertEqual(str(option), option.name)

        serializer = ListOptionSerializer(instance=option)
        self.assertEqual(serializer.data['name'], 'Yes')

    def test_type_must_be_in_choices(self):
        self.question_attributes['type'] = QuestionTypes.geo
        self.question.type = self.question_attributes['type']
        self.question.save()
        serializer = QuestionDefinitionSerializer(
            instance=self.question, data=self.question_attributes
        )
        self.assertTrue(serializer.is_valid())
        self.assertEqual(
            serializer.data['question_type'],
            QuestionTypes.FieldStr.get(QuestionTypes.geo),
        )
