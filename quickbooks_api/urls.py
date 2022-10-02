from django.urls import path, re_path

from . import views

import urllib

from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from django.conf import settings





urlpatterns = [

path('<int:client_acc_id>/', views.connectToQuickbooks,
         name='connectToQuickbooks'),


]
