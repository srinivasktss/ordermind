import anthropic
from django.conf import settings

CLIENT = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
MODEL = 'claude-haiku-4-5'