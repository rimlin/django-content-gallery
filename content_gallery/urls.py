from django.urls import path

from . import views

app_name = 'content_gallery'

urlpatterns = [
    # a URL for getting a list of objets of the model
    path(
        '^ajax/choices/<int:pk>/$',
        views.choices,
        name='choices'
    ),
    # a URL for getting data of all images related to the object
    path(
        '^ajax/gallery_data/<str:app_label>/'
        '<str:content_type>)/<int:object_id>)/$',
        views.gallery_data,
        name='gallery_data'
    ),
]
