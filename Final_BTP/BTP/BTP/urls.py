from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from django.urls import include
from eVoting import views
from eVoting.views import *

urlpatterns = [

    # Web Page Functions

    path('admin/', admin.site.urls),
    url('^index$', views.index, name="index"),
    url('^otpPage$', views.otpPage, name="otpPage"),
    url('^votingPage$', views.votingPage, name="votingPage"),
    url('^doubleVoting$', views.doubleVoting, name="doubleVoting"),

    # Functions for real blockchain

    url('^add_vote$', views.add_vote, name="add_vote"),
    url('^mine_block$', views.mine_block, name="mine_block"),
    url('^has_vote$', views.has_vote, name="has_vote"),
    url('^connect_node$', views.connect_node, name="connect_node"),
    url('^no_of_votes$', views.has_vote, name="no_of_votes"),
    url('^check_blockchain$', views.check_blockchain, name="check_blockchain"),
    url('^print_chain$', views.print_chain, name="print_chain"),

]
