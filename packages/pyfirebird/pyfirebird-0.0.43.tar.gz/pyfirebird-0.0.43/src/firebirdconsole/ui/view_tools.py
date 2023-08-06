from django.shortcuts import render
import json

def render_application(request, *, 
    scripts, sub_title, app_context=None, init_menu_key=None,
    status=200
):
    context={
        'user': request.user,
        'scripts': scripts,
        'sub_title': sub_title
    }

    if app_context is not None:
        context['app_context'] = json.dumps(app_context)
    
    if init_menu_key is not None:
        context['init_menu_key'] = init_menu_key

    return render(
        request,
        'application.html',
        context=context,
        status=status
    )

