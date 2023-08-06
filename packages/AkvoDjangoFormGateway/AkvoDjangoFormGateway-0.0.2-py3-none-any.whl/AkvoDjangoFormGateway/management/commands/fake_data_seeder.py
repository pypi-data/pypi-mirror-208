from django.core.management import BaseCommand
from AkvoDjangoFormGateway.models import AkvoGatewayData as FormData
from AkvoDjangoFormGateway.utils.functions import seed_data


class Command(BaseCommand):
    help = "Command to generate fake data for data & answer as test purpose"

    def add_arguments(self, parser):
        parser.add_argument(
            "-r", "--repeat", nargs="?", const=20, default=20, type=int
        )
        parser.add_argument(
            "-t", "--test", nargs="?", const=False, default=False, type=bool
        )

    def handle(self, *args, **options):
        test = options.get("test")
        repeat = options.get("repeat")
        FormData.objects.all().delete()
        seed_data(repeat=repeat, test=test)
