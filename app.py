# compose_flask/app.py
from flask import Flask
from flask import request

from keras.models import load_model
from slackclient import SlackClient
from lib.vault import Vault
from lib.github import Github
from lib.suggestions import Suggestions
from apscheduler.schedulers.background import BackgroundScheduler

import keras.backend as kb
import keras.backend.tensorflow_backend as tb

import os
import numpy as np
import json
import pickle
import random
import spacy
import requests
import pymsteams
import atexit

app = Flask(__name__)

data_json = 'intents.json'
words_file = 'words.pkl'
tags_file = 'tags.pkl'

intents = json.loads(open(data_json).read())
words = pickle.load(open(words_file, 'rb'))
tags = pickle.load(open(tags_file, 'rb'))

npl = spacy.load('en_core_web_sm')

addr = os.environ['VAULT_ADDR']
token = os.environ['VAULT_TOKEN']

vault = Vault(addr, token)
github = Github()
suggestions = Suggestions()

# Scheduled Tasks
scheduler = BackgroundScheduler()
scheduler.add_job(func=suggestions.suggest_version, trigger="interval", minutes=59)
scheduler.add_job(func=suggestions.adoption_stats, trigger="interval", hours=1)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

def clean_up_sentence(sentence):
    response = []
    for token in npl(sentence):
        if token.lemma_ != "-PRON-":
            response.append(token.lemma_.lower())
        else:
            response.append(token.text.lower())

    return response

# return bag of words array: 0 or 1 for each word in the bag that exists in the sentence
def bow(sentence, words, show_details=False):
    # tokenize the pattern
    sentence_words = clean_up_sentence(sentence)
    # bag of words - matrix of N words, vocabulary matrix
    bag = [0]*len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                # assign 1 if current word is in the vocabulary position
                bag[i] = 1
                if show_details:
                    print ("found in bag: %s" % w)
    return(np.array(bag))

def predict_class(sentence):
    # filter out predictions below a threshold
    p = bow(sentence, words)

    file_model = 'chatbot_model.h5'
    model = load_model(file_model)

    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i,r] for i,r in enumerate(res) if r>ERROR_THRESHOLD]
    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": tags[r[0]], "probability": str(r[1])})
    return return_list

def getResponse(ints, intents_json):
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if(i['tag']== tag):
            # Check tags to call vault when necessary
            if tag == "status":
                result = vault.get_status()
            elif tag == "root":
                result = vault.is_root()
            elif tag == "auditdevices":
                result = vault.get_audit_devices()
            elif tag == "authmethods":
                result = vault.get_auth_methods()
            elif tag == "identity":
                result = vault.get_identity()
            elif tag == "metrics":
                result = vault.get_metrics()
            elif tag == "policies":
                result = vault.get_policies()
                result = ", ".join(result)
            elif tag == "namespaces":
                result = vault.get_list_namespaces()
            elif tag == "secretsengine":
                result = str(vault.get_secrets_engine_list())
            elif tag == "leases":
                result = vault.get_expire_leases()
            elif tag == "configuration":
                result = vault.get_configuration()
            elif tag == "health":
                result = vault.get_health()
            elif tag == "information":
                result = vault.get_general_information()
            elif tag == "version":
                suggestions.suggest_version()
                result = False
            elif tag == "features":
                result = vault.get_features()
            elif tag == "apps":
                result = vault.get_integrated_apps()
            elif tag == "wrapping":
                result = vault.wrapping()
            elif tag == "uptime":
                result = vault.uptime()
            elif tag == "authenticated":
                result = vault.is_authenticated()
            elif tag == "initialized":
                result = vault.is_initialized()
            elif tag == "adoptionstats":
                result = suggestions.adoption_stats_detailed()
            else:
                result = random.choice(i['responses'])
            break
    return result

def chatbot_response(msg):
    ints = predict_class(msg)
    res = getResponse(ints, intents)
    return res

# Http Endpoint
@app.route('/get-answer', methods=['POST'])
def get_answer():

    kb.clear_session()
    tb._SYMBOLIC_SCOPE.value = True

    msg = request.form.get('msg', False)
    
    if msg.lower().find("metrics") >= 0:
        res = requests.get(
            addr + "/v1/sys/metrics?format=", 
            headers={'X-Vault-Token': token}
        ).json()
    else:
        res = chatbot_response(msg)


    if not res:
        return {'success': False, 'answer': ""}

    return {'success': True, 'answer': res}

# Slack Implementation
@app.route('/slack/get-answer', methods=['POST', 'GET'])
def slack_get_answer():
    # Slack bot token
    arr_token = ("xoxb", "918589458594", "931400580288", "9LrOqSiT1GEKFftbqrfRXhD4")
    sl_token = "-".join(arr_token)
    
    # Check if this request is a handshake
    if request.json.get('challenge', False):
        return {'challenge': request.json.get('challenge')}

    else:
        # Check if the last event was a bot response and it's from the right channel
        if not request.json['event'].get('bot_id', False) and request.json['event']['channel'] == "CUBKCGJNB":

            # Check if the message it's a channel join
            if request.json['event'].get('subtype', False) == "channel_join":
                res = "Welcome <@" + request.json['event'].get('user', "") + ">"

            # Get message
            elif request.json['event'].get('text', False):

                msg = request.json['event']['text']
                res = chatbot_response(msg)

            else:
                # Unknown event
                res = False

            # send the message
            if res:
                slack_client = SlackClient(sl_token)
                raq = slack_client.api_call("chat.postMessage", channel=request.json['event']['channel'], text=res) # json.dumps(res, indent=4, sort_keys=True).strip("{").strip("}"))

        return {'success': True}

# Microsoft Teams Implementation
@app.route('/mt/get-answer', methods=['POST', 'GET'])
def mt_get_answer():
    msg = request.json.get('text', False)

    if msg:
        res = chatbot_response(msg)

        webhook_url = "https://outlook.office.com/webhook/\
                66cbaada-14f1-4c2f-8639-22993cb92447@125b0b2a-\
                fc11-406b-8ee5-edc4003afbf3/IncomingWebhook/92b\
                01d770e4c44a6801c1a2062a9efaf/0dc1d84a-92f3-4bf4\
                -82aa-4a9b6316e748"

        # You must create the connectorcard object with the Microsoft Webhook URL
        myTeamsMessage = pymsteams.connectorcard(webhook_url)

        # Add text to the message.
        myTeamsMessage.text(res)

        # send the message.
        myTeamsMessage.send()

    return {'success': True}

# Reponse to more than one channel
# def slackConversations():
    # # Getting channels
    # conv_list_url = "https://slack.com/api/conversations.list?token=" + token
    # resp_conv_list = make_request(conv_list_url)

    # # Getting id and name for every channel
    # if resp_conv_list.get('ok', False):
    #     bot_channels = [{
    #         'id': c.get('id'),
    #         'channel': c.get('name')
    #     } for c in resp_conv_list.get('channels', [])]

    # # Getting the last message of every channel
    # response_msgs = []
    # for channel in bot_channels:
    #     conv_hist = "https://slack.com/api/conversations.history?token=" + token + "&channel=" + channel['id'] + "&inclusive=true&limit=1"
    #     response_msgs.append(make_request(conv_hist))

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, use_reloader=False)

