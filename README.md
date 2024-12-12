_**System Architecture Overview**_

**Architecture Type:**
The application follows a Client-Server model where clients connect to a central server that permits them to perform actions such as registering, logging in, adding or buying products, and messaging other users.

**Components:**
Client: Users, who could be sellers or buyers,  interact with the application through an interactive graphical user interface (GUI) implemented using PyQt5, which sends requests to the server and receives responses in real time.
Server: Manages requests from users, performs database operations, and enables direct communication between online users.
Database (SQLite): Stores data such as user credentials and product details.

**Protocol:**
*Communication Protocol:* The server and clients communicate over TCP, which is reliable for real-time messaging and data transfer between the components.
*Message Format:* JSON-based protocol for standardized requests and responses. Each request includes a type field indicating the action and necessary data fields. Each response includes a status field and additional data.

**Database Structure:**
*Database Type:* SQLite
*Tables:*
1. *User table:* stores the user’s ID number, name, username, password, email, online status, and IP address and port number.
2. *Products table:* stores the product’s ID number, name, description, price, image, average rating, quantity, and purchase count along with the ID number of the product’s owner and buyer, if sold.
3. *Ratings table:* stores the IDs of the product, user, and rating along with the rating. 
4. *Purchases table:* stores the IDs of the product, user, and purchase along with the purchase date. 
	
**Error Handling and Status Codes:**
Each server response includes a status indicating the result of the request:
- Success: The request was successfully processed.
- Error: An error message is returned if the request cannot be completed.
