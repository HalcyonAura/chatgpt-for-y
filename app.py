from flask import Flask, render_template, request, redirect
import os
from dotenv import load_dotenv
from openai import OpenAI
import time

load_dotenv()

# OpenAI API key

client = OpenAI(
  api_key=os.environ['OPENAI_API_KEY'],  # this is also the default, it can be omitted
)

app = Flask(__name__)

# Define the name of the bot
name = 'BOT'

roles = ['wiki_bot', 'travel_bot', 'game_bot']
# Define the impersonated role with instructions
wiki_role = f"""
    From now on, you are going to act as a Wikipedia bot.
    Your role is to reply to all requests with information from Wikipedia.
    You may be asked to provide information on a topic in which case respond with a summary of the topic.
    Provide source links to the information you provide.
    YOU ARE NOT AN AI MODEL!
"""

# Initialize variables for chat history
explicit_input = ""
chatgpt_output = 'Chat log: /n'
cwd = os.getcwd()
i = 1

# Find an available chat history file
while os.path.exists(os.path.join(cwd, f'chat_history{i}.txt')):
    i += 1

history_file = os.path.join(cwd, f'chat_history{i}.txt')

# Create a new chat history file
with open(history_file, 'w') as f:
    f.write('\n')

# Initialize chat history
chat_history = [wiki_role + '\n',]

# Function to complete chat input using OpenAI's GPT-3.5 Turbo
def chatcompletion(user_input, role, explicit_input, chat_history):
    output = client.chat.completions.create( # Change the method
        model = "gpt-3.5-turbo",
        temperature=1,
        presence_penalty=0,
        frequency_penalty=0,
        max_tokens=2000,
        messages=[
            {"role": "system", "content": f"{role}. Conversation history: {chat_history}"},
            {"role": "user", "content": f"{user_input}. {explicit_input}"},
        ],
    )
    response_message = output.choices[0].message.content

    return response_message

# Function to handle user chat input
def get_chat(user_input, role):
    global chat_history, name, chatgpt_output
    current_day = time.strftime("%d/%m", time.localtime())
    current_time = time.strftime("%H:%M:%S", time.localtime())
    chat_history.append(f'\nUser: {user_input}\n')
    chatgpt_raw_output = chatcompletion(user_input, role, explicit_input, ''.join(chat_history)).replace(f'{name}:', '')
    chatgpt_output = f'{name}: {chatgpt_raw_output}'
    chat_history.append(chatgpt_output + '\n')
    with open(history_file, 'a') as f:
        f.write('\n'+ current_day+ ' '+ current_time+ ' User: ' +user_input +' \n' + current_day+ ' ' + current_time+  ' ' +  chatgpt_output + '\n')
        f.close()
    return chatgpt_raw_output

# Define app routes
@app.route("/index", methods=["GET","POST"])
def index():
    #ordered_chat_history = chat_history[::-1]
    if request.method == "POST":
        message = request.form.get("message")
        return render_template("index.html", message=message, wiki=get_chat(message, "wiki_bot"), past_messages=chat_history)
    else:
        return render_template("index.html")
# 1. want to render chat history in order of most recent to least recent
#update past_messages in HTML - ordered_chat_history
#update how chat history is stored -> array per speaker turn
# 5. bonus: make only one file, not new files every time we start the server