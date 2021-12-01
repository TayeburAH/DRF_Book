from django.urls import path, include
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from custom_user.views import CustomUserSignupView, login, logout, CustomUserAccountChange, reset_password_email, reset_password

urlpatterns = [
    # Books
    path('', views.test, name='test'),
    path(r'books/', views.BookView.as_view(), name='books'),
    path('book/<int:book_id>', views.BookChange.as_view(), name='book'),

    # Your Order
    path(r'orders/', views.OrderView.as_view(), name='books'),
    path('order/<slug:order_id>', views.OrderChange.as_view(), name='order'),

    # Login via drf button. Although it shows during JWT it does not work
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    # Auth POST request
    # path('gettoken/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # by refresh token or username and password
    # http://127.0.0.1:8000/api/gettoken/

    # body = {
    #         "username": "Takib",
    #         "password": "1234"
    #       }
    # NO COMMA ON THE LAST ONE
    # Each time username and password is sent, you will get a new access and refresh token

    path('tokenrefresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # Each time refresh token is sent, you will get a new access  token
    # http://127.0.0.1:8000/api/tokenrefresh/
    # refresh token is fixed for 1 day
    # body = {
    #     "refresh": "eyJ0eXAiOiJKV1jt2wrOydHdrG21jfnAVC3V28E"
    # }

    path('tokenverify/', TokenVerifyView.as_view(), name='token_verify'),

    # you can verify both token,
    # if Ture {} is returned
    # if False

    # {
    # "detail": "Token is invalid or expired",
    # "code": "token_not_valid"
    # } is returned

    # body = {
    #     "token": "eyJ0eXAiOiJKV1jt2wrOydHdrG21jfnAVC3V28E"
    # }
    # response.headers.get('status')

    path('signup/', CustomUserSignupView.as_view(), name='customusersignupview'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('change_password/', CustomUserAccountChange.as_view(), name='customUserAccountChange'),
    path('password_reset_email/', reset_password_email, name='reset_password_email'),
    path('password_reset/<uid>/<token>', reset_password, name='reset_password'),

]
