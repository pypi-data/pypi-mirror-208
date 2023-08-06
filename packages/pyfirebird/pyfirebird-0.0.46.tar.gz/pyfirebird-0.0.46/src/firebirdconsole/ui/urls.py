from django.urls import path
from . import views
from .views import apis

urlpatterns = [
    path('', views.home, name='home'),
    path('pipelines/<str:pipeline_id>', views.pipeline, name='pipeline'),

    path('apis/pipelines', apis.list_pipelines, name='api.list_pipelines'),
    path('apis/pipelines/<str:pipeline_id>', apis.get_pipeline, name='api.get_pipeline'),
    path('apis/pipelines/<str:pipeline_id>/executors/<str:id>', apis.EXECUTOR, name='api.executor'),
]
