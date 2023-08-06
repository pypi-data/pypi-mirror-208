# from django.
from rest_framework import serializers
from .models import (
    AkvoGatewayForm,
    AkvoGatewayQuestion,
    AkvoGatewayQuestionOption,
    AkvoGatewayData,
    AkvoGatewayAnswer,
)
from .constants import QuestionTypes
from .utils.functions import get_answer_value


class CheckSerializer(serializers.Serializer):
    id = serializers.IntegerField(default=1)
    check = serializers.CharField(default="OK")


class ListFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = AkvoGatewayForm
        fields = ['id', 'name', 'description', 'version']


class ListOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AkvoGatewayQuestionOption
        fields = ['id', 'name', 'order']


class ListQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AkvoGatewayQuestion
        fields = ['id', 'form', 'order', 'text']


class ListDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = AkvoGatewayData
        fields = '__all__'


class ListDataAnswerSerializer(serializers.ModelSerializer):
    value = serializers.SerializerMethodField()

    class Meta:
        model = AkvoGatewayAnswer
        fields = ['question', 'value']

    def get_value(self, instance: AkvoGatewayAnswer):
        return get_answer_value(instance)


class QuestionDefinitionSerializer(serializers.ModelSerializer):
    question_type = serializers.SerializerMethodField()
    options = serializers.SerializerMethodField()

    class Meta:
        model = AkvoGatewayQuestion
        fields = ['id', 'text', 'required', 'question_type', 'options']

    def get_question_type(self, obj):
        return QuestionTypes.FieldStr.get(obj.type)

    def get_options(self, instance):
        options = (
            [
                options.name
                for options in instance.ag_question_question_options.all()
            ]
            if instance.ag_question_question_options.count()
            else None
        )
        return options
