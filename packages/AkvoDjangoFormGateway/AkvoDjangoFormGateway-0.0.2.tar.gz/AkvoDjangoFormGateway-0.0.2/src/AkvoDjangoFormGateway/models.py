from django.db import models
from .constants import QuestionTypes, StatusTypes


# Create your models here.
class AkvoGatewayForm(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, default=None)
    version = models.IntegerField(default=1)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "ag_form"


class AkvoGatewayQuestion(models.Model):
    form = models.ForeignKey(
        to=AkvoGatewayForm,
        on_delete=models.CASCADE,
        related_name="ag_form_questions",
    )
    order = models.BigIntegerField(null=True, default=None)
    text = models.TextField()
    type = models.IntegerField(choices=QuestionTypes.FieldStr.items())
    required = models.BooleanField(null=True, default=True)

    def __str__(self):
        return self.text

    class Meta:
        db_table = "ag_question"


class AkvoGatewayQuestionOption(models.Model):
    question = models.ForeignKey(
        to=AkvoGatewayQuestion,
        on_delete=models.CASCADE,
        related_name="ag_question_question_options",
    )
    order = models.BigIntegerField(null=True, default=None)
    code = models.CharField(max_length=255, default=None, null=True)
    name = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        db_table = "ag_option"


class AkvoGatewayData(models.Model):
    name = models.TextField()
    form = models.ForeignKey(
        to=AkvoGatewayForm,
        on_delete=models.CASCADE,
        related_name="ag_form_data",
    )
    geo = models.JSONField(null=True, default=None)
    phone = models.CharField(max_length=25)
    status = models.IntegerField(default=StatusTypes.draft)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(default=None, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "ag_data"


class AkvoGatewayAnswer(models.Model):
    data = models.ForeignKey(
        to=AkvoGatewayData,
        on_delete=models.CASCADE,
        related_name="ag_data_answer",
    )
    question = models.ForeignKey(
        to=AkvoGatewayQuestion,
        on_delete=models.CASCADE,
        related_name="ag_question_answer",
    )
    name = models.TextField(null=True, default=None)
    value = models.FloatField(null=True, default=None)
    options = models.JSONField(default=None, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(default=None, null=True)

    def __str__(self):
        return self.data.name

    class Meta:
        db_table = "ag_answer"
