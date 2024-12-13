# AUBoutiqueII

**Project Overview:**

This project implements a client-server architecture for an e-commerce platform called AUBoutique. It allows users to register, login, view products, add products, buy products, view buyers of products, text with another user, search products, rate products, and view best sellers. This system is composed of two parts: 
1. Server: The server handles client requests, manages the database, and helps the communication between clients. 
2. Client: The client is the one interacting with the system and requesting certain actions to be performed through the GUI. 

It is important to note that SQLite database is used in this project to store the user's data (username, password, products, messages,...). The server automatically creates "auboutique.db" database. 

Some other notes worth mentioning: 
- The use of socket to handle the communication between the client and server codes.
- Users interact with an interactive graphical user interface (GUI) implemented using PyQt5, which sends requests to the server and receives responses in real time.


**Instructions for running the project:**

Step 1: Set up the server code 
  - Open the terminal
  - Navigate to the directory containing "server.py" (example: cd desktop)
  - Execute the following command: "python server.py"
  - The server will start listening for connections at port 8005.

Step 2: Set up the client code
  - Open a new window in the terminal
  - Navigate to the directory containing "client.py" (example: cd desktop)
  - Execute the following command: "python client.py"
  - The client will connect
  - User will now view and interact with the GUI 

*Note:* It is important to run the server code first since the client will attempt to connect to the server at localhost:8005. This connection will fail if the server code is not already running.


**Dependencies/external libraries needed for the project:** 

Running the project requires Python version 3 (Python 3.x) and the following libraries: 
  - socket (for network communication) 
  - json (for json messages and their encoding and decoding) 
  - threading (to handle multiple client connections)
  - sqlite3 (for server database)
  - PyQt5 (for the GUI)
