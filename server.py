import socket
import threading
import sqlite3
import json
import requests

connectedUsers = {}

def setupDatabase():
    db = sqlite3.connect("auboutique.db",check_same_thread=False)
    cursor = db.cursor()
    
    cursor.execute('''
                   CREATE TABLE if not exists users(
                       userId INTEGER PRIMARY KEY AUTOINCREMENT,
                       userUsername TEXT ,
                       userPassword TEXT,
                       userName TEXT,
                       userEmail TEXT, 
                       userOnline INT,
                       userIP TEXT,
                       userPort INTEGER)
                   ''') 
                   
    cursor.execute('''
                   CREATE TABLE if not exists products(
                       productId INTEGER PRIMARY KEY AUTOINCREMENT,
                       ownerId INT, 
                       productName TEXT,
                       productDescription TEXT, 
                       productPrice REAL, 
                       imagePath TEXT, 
                       buyerId INT, 
                       averageRating REAL DEFAULT 0.0,
                       quantity INTEGER DEFAULT 1,
                       purchaseCount INTEGER DEFAULT 0)
                   ''')
    
    cursor.execute('''
                   CREATE TABLE if not exists ratings(
                        ratingId INTEGER PRIMARY KEY AUTOINCREMENT,
                        productId INT,
                        userId INT, 
                        rating INTEGER, 
                        FOREIGN KEY(productId) REFERENCES products(productId),
                        FOREIGN KEY(userId) REFERENCES users(userId))
                   ''')
    
    cursor.execute('''
                   CREATE TABLE if not exists purchases(
                        purchaseId INTEGER PRIMARY KEY AUTOINCREMENT,
                        productId INTEGER,
                        userId INTEGER,
                        purchaseDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
                        FOREIGN KEY(productId) REFERENCES products(productId),
                        FOREIGN KEY(userId) REFERENCES users(userId))
                   ''')
    
    db.commit()
    return db

def updateUserIPandPort(userId, userIP, userPort, cursor, db): 
    cursor.execute("UPDATE users SET userIP=?, userPort=? WHERE userId=?", (userIP, userPort, userId))
    db.commit()
    
def registerUser(request,cursor,db):
    try:
        userName = request['userName']
        userEmail = request['userEmail']
        userUsername = request['userUsername']
        userPassword = request['userPassword']

        cursor.execute("INSERT INTO users(userName,userEmail,userUsername,userPassword,userOnline) VALUES (?,?,?,?,?)" , (userName, userEmail, userUsername, userPassword,0))
        db.commit()
        return {"status": "success", "message": "Registration successful!"}
    
    except sqlite3.IntegrityError:
       return {"status": "error", "message": "Username or email already taken. Try again!"}
   
def loginUser(request,cursor,db):
    
    try:
        userUsername = request['userUsername']
        userPassword = request['userPassword']

        if not userUsername or not userPassword:
            return {"status": "error", "message": "Username or password missing"}

        cursor.execute("SELECT userId FROM users WHERE userUsername=? AND userPassword=?", (userUsername, userPassword))
        user = cursor.fetchone()
        
        if user is not None:
            cursor.execute("UPDATE users SET userOnline = 1 WHERE userId=?", (user[0],))
            db.commit()
            return {"status": "success", 'message': 'Login successful! Welcome to AUBoutique!', "userId": user[0],"userUsername": userUsername}
        else:
            return {"status": "error", "message": "Invalid username or password"}

    except Exception as e:
        print(f"Error during login processing: {e}")
        return {"status": "error", "message": "An error occurred during login."}

def updateUserStatus(userId, userStatus, cursor, db):
    cursor.execute("UPDATE users SET userOnline = ? WHERE userId = ?", (userStatus, userId))
    db.commit()
    
def listProducts(cursor):
    cursor.execute("SELECT products.productId, products.productName, products.productDescription, products.productPrice, products.quantity, users.userId FROM products JOIN users ON products.ownerId = users.userId WHERE products.quantity>0")
    products = cursor.fetchall()
    productsList = []
    
    for p in products: 
        productDetails = {"productId": p[0], "productName": p[1], "productDescription": p[2], "productPrice": p[3], "quantity": p[4], "ownerId": p[5]}
        productsList.append(productDetails)
    
    return {"status":"success","products":productsList}


def viewProductsByOwner(request, cursor):
    ownerId = request['ownerId']  
    cursor.execute("SELECT productId, productName, productDescription, productPrice, quantity FROM products WHERE ownerId = ? AND quantity>0", (ownerId,))
    products = cursor.fetchall()
    
    productsList = []
    for p in products: 
        productDetails = {"productId": p[0], "productName": p[1], "productDescription": p[2], "productPrice": p[3], "quantity": p[4]}
        productsList.append(productDetails)
    
    return {"status":"success","products":productsList}

def checkOnlineStatus(request, cursor):
    try:
        cursor.execute("SELECT userOnline FROM users WHERE userId = ?", (request['ownerId'],))
        status = cursor.fetchone()
        
        if status is not None:
            return {"status": "success", "userOnline": bool(status[0])}
        else:
            return {"status": "error", "message": "Owner not found"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def addProduct(request,cursor,db):
    try:
        productPrice = request['productPrice']
        productCurrency = request['currency'].upper()  
        currencyFrom = 'USD' 
        
        if int(request['productPrice']) < 0 or int(request['quantity']) < 1:
            return {"status": "error", "message": "Price must be a positive number and quantity must be at least 1."}
       
        if productCurrency != currencyFrom:
            conversionResult  = convertMoney(productCurrency, currencyFrom, productPrice)
            
            if conversionResult["status"] == "error":
                return conversionResult
            
            productPrice = conversionResult["convertedAmount"]
        
        cursor.execute("INSERT INTO products (ownerId, productName, productDescription, productPrice, imagePath, quantity) VALUES (?, ?, ?, ?, ?, ?)", (request['userId'], request['productName'], request['productDescription'], productPrice, request['imagePath'], request['quantity']))
        db.commit()
        
        print("Product added to database successfully")
        return {"status": "success", "message": "Product added successfully!"}
    
    except Exception as e:
        print(f"Error in addProduct: {e}")
        return {"status": "error", "message": str(e)}

def buyProduct(request, cursor, db):
    try:
        productId = request['productId']
        userId = request['userId']
        cursor.execute("SELECT quantity FROM products WHERE productId=?", (productId,))
        product = cursor.fetchone()
        if not product or product[0]<=0: 
            return {"status": "error", "message": "Product is out of stock."}

        cursor.execute("UPDATE products SET quantity=quantity-1, purchaseCount=purchaseCount+1 WHERE productId=?", (productId,))
        cursor.execute("INSERT INTO purchases (productId, userId) VALUES(?,?)", (productId, userId))
        db.commit()
        
        updatedProductsResponse = listProducts(cursor)
        if updatedProductsResponse["status"] != "success" or "products" not in updatedProductsResponse: 
            return {"status": "error", "message": "Failed to get the updated products list."}

        return {"status": "success", "message": "Purchase confirmed. Please collect your product from the AUB Post Office on the specified date.", "updatedProducts": updatedProductsResponse["products"]}
    
        #return {"status": "success", "message": "Purchase confirmed. Please collect your product from the AUB Post Office on the specified date."}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}

def sendMessage(request, senderUsername):
    
    if 'recipient' not in request or 'message' not in request:
        return {"status": "error", "message": "Recipient and message must be provided."}
    
    recipientUsername = request['recipient']
    message = request['message']
    
    print(f"Trying to send message to: {recipientUsername}")
    
    if recipientUsername in connectedUsers:
        recipientConnection = connectedUsers[recipientUsername]
        
        response = {"status": "success", "from": senderUsername, "message": message}
        json_response = json.dumps(response)
        
        try:
            recipientConnection.sendall(json_response.encode('utf-8'))

        except Exception as e:
            return {"status": "error", "message": f"Failed to send message: {str(e)}"}
        
        return {"status": "success", "message": "Message sent."}
        
    else:
        print(f"User {recipientUsername} is not in connectedUsers.")
        return {"status": "error", "message": "User is not online."}

def viewBuyers(request, cursor):
    #cursor.execute("SELECT users.userUsername FROM products JOIN users ON products.buyerId = users.userId WHERE products.productId = ?", (request['productId'],))
    #buyer = cursor.fetchone()
    #if buyer:
        #return {"status": "success", "buyer": buyer[0]}
    #else:
        #return {"status": "error", "message": "No buyer found for this product."}   
    
    try: 
        productId = request['productId']
        
        cursor.execute("""SELECT users.userId, users.userUsername FROM purchases JOIN users ON purchases.userId = users.userId WHERE purchases.productId=?""", (productId,))
        buyers = cursor.fetchall()

        if not buyers: 
            return {"status": "error", "message": "No buyers found for this product."}
        
        buyerDetails = [{"userId": buyer[0], "username": buyer[1]} for buyer in buyers]

        return {"status": "success", "message": f"{len(buyers)} purchases made for this product.", "buyers": buyerDetails}
        
    except Exception as e: 
        return {"status": "error", "message": str(e)}

def convertMoney(fromCurrency, toCurrency, amount):
    try:
        # Validate amount
        if amount <= 0:
            return "Please enter a valid amount."

        # Fetch exchange rates
        url = f"https://api.frankfurter.dev/v1/latest?base={fromCurrency}&symbols={toCurrency}"
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes

        data = response.json()
        
        # Check if target currency exists
        if toCurrency in data['rates']:
            convertedAmount = round(amount * data['rates'][toCurrency], 2)
            return {"status": "success", "convertedAmount": convertedAmount}
      
        else:
            return {"status": "error", "message": "Conversion rate not available."}   
    
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": f"Error fetching data: {e}"}
   
    except Exception as e:
        return {"status": "error", "message": f"Unexpected error: {e}"}


def searchProducts(request, cursor):
    searchTerm = "%" + request['query'].strip().lower() + "%"
    cursor.execute("""
        SELECT products.productId, products.productName, products.productDescription, 
               products.productPrice, users.userId 
        FROM products 
        JOIN users ON products.ownerId = users.userId 
        WHERE products.buyerId IS NULL AND 
              (LOWER(products.productName) LIKE LOWER(?) OR LOWER(products.productDescription) LIKE LOWER(?))
    """, (searchTerm, searchTerm))
    
    products = cursor.fetchall()
    if not products:
        return {"status": "success", "message": "No products found matching your search."}
    productsList = [{"productId": p[0], "productName": p[1], "productDescription": p[2], "productPrice": p[3], "ownerId": p[4]} for p in products]
    
    return {"status": "success", "products": productsList}

def addRating(request, cursor, db): 
    try: 
        productId = request['productId']
        userId = request['userId']
        rating = request['rating']

        if rating<1 or rating>5: 
            return {"status": "error", "message": "Rating must be between 1 and 5."}
        
        cursor.execute("INSERT INTO ratings(productId, userId, rating) VALUES(?,?,?)", (productId, userId, rating))
        db.commit()

        updateProductAverageRating(productId, cursor, db)

        return {"status": "success", "message": "Rating added."}
    
    except Exception as e: 
        return {"status": "error", "message": str(e)}

def updateProductAverageRating(productId, cursor, db): 
    cursor.execute("SELECT AVG(rating) FROM ratings WHERE productId = ?", (productId,))

    averageRating = cursor.fetchone()[0] or 0.0

    if averageRating == None: 
        averageRating = 0.0

    averageRating = round(averageRating, 2)
    cursor.execute("UPDATE products SET averageRating =? WHERE productId=?", (averageRating, productId))
    db.commit()
    
def viewAverageRating(request, cursor): 
    try: 
        productId = request['productId']

        cursor.execute("SELECT averageRating FROM products WHERE productId = ? ", (productId,))
        averageRating = cursor.fetchone()

        if averageRating: 
            return {"status": "success", "averageRating": round(averageRating[0],2)}
        
        else: 
            return{"status": "error", "message": "Product not found."}
        
    except Exception as e: 
        return {"status": "error", "message": str(e)}
    
def getBestSellers(cursor): 
    try: 
        cursor.execute('''
                        SELECT products.productId, products.productName, products.productPrice
                        FROM products
                        WHERE purchaseCount>0
                        GROUP BY products.productId
                        ORDER BY purchaseCount DESC
                        LIMIT 2;
                       ''')
        
        bestSellers = cursor.fetchall()

        if not bestSellers: 
            return {"status": "success", "message": "No products have been purchased yet!"}

        listOfbestSellers = []
        for product in bestSellers: 
            listOfbestSellers.append({"productId": product[0], "productName": product[1], "productPrice": product[2]})
        
        return {"status": "success", "bestSellers": listOfbestSellers}
    
    except Exception as e:
        return {"status": "error", "message": f"Error getting the best sellers: {str(e)}"}

def handleClient(connection,address):
    
    db = sqlite3.connect("auboutique.db",check_same_thread=False)
    cursor = db.cursor()
    
    
    print(f"Connection from {address} has been established!")
    
    currentUserId = None
    currentUsername = None
    
    try:
       while True:
            data = connection.recv(1024).decode('utf-8')
            
            if not data:
                print("No data recieved!")
                break
            
            print(f"Received: {data}")
            
            request = json.loads(data)
            
            if request['action'] == 'register':
                response = registerUser(request, cursor, db)
                
            elif request['action'] == 'login':
                response = loginUser(request, cursor, db)
                
                if response["status"] == "success":
        
                    currentUserId = response["userId"]
                    currentUsername = response["userUsername"]
                    
                    updateUserStatus(currentUserId, 1, cursor, db)
                    connectedUsers[currentUsername] = connection
                    
                    print(f"Login successful for user: {currentUsername}, UserId: {currentUserId}")
                    print(f"Current connected users: {connectedUsers}")
                    
                    response['products'] = listProducts(cursor)
                    
                else:
                    print("Login failed:", response["message"])
            
            elif request['action'] == 'listProducts':
                response = listProducts(cursor)
            
            elif request['action'] == 'viewProductsByOwner':
                response = viewProductsByOwner(request, cursor)
            
            elif request['action'] == 'checkOnlineStatus':
                response = checkOnlineStatus(request, cursor)
            
            elif request['action'] == 'addProduct':
                response = addProduct(request, cursor,db)
                
            elif request['action'] == 'buyProduct':
                response = buyProduct(request, cursor,db)
            
            elif request['action'] == 'sendMessage':
                response = sendMessage(request,currentUsername)
                
            elif request['action'] == 'viewBuyers':
                response = viewBuyers(request, cursor)
                
            elif request['action'] == 'addRating': 
                response = addRating(request, cursor,db)
            
            elif request['action'] == 'viewAverageRating': 
                response = viewAverageRating(request, cursor)
                 
            elif request['action'] == 'searchProducts':
                response = searchProducts(request, cursor)
            
            elif request['action'] == 'getBestSellers': 
                response = getBestSellers(cursor)
                
            else:
                response = {"status": "error", "message": "Invalid action"}
                
            connection.sendall(json.dumps(response).encode('utf-8'))
            
    except Exception as e:
        response = {"status": "error", "message": str(e)}
        print(f"Error handling request from {address}: {e}")
        connection.sendall(json.dumps(response).encode('utf-8'))
        
    finally:
        if currentUserId:
            updateUserStatus(currentUserId, 0, cursor, db)  
            if currentUsername in connectedUsers:
                del connectedUsers[currentUsername]
                
        connection.close()
        print(f"Connection with {address} closed.")
        db.close()
        
def startServer():
    db = setupDatabase()
    serverSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    serverSocket.bind((socket.gethostbyname(socket.gethostname()),8005))
    serverSocket.listen()
    print("Server is listening on port 8005")
    
    try:
        while True: 
            try: 
                conn , addr = serverSocket.accept()
                print(f'Accepted connection from {addr}')
                thread = threading.Thread(target=handleClient, args = (conn, addr))
                thread.start() 
            except Exception as e:
                print(f"Error accepting connection: {e}")
    finally:
        serverSocket.close()
        db.close()
        print("Server shutdown.")

startServer()
    