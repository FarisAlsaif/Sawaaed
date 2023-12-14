import os
import argparse
import threading
import rticonnextdds_connector as rti
import random
from datetime import datetime
from posixpath import split
from time import sleep

from os import error, path as os_path

file_path = os_path.dirname(os_path.realpath(__file__))

parser = argparse.ArgumentParser(description='DDS KFUPM Sawaed')
# take arguments 
parser.add_argument('user', help='User name', type=str)
parser.add_argument('building', help='building number', type=str)
parser.add_argument('content', help='breif discription of offer', type=str)

args = parser.parse_args()

###enviroment varible (to applay filter)
os.environ['username'] = str(args.user)


lock = threading.RLock()
finish_thread = False

def user_subscriber_task(user_input):
    global finish_thread

    while finish_thread == False:
        try:
            user_input.wait(500)
        except rti.TimeoutError as error:
            continue

        with lock:
            user_input.read()
            for sample in user_input.samples:
                if (sample.info['sample_state'] == 'NOT_READ') and (sample.valid_data == False) and (sample.info['instance_state'] == 'NOT_ALIVE_NO_WRITERS'):
                    print("User: " + sample.get_string("username") +" Request: " + sample.get_string("userrequestcontent")+" - Not avilivale any more!")

def user_offer_subscriber_task(user_offer_input):
    global finish_thread

    while finish_thread == False:
        try:
            user_offer_input.wait(500)
        except rti.TimeoutError as error:
            continue

        with lock:
            user_offer_input.read()
            for sample in user_offer_input.samples:
                if (sample.info['sample_state'] == 'NOT_READ') and (sample.valid_data == False) and (sample.info['instance_state'] == 'NOT_ALIVE_NO_WRITERS'):
                    print("User: " + sample.get_string("username")  +" Offer: " + sample.get_string("useroffercontent")+" - Not avilivale any more!")

def message_subscriber_task(message_input):
    global finish_thread

    while finish_thread == False:
        try:
            message_input.wait(500)
        except rti.TimeoutError as error:
            continue

        with lock:
            message_input.take()
            for sample in message_input.samples.valid_data_iter:
                print("From: " + sample.get_string("fromuser") + " - " + sample.get_string("usermsg"))

def command_task(user, message_output, user_input, user_offer_input):
    global finish_thread

    while finish_thread == False:
        command = input("\nEnter command: ")
        if command == "exit":
            finish_thread = True
        elif command == "list":
            with lock:
                user_input.read()
                for sample in user_input.samples.valid_data_iter:
                    if sample.info['instance_state'] == 'ALIVE':
                        print("User: "+ sample.get_string("username")+" Building: "+ sample.get_string("userrequestbuilding") +" Request a "+sample.get_string("userrequestcontent"))
                        user_offer_input.read()
                for sample in user_offer_input.samples.valid_data_iter:
                    if sample.info['instance_state'] == "ALIVE":
                        print("User: " + sample.get_string("username") + " - Building: " + sample.get_string("userofferbuildign") + " Offer a "+sample.get_string("useroffercontent"))
                        
        elif command.startswith("send"):
            destination = command.split(maxsplit=2)
            if len(destination) == 3:
                with lock:
                    message_output.instance.set_string("fromuser", user)
                    message_output.instance.set_string("touser", destination[1])
                    message_output.instance.set_string("usermsg", destination[2])   

                    message_output.write()
            else:
                print("Wrong usage: Use \"send user message\"\n")  
        else:
            print("Unknown command")

with rti.open_connector(
    config_name = "KFUPM_ParticipantLibrary::KFUPM_Participant",
    url="http://3.123.24.195/FinalProject.xml") as connector:
##
    user_output = connector.get_output("RequestTypePublisher::userrequestinfoTopicWriter")
    message_output = connector.get_output("UserMsgPublisher::msginfoTopicWriter")

    user_input = connector.get_input("RequestTypeSubscriber::userrequestinfoTopicReader")
    message_input = connector.get_input("UserMsgSubscriber::msginfoTopicReader")

    user_offer_input = connector.get_input("OfferTypeSubscriber::userofferinfoTopicReader")
###
    user_output.instance.set_string("username", args.user)
    user_output.instance.set_string("userrequestbuilding", args.building)
    user_output.instance.set_string("userrequestcontent", args.content)



    user_output.write()

    t1 = threading.Thread(target=command_task, args=(args.user, message_output, user_input, user_offer_input,))
    t1.start()

    t2 = threading.Thread(target=message_subscriber_task, args=(message_input,))   
    t2.start()

    t3 = threading.Thread(target=user_subscriber_task, args=(user_input,))
    t3.start()

    t4 = threading.Thread(target=user_offer_subscriber_task, args=(user_offer_input,))
    t4.start()

    t1.join()
    t2.join()
    t3.join()
    t4.join()


    #unregister
    user_output.instance.set_string("username", args.user)
    user_output.write(action="unregister")
