from django.shortcuts import render
from django.shortcuts import redirect
import datetime
import hashlib
import json
from uuid import uuid4
import socket
from urllib.parse import urlparse
from django.http import JsonResponse, HttpResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
import requests
import random
from Blockchain import Blockchain
from Acc_Blockchain import Acc_Blockchain
from random import randint
import threading
from .forms import Roll_noForm, OTPForm, CandidateForm
from django.core.mail import send_mail
import time

rblockchain = Acc_Blockchain()

# Add Candidates Here

rblockchain.add_cad("Adam")
rblockchain.add_cad("Eve")
rblockchain.add_cad("John")


                 ##############################################################
                 ##################### Blockchain Web Functions ###############
                 ##############################################################

@csrf_exempt
def add_vote(request):
    if request.method == 'POST':
        data_json = json.loads(request.body)
        vote_keys = ['roll_no', 'cad']
        if not all(key in data_json for key in vote_keys):
            return 'Some keys are unaccounted try again', HttpResponse(status=204)

        group = rblockchain.which_group(data_json['roll_no'])
        year = rblockchain.which_year(data_json['roll_no'])
        already_voted = rblockchain.is_valid_roll(group, year, data_json['roll_no'])
        if not already_voted:
            return redirect('doubleVoting')
        added = rblockchain.add_tem_acc(group, year, data_json['roll_no'], data_json['cad'])
        rblockchain.vote_to_cad_buffer(data_json['cad'])
        rblockchain.alert_network(data_json['roll_no'], data_json['cad'])
        response = {'Message': f'The newly casted is now stored in buffer of blockchain {added}'}
        rblockchain.otp = None
        rblockchain.new_roll_no = None
        return JsonResponse(response)
    else:
        redirect('index')


@csrf_exempt
def mine_block(request):
    return redirect('index')
    if request.method == 'GET':
        rblockchain.mine_Acc()
        rblockchain.print_chain()
        response = {'Message': 'A block is mined!'}
        return JsonResponse(response)


@csrf_exempt
def connect_node(request):
    if request.method == 'POST':
        data_json = json.loads(request.body)
        nodes = data_json.get('nodes')
        if nodes is None:
            return "No node", HttpResponse(status=204)
        for node in nodes:
            rblockchain.add_node(node)
        response = {'Message': 'All the given nodes are now connected. Blockchain now connected to the following nodes:',
                    'Nodes': list(rblockchain.nodes)}
        rblockchain.otp = None
        rblockchain.new_roll_no = None
        return JsonResponse(response)


@csrf_exempt
def has_vote(request):
    data_json = json.loads(request.body)
    print(data_json['roll_no'], data_json['cad'])
    vote_keys = ['roll_no', 'cad']
    if not all(key in data_json for key in vote_keys):
        return 'Some keys are unaccounted try again', HttpResponse(status=204)
    present = rblockchain.has_vote(data_json['roll_no'], data_json['cad'])
    if present:
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=201)


@csrf_exempt
def has_roll(request):
    return render(request, 'DoubleVoting.html')


@csrf_exempt
def no_of_votes(request):

    if len(rblockchain.new_acc) >= 3:
        return HttpResponse(status=200)

    return HttpResponse(status=201)


@csrf_exempt
def send_data(request):
    if request.method == 'POST':
        data_json = json.loads(request.body)
        print(data_json['roll_no'], data_json['cad'])
        vote_keys = ['roll_no', 'cad']
        if not all(key in data_json for key in vote_keys):
            return 'Some keys are unaccounted try again', HttpResponse(status=204)
        present = rblockchain.has_vote(data_json['roll_no'], data_json['cad'])
        if present:
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=201)


@csrf_exempt
def check_blockchain(request):
    if request.method == 'POST':
        data_json = json.loads(request.body)
        our_json = rblockchain.to_json()
        if our_json == data_json:
            return HttpResponse(status=201)
        else:
            return HttpResponse(status=200)


@csrf_exempt
def print_chain(request):
       rblockchain.print_chain()
       rblockchain.otp = None
       rblockchain.new_roll_no = None
       return redirect('index')


                 ##############################################################
                 ##################### Web Pages ##############################
                 ##############################################################

@csrf_exempt
def index(request):
    if request.method == 'GET':
        return render(request, 'Index.html')
    else:
        form = Roll_noForm(request.POST)
        if form.is_valid():
            print("Form Print Roll_no ",form.cleaned_data['Roll_no'])
            group = rblockchain.which_group(form.cleaned_data['Roll_no'])
            year = rblockchain.which_year(form.cleaned_data['Roll_no'])
            already_voted = rblockchain.is_valid_roll(group, year, form.cleaned_data['Roll_no'])
            if not already_voted:
                return redirect('doubleVoting')
            rblockchain.new_roll_no = form.cleaned_data['Roll_no']
        return redirect('otpPage')


@csrf_exempt
def otpPage(request):
    if rblockchain.new_roll_no == None:
        return redirect('index')
    if request.method == "GET":
        if len(rblockchain.new_roll_no) > 1:
            print("Voter ", rblockchain.new_roll_no)
            rblockchain.otp = randint(100000, 999999)
            print("OTP is " , rblockchain.otp)
            send_mail(
                'OTP for eVoting',
                'OTP for the voting application is ' + str(rblockchain.otp),
                'jaswanth.iitgoa@gmail.com',
                ['fivoso9310@isecv.com'],
                fail_silently=False,
            )
            return render(request, 'otpPage.html')
    else:
        form = OTPForm(request.POST)
        if form.is_valid():
            print("OTP entered is ", form.cleaned_data['OTP'])
            if str(rblockchain.otp) == form.cleaned_data['OTP']:
                return redirect('votingPage')
            else:
                response = {'Message': 'The OTP entered is incorrect, Please try again from beginning'}
                rblockchain.otp = None
                rblockchain.new_roll_no = None
                return JsonResponse(response)


@csrf_exempt
def votingPage(request):
    if rblockchain.otp == None or rblockchain.new_roll_no == None:
        print("Hi")
        return redirect('index')
    if request.method == "GET":
        return render(request, 'VotingPage.html')
    else:
        form = CandidateForm(request.POST)
        if form.is_valid():
            print("Candidate is ", form.cleaned_data['CAD'])
            info_json = {'roll_no': str(rblockchain.new_roll_no), 'cad': str(form.cleaned_data['CAD'])}
            node_address = request.get_host()
            requests.post(f'http://{node_address}/add_vote', json=info_json)
            rblockchain.otp = None
            rblockchain.new_roll_no = None
            return render(request, 'Success.html')


@csrf_exempt
def doubleVoting(request):
    rblockchain.otp = None
    rblockchain.new_roll_no = None
    return render(request, 'DoubleVoting.html')


@csrf_exempt
def votingSuccess(request):
    rblockchain.otp = None
    rblockchain.new_roll_no = None
    return render(request, 'DoubleVoting.html')



        ########################### Mine and Validation ###################################

def final_miner():
    mined = rblockchain.mine_Acc()
    if mined:
        rblockchain.alert_network_mine()

        valid = rblockchain.validation()
        if valid:
            print("Valid Blockchain")

        time.sleep(5)

        valid = rblockchain.valid_v2()
        if valid:
            print("Same as others")

    threading.Timer(5.0, final_miner).start()
    return None


final_miner()

