from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.http import HttpResponse as HR
from google.cloud import storage
import cloudstorage
import os


def index(request):
	os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="SAFEWheel-e3260c10b7e8.json"
	project = 'safewheel-219707'
	storage_client = storage.Client(project=project)
	bucket = storage_client.get_bucket('safewheel_data')

	eye_time = bucket.blob('Eye Time').download_as_string()
	eye_time = eye_time.decode('utf-8')
	eye_count = str(len(eye_time.split('|')[1:]))
	eye_time = str(eye_time.split('|')[1:])

	hand_time = bucket.blob('Hand Time').download_as_string()
	hand_time = hand_time.decode('utf-8')
	hand_count = str(len(hand_time.split('|')[1:]))
	hand_time = str(hand_time.split('|')[1:])
	
	context = {'eye_time' : eye_time,'hand_time': hand_time, 'eye_count': eye_count, 'hand_count': hand_count}
	#return render(request, 'safewheel/index.html', context)
	return render(request, 'safewheel/text.html', context)
