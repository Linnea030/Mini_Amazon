from django.urls import path

from . import views

urlpatterns = [
    # path('login/', views.login),
    # path('register/',views.register),
    # path('index/', views.index),

    # path('login/', views.loginView),
    # path('reg/', views.regView),
    # path('index/', views.index),
    # path('logout/', views.logout),

    path('', views.homePage, name='home'),
    path('home/', views.homePage, name='home'),
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutPage, name='logout'),
    path('register/', views.registerPage, name='register'),
    path('profile/', views.profilePage, name='user_profile'),
    path('edit_profile/', views.user_edit_page, name='user_edit'),
    path('category/', views.category_page, name='category_page'),
    path('product/<int:cate_id>', views.product_page, name='product_page'),
    path('buy/<int:product_id>', views.buy_page, name='buy'),
    path('buycart/<int:product_id>', views.buy_page1, name='buy1'),
    path('viewOrder/', views.viewOrder, name='viewOrder'),
    path('search/', views.search, name='search'),
    path('addCart/<int:product_id>', views.add_to_cart, name='add_to_cart'),
    path('deleteCart/<int:product_id>', views.delete_cart, name='delete_cart'),
    path('cart/', views.view_cart, name='view_cart')
]