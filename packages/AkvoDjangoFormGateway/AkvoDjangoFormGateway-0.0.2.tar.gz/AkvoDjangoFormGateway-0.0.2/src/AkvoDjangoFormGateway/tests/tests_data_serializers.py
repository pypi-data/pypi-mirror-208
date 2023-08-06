from django.test import TestCase
from AkvoDjangoFormGateway.utils.functions import seed_data
from AkvoDjangoFormGateway.models import (
    AkvoGatewayForm as Forms,
    AkvoGatewayQuestion as Questions,
    AkvoGatewayQuestionOption as QO,
    AkvoGatewayData as FormData,
    AkvoGatewayAnswer as Answers,
)

from AkvoDjangoFormGateway.serializers import (
    ListDataSerializer,
    ListDataAnswerSerializer,
)
from AkvoDjangoFormGateway.constants import QuestionTypes


class DataSerializerTestCase(TestCase):
    def setUp(self):
        form = Forms.objects.create(
            name="Form Test", description="Test description"
        )
        questions = [
            {"question": "Your full name", "type": QuestionTypes.text},
            {
                "question": "Check if any",
                "type": QuestionTypes.multiple_option,
                "options": ["Toilet", "Hand Washing Facilities"],
            },
            {
                "question": "Gender",
                "type": QuestionTypes.option,
                "options": ["Male", "Female"],
            },
            {
                "question": "Date",
                "type": QuestionTypes.date,
            },
            {
                "question": "Gender",
                "type": QuestionTypes.number,
            },
            {
                "question": "Geo",
                "type": QuestionTypes.geo,
            },
        ]
        for q in questions:
            question = Questions.objects.create(
                form=form, text=q["question"], type=q["type"]
            )
            if "options" in q:
                for opt in q["options"]:
                    QO.objects.create(question=question, name=opt)
        seed_data(repeat=2)
        self.data = FormData.objects.all()
        self.data_serializer = ListDataSerializer(instance=self.data.first())

        fd = self.data.first()
        self.answer = Answers.objects.filter(data=fd.id).first()
        self.answer_serializer = ListDataAnswerSerializer(instance=self.answer)

    def test_expected_fields_in_data(self):
        data = self.data_serializer.data
        self.assertCountEqual(
            set(data.keys()),
            set(
                [
                    "id",
                    "name",
                    "form",
                    "geo",
                    "phone",
                    "status",
                    "created",
                    "updated",
                ]
            ),
        )

    def test_expected_fields_in_answer(self):
        data = self.answer_serializer.data
        self.assertCountEqual(set(data.keys()), set(["question", "value"]))
        self.assertEqual(str(self.data.first()), self.data.first().name)

    def test_value_content_in_answer(self):
        data = self.answer_serializer.data
        self.assertEqual(data["value"], self.answer.name)
        self.assertEqual(str(self.answer), self.answer.data.name)
