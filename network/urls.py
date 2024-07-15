
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("newPost", views.newPost, name="newPost"),
    path("profile/<int:user_id>", views.profile, name="profile"),
    path('unfollow/', views.unfollow, name='unFollow'),
    path("follow", views.follow, name="Onfollow"),
    path('following/', views.following, name='following'),
    path("remove_like/<int:post_id>", views.remove_like, name="remove_like"),
    path("add_like/<int:post_id>", views.add_like, name="add_like"),
    path("actualizar_publicacion", views.actualizar_publicacion, name="actualizar_publicacion"),
]
