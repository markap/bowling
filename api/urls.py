from django.conf.urls import url
from api import views

urlpatterns = [
	url('new/', views.CreateGameView.as_view(), name='new'),
	url('add/', views.AddScoreView.as_view(), name='add'),
	url('result/', views.GameResultView.as_view(), name='result'),
]
