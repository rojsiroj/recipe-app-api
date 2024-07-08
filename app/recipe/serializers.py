from django.utils.translation import gettext as _
from rest_framework import serializers

from core.models import Recipe


class RecipeSerializer(serializers.ModelSerializer):
    # Serializer for the user object
    class Meta:
        model = Recipe
