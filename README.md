# dnn-slack-chatbot

##What are we building?
### An NLP based bot that helps with scheduling meetings based on its conversation with a user. The bot is essentially a Flask app that is hosted with Ngrok.
An App named ‘Meetbot’ communicates with our Flask app and responds based on the inference of our model.

## How to build this bot?
### Collect and Prepare the data: Here the intents.json consists of question and answer data that will be used to train the model. 
### Transform the data: The intents are read, word level tokenized and stemmed. We use the Bag-of-words by creating a word dictionary for each document, create one-hot encoded output value and data is pickled.
### Build DNN model: Once we load the model we fitted the training data and saved the checkpoints and model artifacts.
### Run inference on user messages and send the response with highest probability.

## How to integrate the bot with Slack?
### Create an app in Slack that is integrated with a workspace and a channel. 
### Add required Bot Scopes to this app like “Send messages as @Meetbot”, ”View messages” and “Post messages”.
### Integrate the Bot oAuth Token, Signing Secret and Webhook url into our Python Flask code.
### To expose the Flask api to Slack we use ngrok to host our app. This ngrok endpoint is given for Request URL to enable events and subscribe to bot events.
### Using the slack apis the bot can access the message payloads to reply. The model predicts on the message it received and posts the chat message. 

## How to deploy on Apprunner?
### Using Github repository: We can create an App runner service with the source code repository pointing to our github repo, set the required environment variables and configurations.
### Issue faced: the slackclient is deprecated hence used slack_sdk but when deploying module cannot be found.
### Using docker image: The docker image can be pushed to Elastic Container Registry service which can be provided as Container Registry to the App runner service. Further setting the configurations we can build.
### Provide the public endpoint to the Slack event subscription request URL. Thereby using the public endpoint the app can communicate with slack.
### Issue faced: the healthcheck is failing else the localhost is working.



