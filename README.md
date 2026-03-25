AI Discord Chatbot : Vy

Vy is a proof-of-concept AI discord chatbot that mimicks human online chatting. It can read multiple messages sent in a row and treat them as a single prompt, and it automatically splits the AI response into multiple short messages, while handling punctuations that aren't always present in our normal chatting behavior.
The chatbot also has commands that can be used, ranging from an entire save/load system, to admin-only commands that allow precise control of all variables.
A context management feature prevents conversation histories from growing out of control, and keeps API costs in check.

It's coded in python, and uses Ollama to communicate to LLM models via its API. It uses many libraries such as discord.py-self to handle real-time event loops of a discord account, ollama-python to communicate with the API, asyncio to work with non-blocking operations, and aiohttp to handle asynchronous HTTP requests for the API. 

### Disclaimer :
Automating user accounts is against the Discord ToS. This project is a proof of concept, meant to help me learn and improve at coding.

Also, I am aware of the many flaws present in my code, and will be addressing them all eventually, my main focus being university for now. Any feedback is still appreciated though !

## <u>How the program works :</u>
Before launching the program, we need to pip install ollama, aiohttp, and discord.py-self

The code first launches a mirror version of discord, so we can test chatting with the chatbot from another discord account, and ollama, responsible for the AI api.

### The MyClient class :

We create a new object from the class MyClient, and run the program while giving it the discord token of the ai chatbot account, an env variable stored locally.

With the on_ready function, when the connection is established with discord, we send a message in the console for confirmation with print(), and then run the function initiate_admins. What it does is :
* Check if admins.json file exists, and if it does, import the list of admins and stock them in the array admins. Otherwise, have the array admins be empty.


The chatbot detects every single message sent somewhere where it can see it, whether it's in a DM (direct/private message), or any channel in a server visible to the chatbot. It then runs the on_message function for every message.

Upon receiving a message :
* If the message is a DM, ignore.
* If it is currently waiting a specific answer from the are_you_sure function (explained later on), ignore.
* If the message is equal to `!start` AND it is not currently running (in a current conversation with a user), or if the message is equal to `!forcestart`, we save the current author (user who sent the message) and channel, and initiate the connection.

Upon receiving a message while currently running :
* If the author of the message sent, or the channel in which the message was sent, do not match those saved during the `!start` command, ignore.
* If the message starts with a `!`, redirect the processing of the message to the Commands class.
* If the current message stored, messages_sent, is empty, make it equal to the incoming message. Else, append it at the end. 
The goal is being able to receive multiple messages from the user and send them all as a single prompt to the AI.
* We make a new method send_the_sum that sleeps for 2 seconds, then sends the messages_sent to the AI through the OllamaDiscord class (explained later on) and gives back the response to the function send_messages (explained down below). The response is a version of the message that is first processed with the fix_quotes function. What it does is :
* It checks the message for ending quotes, `"` or `”`, and makes sure that the comma is positioned after the ending quote and not inside, as this is a weird glitch that the AI will sometimes do for no reason.
* We use the create_task function from the asyncio library and store it in debounce_task variable. It is a task running with a 2 second timer, and at the end of the timer the message is sent to the AI.
When a message is received, if a task is currently running, it means that it has been less than 2 seconds since the last message. It cancels the running task, and a new task is created with a new 2 seconds timer.

### The send_messages function :

The goal of this function is to divide the message received by the AI into parts, removing commas and full-stops and others to have it seem like it's chatting like a "normal person" and using those as separators for the different parts, and then having the chatbot send several messages on discord, 1 of those parts per message. Some separators are hidden, such as `.` and `,`, while others are kept, such as `?` and `!`.
(I will eventually completely rewrite this whole function and all others tied to it)

* We create a while loop that ends when the message left is empty.
* We call the initiate_list function. What it does is :
  * Replace all the `\\n` in the message with a proper `\n`, sometimes the AI glitches and starts using them for some reason.
  * Define all the separators taken into consideration.
  * Notes all the positions of them inside the message and stores them in the array positions, and then sorts the array positions correctly.
  * A special case is manually treated for when there is a `.` in the middle of a word e.g. `v1.2`, since this should not count as a separator.
* If no separators exist, and if it's not a single `n` remaining, send the message to discord, after being transformed into all lowercase letters if needed using the lowercase_uppercase function. What that function does is :
  * If the 2nd character of the message is in uppercase, we assume that the entire message is in uppercase, and keep it like that e.g. `THIS IS AN EXAMPLE`.
  * Otherwise, make it all lowercase e.g. `this is an example`.
* If the first separator is part of the "chunks" separators such as `(example)`, `"example"`, `“example”`, and `*example*`, we don't want to separate anything in between them to avoid losing the meaning that the AI intentionally chose to highlight. And so we send the message before to discord, and then this whole chunk to discord and then restart the loop with whatever is after. We find those 3 parts using the chunk function. What it does is :
  * Find the position of the 2 separators, and then return the 3 parts aforementioned.
  * If there is another non-chunk separator directly after the end of the chunk separator, e.g. `this is an (example), comma right after the parenthesis !`, we include it in the chunking part.
* We split the message into a before and after using the split function, sending the message before the separator to discord, and then continuing the loop with whatever is after the separator. What the split function does is :
  * Decide which separators to be visible in the message, and which to be completely skipped over.
  * Special cases are manually treated, for when there's a bunch of `!`, `?`, or `.` in a row, or when there's a `!?` or `?!`.

### The API :

The interaction with the AI is done through the OllamaDiscord class. The message sent through the API is divided into 3 types of sections :
* The system command, formatted as `{'role': 'system', 'content': ...}`.
* The user message, formatted as `{'role': 'user', 'content': ...}`.
* The AI response, formatted as `{'role': 'assistant', 'content': ...}`.

The message itself is stored as an array, starting with the system command, then a back and forth between user message and AI response. The AI has no "memory", we need to manually store all previous messages, and then send the entire conversation from the beginning until now every time we want a response.

When a connection is first established, the function chatHistoryInitiate is called. What it does is :
*  It stores the system command in the history variable, resets the messages_count variable to 0, and sets the max_history_message_sent to False. Given that we're using a cloud AI, the bigger the history gets, the more costly a single prompt gets, and so we need to cap how long the history can get, and to do so we need to keep track of the amount of messages sent.

When a message is sent to the AI, it's done with the function ai_chatbot, which in turn calls the function main. The roundabout is to be able to handle KeyboardInterrupt. What the function main does is :
* It first calls the function chatGenerate, and stores the result in the variable ai_output. What the function does is :
  * It states which model is being used, and creates an AsyncClient object.
  * It sends the message through the API, with which AI to talk to, and the message which is made of the history + the new user message.
  * it returns the message content of the response.
  * If an error is encountered, the program keeps retrying to send until it succeeds, while printing in the console the error. It only specifies the error if it is Server Disconnected, otherwise it will show Upstream error for the rest, since no error other than these two has been encountered so far.
* It then updates the history using the function chatHistory. What it does is :
  * It adds the user message and the AI response to the end of the history,with the correct formatting. 
  * It increases the messages_count by 1.
  * if the messages_count is over 80, it removes the 2nd and 3rd positions of the array history, which correspond to the first user message sent and the first AI response received, the first position always being the system prompt. It then calls the function history_max from the class Client, which simply sends a discord message warning the user. 
  It is possible to keep conversing with the AI past this point, however it will always forget the first user message and first AI response present in the history every time a new message is sent.
* It returns the ai_output, so that it can be processed and sent on discord by the Client function on_message that called it.

<br>
<br>

Before explaining the commands, we will explain the function are_you_sure from the class Client. What it does is :
* It first changes the waiting_for_confirmation variable to True. When this variable is True, the on_message function will not process any message sent, and we will manually select which message we want.
* We create a local function check, which checks if the message has the same author and channel ID as the ones stored.
* We start a 30 second timer. When the timer runs out, we send a discord message and then return nothing (None) to exit the function.
Since the waiting_for_confirmation variable is defined as False by default, once we exit out of the function are_you_sure, the program goes back to its default behavior.
* If the user sends a message `yes` or `y`, the function returns True.
* If the user sends a message `no` or `n`, the function returns nothing (None) to exit the function.
* If the user sends anything else, we send a discord message telling them to only respond with a yes or no. 
The function can only end if the timer runs out, or if the user answers successfully.

### The commands : 
They are messages sent by the user that start with a `!`, the first command the user uses is `!start`. These commands are not sent to the AI API, and are instead processed separately. 
The function commands inside the class Commands is called whenever a message sent from the user starts with a `!`. It removes the `!` at the beginning, and then compares the remaining message to see if it matches any current command. Otherwise, it sends a discord message saying that it's not a valid command. 
Only one command can be processed at a time. After a command is processed, the function returns nothing (None), and we get out of the commands and back to the default behavior.

The current commands are :
* help :
a list of all the available commands. Extra commands are shown if the user is an admin.
* start :
Since the `!start` command is handled in the MyClient class, it sends a message to discord saying the conversation has already started.
* forcestart :
Only works if the user is admin. Forcefully establishes a new connection with the current user, regardless of if there was another ongoing conversation or not, and clears the history.

The rest of the commands only work if there is an ongoing conversation. 
* end :
Ends the current connection, and resets the author, channel, and running variables. It then sends a message to discord saying that the connection was ended.
* reset :
Instead of ending, it simply resets the history so the user can start a new conversation. It then sends a message to discord saying that the connection was reset.
* save :
This opens up a save file system, being able to save current conversations so they can be continued later on. They are saved in the directory `saves` situated in the same directory as the code. The `logs.txt` file is always present there, it contains only the titles of the save files, to find them more easily.
If the entire message is exactly equal to `!save`, send a message to discord telling the user to specify the name of the save file.
We replace all the spaces with `_`, and make all the characters lowercase.
We check inside the `logs.txt` file and compare line by line. If the name given exactly matches with an existing save file, send a message to discord telling the user to pick another name.
If all the conditions are correctly met, we create a new file with the name given by the user, and then add that name on a new line in the `logs.txt` file. It then sends a message to discord saying that the saving was successful.
* load :
This complements the save file system.
If the entire message is exactly equal to `!load`, send a message to discord telling the user to specify the name of the save file.
We ask the user if they're sure they want to load, as any unsaved ongoing conversation will be lost, and then call the are_you_sure function to get the answer of the user. If the user refuses or if the timer runs out, the loading process is cancelled.
We replace all the spaces with `_`, and make all the characters lowercase.
We check inside the `logs.txt` file and compare line by line. If the name given DOES NOT exactly match with an existing save file, send a message to discord telling the user to pick a correct name.
If all the conditions are correctly met, we read the save file, and override the history with the one present in the save file, letting the user continue their previous conversation directly. It then sends a message to discord saying that the loading was successful.
* delete : 
Only works if the user is admin. This complements the save file system.
If the entire message is exactly equal to `!delete`, send a message to discord telling the user to specify the name of the save file.
We replace all the spaces with `_`, and make all the characters lowercase.
We ask the user if they're sure they want to delete, as the save file will be lost forever, and then call the are_you_sure function to get the answer of the user. If the user refuses or if the timer runs out, the loading process is cancelled.
We go inside `logs.txt` and save all the current lines. We then rewrite every single line while checking if there is an exact match to the name given by the user. If there is not an exact match, send a message to discord telling the user to pick a correct name. 
If there is an exact match, we dont rewrite the line, and then delete the save file. It then sends a message to discord saying that the deleting was successful.
* addadmin :
Only works if the user is admin. 
If the entire message is exactly equal to `!addadmin`, send a message to discord telling the user to specify the ID of the user.
We replace all the spaces with `_`, and make all the characters lowercase.
If the ID given exists in the array admins, send a message to discord telling the user that the ID given is already an admin.
If all the conditions are correctly met, add the ID to the end of the array admins, and then add it to the `admins.json` file situated in the same directory as the code. It then sends a message to discord saying that the ID was successfully added.
* deladmin :
Only works if the user is admin. 
If the entire message is exactly equal to `!deladmin`, send a message to discord telling the user to specify the ID of the user.
We replace all the spaces with `_`, and make all the characters lowercase.
If the ID given DOES NOT exist in the array admins, send a message to discord telling the user that the ID given is not an admin.
If all the conditions are correctly met, remove the ID from the array admins, as well as from the `admins.json` file. It then sends a message to discord saying that the ID was successfully deleted.
* changeu :
Only works if the user is admin. Change the current user to the one specified. It then sends a message to discord saying that the change was successful.
* changec :
Only works if the user is admin. Change the current channel to the one specified. The chatbot then sends a message in both the previous and the new channels to verify the change went correctly.
* no :
Any message that starts with a `!no` will be ignored by the program, so the user is able to communicate with others without having the AI process it.