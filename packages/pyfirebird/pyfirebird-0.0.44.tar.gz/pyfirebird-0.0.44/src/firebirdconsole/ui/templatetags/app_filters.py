from django import template
import json

register = template.Library()


# convert object to json
@register.filter(name='user_to_json')
def user_to_json(user):
    if not user.is_authenticated:
        payload = {
            'is_authenticated': False
        }
    else:
        payload = {
            'is_authenticated': True,
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser
        }
    return json.dumps(payload)
