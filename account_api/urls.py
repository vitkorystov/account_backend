from django.urls import path
from .views import AccountsViewSet, AddView, PingView, SubtractView, StatusView, SubtractHoldView
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'accounts', AccountsViewSet)

urlpatterns = router.urls
urlpatterns.append(path('add/', AddView.as_view()))
urlpatterns.append(path('ping/', PingView.as_view()))
urlpatterns.append(path('substract/', SubtractView.as_view()))
urlpatterns.append(path('status/', StatusView.as_view()))
urlpatterns.append(path('hold/', SubtractHoldView.as_view()))
