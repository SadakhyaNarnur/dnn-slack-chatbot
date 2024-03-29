from slack_sdk import WebClient
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, render_template
from slackeventsapi import SlackEventAdapter
import string
from datetime import datetime, timedelta
import time
import requests
from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()
import numpy
import tflearn
import tensorflow
import random
import json
import pickle
import nltk
import tensorflow as tf
import re

nltk.download('punkt')
# load_dotenv()
app = Flask(__name__)

@app.route('/')
def index():
  return render_template('index.html')

slack_event_adapter = SlackEventAdapter(
    "c89e2cb12be8c6b870e1d8a170bafa81", '/slack/events', app)

client = WebClient(token="xoxb-6659138368100-6672589994658-T2NDBoLQ0pWYbhXAihhXauQf")
BOT_ID = client.api_call("auth.test")['user_id']
print(BOT_ID)

with open("intents.json") as file:
    data = json.load(file)

try:
    with open("data.pickle", "rb") as f:
        words, labels, training, output = pickle.load(f)
except:
    words = []
    labels = []
    docs_x = []
    docs_y = []

    for intent in data["intents"]:
        for pattern in intent["patterns"]:
            wrds = nltk.word_tokenize(pattern)
            words.extend(wrds)
            docs_x.append(wrds)
            docs_y.append(intent["tag"])

        if intent["tag"] not in labels:
            labels.append(intent["tag"])

    words = [stemmer.stem(w.lower()) for w in words if w != "?"]
    words = sorted(list(set(words)))

    labels = sorted(labels)

    training = []
    output = []

    out_empty = [0 for _ in range(len(labels))]

    for x, doc in enumerate(docs_x):
        bag = []

        wrds = [stemmer.stem(w.lower()) for w in doc]

        for w in words:
            if w in wrds:
                bag.append(1)
            else:
                bag.append(0)

        output_row = out_empty[:]
        output_row[labels.index(docs_y[x])] = 1

        training.append(bag)
        output.append(output_row)


    training = numpy.array(training)
    output = numpy.array(output)

    with open("data.pickle", "wb") as f:
        pickle.dump((words, labels, training, output), f)

net = tflearn.input_data(shape=[None, len(training[0])])
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, len(output[0]), activation="softmax")
net = tflearn.regression(net)

model = tflearn.DNN(net)
# try:
model.load("model.tflearn")
# except:
# model.fit(training, output, n_epoch=1000, batch_size=8, show_metric=True)
# model.save("model.tflearn")

def bag_of_words(s, words):
    bag = [0 for _ in range(len(words))]

    s_words = nltk.word_tokenize(s)
    s_words = [stemmer.stem(word.lower()) for word in s_words]

    for se in s_words:
        for i, w in enumerate(words):
            if w == se:
                bag[i] = 1
            
    return numpy.array(bag)

@ slack_event_adapter.on('message')
def message(payload):
    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')

    # Define regular expressions to match patterns for name, day, and time
    name_pattern = r"with ([\w\s]+)"
    day_pattern = r"on (\w+)"
    date_pattern = r"on (\d{1,2}/\d{1,2}/\d{4})"
    time_pattern = r"at (\d{1,2}(?::\d{2})?\s?[ap]m)"

    # Match patterns in the message text
    name_match = re.search(name_pattern, text, re.IGNORECASE)
    day_match = re.search(day_pattern, text, re.IGNORECASE)
    time_match = re.search(time_pattern, text, re.IGNORECASE)
    date_match = re.search(date_pattern, text, re.IGNORECASE)

    # Initialize variables to store extracted information
    name = None
    day = None
    time = None
    date = None

    # Extract information if patterns are found
    if name_match:
        name = name_match.group(1)
        if user_id != None and BOT_ID != user_id:
            client.chat_postMessage(channel=channel_id, text="Did you say name is "+name)
    if day_match:
        day = day_match.group(1)
        if user_id != None and BOT_ID != user_id:    
            client.chat_postMessage(channel=channel_id, text="You want the meeting on "+day)
    if time_match:
        time = time_match.group(1)
        if user_id != None and BOT_ID != user_id:
            client.chat_postMessage(channel=channel_id, text="Do you confirm this time "+time)
    if date_match:
        date_str = date_match.group(1)
        date = datetime.datetime.strptime(date_str, '%m/%d/%Y').date() 
        if user_id != None and BOT_ID != user_id:
            client.chat_postMessage(channel=channel_id, text="Do you confirm this date "+date)

    name = None
    day = None
    time = None
    date = None

    results = model.predict([bag_of_words(text, words)])
    results_index = numpy.argmax(results)
    tag = labels[results_index]

    for tg in data["intents"]:
        if tg['tag'] == tag:
            responses = tg['responses']
    if user_id != None and BOT_ID != user_id:
        reply = random.choice(responses)
        client.chat_postMessage(channel=channel_id, text=reply)

def send_message_to_slack(message):
    webhook_url = 'https://hooks.slack.com/services/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'
    data = {'text': message}
    headers = {'Content-Type': 'application/json'}
    response = requests.post(webhook_url, json=data, headers=headers)
    response.raise_for_status()

if __name__ == '__main__':
    # Run the Flask application
    send_message_to_slack("Hello, I am your assistant!")
    app.run(host='0.0.0.0',port=5000)
