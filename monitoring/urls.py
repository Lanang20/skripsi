from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("login_view/", views.login_view, name="login_view"),
    path('kemantren/', views.daftar_kemantren, name='daftar_kemantren'),
    path('kemantren/tambah/', views.tambah_kemantren, name='tambah_kemantren'),
    path('kemantren/edit/<int:id>/', views.edit_kemantren, name='edit_kemantren'),
    path('kemantren/hapus/<int:id>/', views.hapus_kemantren, name='hapus_kemantren'),
    path('bendung/', views.daftar_bendung, name='daftar_bendung'),
    path('bendung/tambah/', views.tambah_bendung, name='tambah_bendung'),
    path('bendung/edit/<int:id>/', views.edit_bendung, name='edit_bendung'),
    path('bendung/hapus/<int:id>/', views.hapus_bendung, name='hapus_bendung'),
    path('role/', views.role_list, name='role_list'),
    path('role/tambah/', views.tambah_role, name='tambah_role'),
    path('role/edit/<int:id>/', views.edit_role, name='edit_role'),
    path('role/hapus/<int:id>/', views.hapus_role, name='hapus_role'),
    path('user_list', views.user_list_view, name='user_list'),
    path('user/tambah/', views.tambah_user, name='tambah_user'),
    path('user/edit/<int:id>/', views.edit_user, name='edit_user'),
    path('user/hapus/<int:user_id>/', views.hapus_user, name='hapus_user'),
    path('debit_air/', views.daftar_debit_air, name='debit_air'),
    path('debit_air/tambah/', views.tambah_debit_air, name='tambah_debit_air'),
    path('debit-air/edit/<int:id>/', views.edit_debit_air, name='edit_debit_air'),
    path('debit-air/hapus/<int:id>/', views.hapus_debit_air, name='hapus_debit_air'),
    path('debit-air/cetak/', views.cetak_debit_air_pdf, name='cetak_debit_air_pdf'),
    path("logout_view/", views.logout_view, name="logout_view"),
    path("logout_session/", views.logout_session, name="logout_session"),
]