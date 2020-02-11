# compose_flask/app.py
from flask import Flask
from flask import request

from keras.models import load_model
from slackclient import SlackClient

import keras.backend as kb
import keras.backend.tensorflow_backend as tb

import numpy as np
import json
import pickle
import random
import spacy
import requests

app = Flask(__name__)

data_json = 'intents.json'
words_file = 'words.pkl'
tags_file = 'tags.pkl'

intents = json.loads(open(data_json).read())
words = pickle.load(open(words_file, 'rb'))
tags = pickle.load(open(tags_file, 'rb'))

npl = spacy.load('en_core_web_sm')

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
    res = chatbot_response(msg)

    if not res:
        return {'success': False, 'answer': ""}
    
    return {'success': True, 'answer': res}

# Slack Implementation
@app.route('/', methods=['POST', 'GET'])
def hello_w():
    
    token = ""
    
    if request.json.get('challenge', False):
        return {'challenge': request.json.get('challenge')}
    
    else:
        if not request.json['event'].get('bot_id', False):
            msg = request.json['event']['text']
            res = chatbot_response(msg)
            
            slack_client = SlackClient(token)
            slack_client.api_call("chat.postMessage", channel="#robochat", text=res)
            
        return {'success': True}

# Reponse to more than one channel
def slackConversations():
    pass
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

# slackConversation()
# Simple build
# query = "Hello my friend"
# print("We need to receive this in a json request: %s" % query)
# print("We need to send this in a json response: %s" % chatbot_response(query))



if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
