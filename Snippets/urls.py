from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from MainApp import views

urlpatterns = ([
                   path('', views.index_page, name='home'),
                   path('snippets/add', views.add_snippet_page, name='add_snippet'),
                   path('comment/add/<int:snippet_id>', views.comment_add, name="comment_add"),
                   path('snippets/list', views.snippets_page, name='snippets_list'),
                   path('snippet/<int:snippet_id>', views.snippet_detail, name='snippet-detail',
                        kwargs={'edit': False}),
                   path('snippet/<int:snippet_id>/edit', views.snippet_detail, name='snippet-edit',
                        kwargs={'edit': True}),
                   path('comment/<int:comment_id>/edit', views.comment_edit, name='comment-edit'),
                   path('snippet/<int:snippet_id>/save', views.snippet_save, name='snippet-save'),
                   path('comment/<int:comment_id>/save', views.comment_save, name='comment-save'),
                   path('snippet/<int:snippet_id>/delete', views.snippet_delete, name='snippet-delete'),
                   path('comment/<int:comment_id>/delete', views.comment_delete, name='comment-delete'),
                   path('snippet/search', views.snippet_search, name='snippet-search'),
                   path('login', views.login, name='login'),
                   path('logout', views.logout, name='logout'),
                   path('auth/register', views.create_user, name='register'),
                   path('admin/', admin.site.urls)
               ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
               + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT))
