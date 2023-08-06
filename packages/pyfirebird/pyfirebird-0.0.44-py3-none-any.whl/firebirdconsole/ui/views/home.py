from django.http  import HttpRequest, HttpResponse
from firebirdconsole.ui.view_tools import render_application

def home(request:HttpRequest)->HttpResponse:
    return render_application(
        request, 
        scripts = ['/static/js-bundle/home.js'], 
        sub_title='home'
    )
