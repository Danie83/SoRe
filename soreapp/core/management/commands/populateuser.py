import os
import json
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import UserProfile

class Command(BaseCommand):
    help = 'Import users from a file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the file containing usernames')

    def handle(self, *args, **options):
        file_path = options['file_path']

        if not os.path.isfile(file_path):
            self.stderr.write(self.style.ERROR(f"File not found at path: {file_path}"))
            return

        with open(file_path, 'r') as file:
            count = 0
            for line in file:
                try:
                    user_data = json.loads(line)
                    username = user_data.get('accountName')

                    if not username:
                        self.stderr.write(self.style.ERROR(f"Username not found in JSON: {line}"))
                        continue
                        
                    if '.' in username:
                        self.stdout.write(self.style.WARNING(f"User {username} is invalid."))
                        continue

                    if not User.objects.filter(username=username).exists():
                        user = User.objects.create_user(username=username, password="user")
                        user.save()
                        profile = UserProfile.objects.get(user=user)
                        profile.setup_complete = True
                        profile.save()
                        count += 1

                        self.stdout.write(self.style.SUCCESS(f"User {username} created successfully. {count}"))
                    else:
                        self.stdout.write(self.style.WARNING(f"User {username} already exists."))
                        break
                except json.JSONDecodeError as e:
                    self.stderr.write(self.style.ERROR(f"Error decoding JSON: {e}"))