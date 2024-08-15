from flask import Flask, render_template, request
import os
from dotenv import load_dotenv
from openai import OpenAI
import time
import json

load_dotenv()

# OpenAI API key

client = OpenAI(
  api_key=os.environ['OPENAI_API_KEY'],  # this is also the default, it can be omitted
)

app = Flask(__name__)

# Define the name of the bot
name = 'BOT'

# Define the impersonated role with instructions
roles = {'wiki_bot': f"""
    From now on, you are going to act as a Wikipedia bot.
    Your role is to reply to all requests with information from Wikipedia.
    You may be asked to provide information on a topic in which case respond with a summary of the topic.
    Provide source links to the information you provide.
    YOU ARE NOT AN AI MODEL!
""", 'travel_bot': f"""
    From now on, you are going to act as a travel bot.
    Your role is to provide information on travel destinations based on the requested options supplied by the user.
    Provide source links to the information you provide.
""", 'game_bot': ""} 

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
chat_history = [{'name': name, 'message': roles['wiki_bot']}] 
#chat_history = [{'name': name, 'message': roles['travel_bot']}] # replace with wiki_bot if working with wiki_bot project, temporary fix until better solution for chat history tracking across multiple bots being active at the same time

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
    #chat_history.append(f'\nUser: {user_input}\n')
    chat_history.append({'name': 'User', 'message': user_input, 'day': current_day, 'time': current_time})
    string_history = json.dumps(chat_history)
    chatgpt_raw_output = chatcompletion(user_input, role, explicit_input, string_history).replace(f'{name}:', '')
    chatgpt_output = f'{chatgpt_raw_output}'
    #chat_history.append(chatgpt_output + '\n')
    current_time = time.strftime("%H:%M:%S", time.localtime())
    chat_history.append({'name': name, 'message': chatgpt_output, 'day': current_day, 'time': current_time})
    with open(history_file, 'a') as f:
        f.write('\n'+ current_day+ ' '+ current_time+ ' User: ' +user_input +' \n' + current_day+ ' ' + current_time+  ' ' +  chatgpt_output + '\n')
        f.close()
    return chatgpt_raw_output

# Define app routes
@app.route("/", methods=["GET","POST"])
def index():
    if request.method == "POST":
        message = request.form.get("message")
        get_chat(message, "wiki_bot"),
        return render_template("index.html", message=message, past_messages=chat_history[1::])
    else:
        return render_template("index.html")
    

# Define app routes
# @app.route("/travel", methods=["GET","POST"])
# def travel():
#     if request.method == "POST":
#         location = request.form.get("location")
#         # currency, food, optimal tourist plan, weather, duration of trip, visa requirements, language: this should be a multiple select in a form
#         options = request.form.getlist("options[]")
#         input_text = f"Given {location} I want to know about: {''.join(options)}"
#         get_chat(input_text, "travel_bot")
#         return render_template("travel.html", location=location, past_messages=chat_history[1::])
#     else:
#         return render_template("travel.html")