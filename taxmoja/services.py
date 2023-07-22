
from django.shortcuts import get_object_or_404


def get_model_object_by_id (model, id):
    return get_object_or_404(model, pk=id)
    