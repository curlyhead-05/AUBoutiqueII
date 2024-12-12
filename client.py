# -*- coding: utf-8 -*-

import sys
import socket
import json
import threading
from PyQt5.QtGui import QFont, QTextCursor

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QLineEdit, QLabel, QMessageBox, QStackedWidget, QInputDialog,
    QTextEdit, QSpacerItem, QSizePolicy
)

messages = []

def connectToServer():
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((socket.gethostbyname(socket.gethostname()), 8005))
    return clientSocket

def sendRequest(clientSocket, request):
    
    json_request = json.dumps(request)
    clientSocket.sendall(json_request.encode('utf-8'))
    
    json_response = clientSocket.recv(1024).decode('utf-8')
    
    if not json_response:
        raise ValueError("Empty response from server")
        
    response = json.loads(json_response)
    return response

class ClientApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.stopListening = False
        
        self.clientSocket = connectToServer()
        self.userId = None

        self.setupMainWindow()
        
        listeningThread = threading.Thread(target=self.listenForMessages, args=(self.clientSocket,))
        listeningThread.daemon = True  
        listeningThread.start()
       
    def setupMainWindow(self):
        
        self.setWindowTitle("AUBoutique")
        self.setGeometry(50, 50, 1000, 400)
        
        font = QFont("Comic Sans MS", 20)  
        self.setFont(font)
    
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.layout = QVBoxLayout(self.centralWidget)

        self.stack = QStackedWidget()
        self.layout.addWidget(self.stack)

        self.initMainPage()
        self.initLoginPage()
        self.initRegisterPage()
        self.initActionsPage()
        
        self.messageArea = QTextEdit(self)
        self.messageArea.setReadOnly(True) 
        self.messageArea.setText("Messages will appear here...")
    
        self.messageArea.setAlignment(Qt.AlignCenter)
        self.messageArea.setStyleSheet("font-size: 25px; border: 2px solid #ff69b4; border-radius: 5px; background-color: #f9f9f9; border: 1px solid #cccc; padding: 5px;")
        self.messageArea.setFixedHeight(120)
        self.layout.addWidget(self.messageArea)  
        
        self.stack.setCurrentWidget(self.mainPage)

    def initMainPage(self):

        self.mainPage = QWidget()
        layout = QVBoxLayout(self.mainPage)
        
        btnRegister = QPushButton("Register")
        btnlogin = QPushButton("Already Registered? Login Here!")
        btnexit = QPushButton("Exit")
        
        buttonStyle = """
        QPushButton {font-size: 20px; background-color: #ff69b4; color: white; padding: 25px; border-radius: 8px;}
        QPushButton:hover {background-color: #21867a;}
         """
         
        for button in [btnRegister, btnlogin, btnexit]:
            button.setStyleSheet(buttonStyle)
            button.setFixedWidth(350) 
        
        btnRegister.clicked.connect(lambda: self.stack.setCurrentWidget(self.registerPage))
        btnlogin.clicked.connect(lambda: self.stack.setCurrentWidget(self.loginPage))
        btnexit.clicked.connect(self.close)
        
        welcomeLabel = QLabel("Welcome to AUBoutique!")
        welcomeLabel.setAlignment(Qt.AlignCenter)
        welcomeLabel.setStyleSheet("font-size: 45px; font-weight: bold; color: #ff69b4;")
       
        layout.addWidget(welcomeLabel)
        layout.addWidget(btnRegister)
        layout.addWidget(btnlogin)
        layout.addWidget(btnexit)
        
        buttonLayout = QVBoxLayout()
        buttonLayout.setAlignment(Qt.AlignCenter)
        buttonLayout.setSpacing(8)  
        buttonLayout.addWidget(btnRegister)
        buttonLayout.addWidget(btnlogin)
        buttonLayout.addWidget(btnexit)
         
        self.layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.layout.addLayout(buttonLayout)
        self.layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Minimum))
        self.layout.addLayout(buttonLayout)
        self.stack.addWidget(self.mainPage)

    def initLoginPage(self):

        self.loginPage = QWidget()
        layout = QVBoxLayout(self.loginPage)
        
        header = QLabel("Login")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("font-size: 45px; font-weight: bold; color: #ff69b4;")
    
        self.loginUsername = QLineEdit()
        self.loginPassword = QLineEdit()
        self.loginPassword.setEchoMode(QLineEdit.Password)

        self.loginUsername.setPlaceholderText("Username")
        self.loginPassword.setPlaceholderText("Password")

        btnLogin = QPushButton("Login")
        btnBack = QPushButton("Back")
        
        buttonStyle = """QPushButton {font-size: 16px; background-color: #ff69b4; color: white; padding: 10px; border-radius: 8px;}
                         QPushButton:hover { background-color: #ff1493;  }
                      """
                      
        btnLogin.setStyleSheet(buttonStyle)
        btnBack.setStyleSheet(buttonStyle)
    
        btnLogin.clicked.connect(self.handleLogin)
        btnBack.clicked.connect(lambda: self.stack.setCurrentWidget(self.mainPage))

        layout.addWidget(header)
        layout.addWidget(self.loginUsername)
        layout.addWidget(self.loginPassword)
        layout.addWidget(btnLogin)
        layout.addWidget(btnBack)

        self.stack.addWidget(self.loginPage)

    def initRegisterPage(self):
        self.registerPage = QWidget()
        layout = QVBoxLayout(self.registerPage)
        
        header = QLabel("Register")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("font-size: 45px; font-weight: bold; color: #ff69b4;")
    
        self.registerName = QLineEdit()
        self.registerEmail = QLineEdit()
        self.registerUsername = QLineEdit()
        self.registerPassword = QLineEdit()
        self.registerPassword.setEchoMode(QLineEdit.Password)

        self.registerName.setPlaceholderText("Full Name")
        self.registerEmail.setPlaceholderText("Email")
        self.registerUsername.setPlaceholderText("Username")
        self.registerPassword.setPlaceholderText("Password")
        
        buttonStyle = """QPushButton {font-size: 16px; background-color: #ff69b4; color: white; padding: 10px; border-radius: 8px;}
                         QPushButton:hover {background-color: #ff1493;}
                      """
    
        btnRegister = QPushButton("Register")
        btnBack = QPushButton("Back")
        btnRegister.setStyleSheet(buttonStyle)
        btnBack.setStyleSheet(buttonStyle)
        
        btnRegister.clicked.connect(self.handleRegister)
        btnBack.clicked.connect(lambda: self.stack.setCurrentWidget(self.mainPage))

        layout.addWidget(header)
        layout.addWidget(self.registerName)
        layout.addWidget(self.registerEmail)
        layout.addWidget(self.registerUsername)
        layout.addWidget(self.registerPassword)
        layout.addWidget(btnRegister)
        layout.addWidget(btnBack)

        self.stack.addWidget(self.registerPage)
        
    def initActionsPage(self):

        self.actionsPage = QWidget()
        layout = QVBoxLayout(self.actionsPage)
        
        header = QLabel("Choose an action")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("font-size: 30px; font-weight: bold; color: #ff69b4;")
      
        self.btnViewProducts = QPushButton("View Available Products")
        self. btnViewProductsByOwner = QPushButton("View Products By Owner")
        self.btnCheckOnlineStatus = QPushButton("Check Owner's Online Status")
        self.btnAddProduct = QPushButton("Add Product")
        self.btnBuyProduct = QPushButton("Buy Product")
        self.btnSendMessage = QPushButton("Send Message")
        self.btnViewBuyers = QPushButton("View Buyer")
        self.btnSearchProducts = QPushButton("Search Products")
        self.btnDisplayMessages = QPushButton("Display Incoming Messages")
        self.btnDisplayMessages = QPushButton("Display Incoming Messages")
        self.btnGetBestSellers = QPushButton("Get Best Sellers")
        self.btnAddRating = QPushButton("Add Rating")
        self.btnViewAverageRating = QPushButton("View Average Rating")
        self.btnLogout = QPushButton("Logout")
        
        buttonStyle = """QPushButton {font-size: 14px; background-color: #ff69b4; color: white; padding: 8px; border-radius: 8px;}
                          QPushButton:hover {background-color: #ff1493;}
                       """
        for button in [self.btnViewAverageRating, self.btnAddRating, self.btnViewProducts, self.btnViewProductsByOwner, self.btnCheckOnlineStatus, self.btnAddProduct, self.btnBuyProduct, self.btnSendMessage, self.btnViewBuyers, self.btnSearchProducts, self.btnDisplayMessages,self.btnGetBestSellers, self.btnLogout ]: button.setStyleSheet(buttonStyle)


        self.btnViewProducts.clicked.connect(self.handleListProducts)
        self.btnViewProductsByOwner.clicked.connect(self.handleViewProductsByOwner)
        self.btnCheckOnlineStatus.clicked.connect(self.handleCheckOnlineStatus)
        self.btnAddProduct.clicked.connect(self.handleAddProduct)
        self.btnBuyProduct.clicked.connect(self.handleBuyProduct)
        self.btnSendMessage.clicked.connect(self.handleSendMessage)
        self.btnViewBuyers.clicked.connect(self.handleViewBuyers)
        self.btnSearchProducts.clicked.connect(self.handleSearchProducts)
        self.btnDisplayMessages.clicked.connect(self.handleDisplayIncomingMessages) 
        self.btnGetBestSellers.clicked.connect(self.handleGetBestSellers)
        self.btnAddRating.clicked.connect(self.handleAddRating)
        self.btnViewAverageRating.clicked.connect(self.handleViewAverageRating)
        self.btnLogout.clicked.connect(self.handleLogout)

        layout.addWidget(header)
        layout.addWidget(self.btnViewProducts)
        layout.addWidget(self.btnViewProductsByOwner)
        layout.addWidget(self.btnCheckOnlineStatus)
        layout.addWidget(self.btnAddProduct)
        layout.addWidget(self.btnBuyProduct)
        layout.addWidget(self.btnSendMessage)
        layout.addWidget(self.btnViewBuyers)
        layout.addWidget(self.btnSearchProducts)
        layout.addWidget(self.btnDisplayMessages)
        layout.addWidget(self.btnGetBestSellers)
        layout.addWidget(self.btnAddRating)
        layout.addWidget(self.btnViewAverageRating)
        layout.addWidget(self.btnLogout)
        
        self.stack.addWidget(self.actionsPage) 


    def handleLogin(self):
        
        username = self.loginUsername.text()
        password = self.loginPassword.text()
        
        if not username or not password:
            self.showMessageBox("Error", "Please fill in all fields.")
            return
   
        request = {"action": "login", "userUsername": username, "userPassword": password}
       
        try:
            response = sendRequest(self.clientSocket, request)
           
            if response['status'] == 'success':
                self.userId = response["userId"]
                self.showMessageBox("Success", response['message'])
                
                self.stack.setCurrentWidget(self.mainPage)
                self.loginUsername.clear()
                self.loginPassword.clear()
 
                self.handleListProducts()
                
                self.stack.setCurrentWidget(self.actionsPage)
             
            else:
                self.showMessageBox("Error", response['message'])
                
        except Exception as e:
            self.showMessageBox("Error", f"Login failed: {str(e)}")
            
    def handleRegister(self):

        name = self.registerName.text()
        email = self.registerEmail.text()
        username = self.registerUsername.text()
        password = self.registerPassword.text()
        
        if not username or not password or not email or not password:
            self.showMessageBox("Error", "Please fill in all fields.")
            return
        
        request = {
            "action": "register",
            "userName": name,
            "userEmail": email,
            "userUsername": username,
            "userPassword": password
        }

        try:
            response = sendRequest(self.clientSocket, request)
            if response['status'] == 'success':
                self.showMessageBox("Success", response['message'])
                self.stack.setCurrentWidget(self.mainPage)
                self.registerName.clear()
                self.registerEmail.clear()
                self.registerUsername.clear()
                self.registerPassword.clear()
                
            else:
                self.showMessageBox("Error", response['message'])
                
        except Exception as e:
            self.showMessageBox("Error", f"Registration failed: {str(e)}")
    
    def handleLogout(self):

        self.stopListening = True
        self.userId = None
        self.clientSocket.close() 
        self.showMessageBox("Info", "Logged out successfully.")
        self.stack.setCurrentWidget(self.mainPage)
        
    def handleListProducts(self):
        request = {"action": "listProducts"}
        try:
            response = sendRequest(self.clientSocket, request)

            if response["status"] == "success":
                products = response.get("products", [])
                if products:
                    productsMessage = "Products available:\n"
                    
                    for product in response["products"]:
                        productsMessage += f"ID: {product['productId']}\n"
                        productsMessage += f"Name: {product['productName']}\n"
                        productsMessage += f"Description: {product['productDescription']}\n"
                        productsMessage += f"Price: ${product['productPrice']:.2f}\n"
                        productsMessage += f"Quantity Available: {product['quantity']}\n"
                        productsMessage += f"Owner ID: {product['ownerId']}\n\n"
                    
                    self.showMessageBox("Products", productsMessage)
                else:
                    self.showMessageBox("No Products", "No available products to show.")
            else:
                self.showMessageBox("Error", response["message"])
        except Exception as e:
            self.showMessageBox("Error", f"Failed to list products: {str(e)}")
  
    def handleViewProductsByOwner(self):
        """Handle View Products By Owner Request"""
        ownerId, ok = QInputDialog.getInt(self, "Enter Owner ID", "Owner ID:")
       
        if ok:
            request = {"action": "viewProductsByOwner", "ownerId": ownerId}
           
            try:
                response = sendRequest(self.clientSocket, request)

                if response["status"] == "success":
                    products = response.get("products", [])
                    if products:
                        productsMessage = f"Products by Owner {ownerId}:\n"
                        for product in products:
                            productsMessage += f"ID: {product['productId']}\n"
                            productsMessage += f"Name: {product['productName']}\n"
                            productsMessage += f"Description: {product['productDescription']}\n"
                            productsMessage += f"Quantity Available: {product['quantity']}\n"
                            productsMessage += f"Price: ${product['productPrice']:.2f}\n\n"
                        self.showMessageBox("Products", productsMessage)
                    else:
                        self.showMessageBox("No Products", f"No products found for owner {ownerId}.")
                else:
                    self.showMessageBox("Error", response["message"])
            except Exception as e:
                self.showMessageBox("Error", f"Failed to view products: {str(e)}")
      
    def handleExit(self):
        self.stopListening = True
        self.clientSocket.close()
        self.close()
        print("Application exited and listening thread stopped.")

    def handleCheckOnlineStatus(self):
        ownerId, ok = QInputDialog.getInt(self, "Enter Owner ID", "Owner ID:")
        if not ok:
            print("failure 1")
            return None

        request = {"action": "checkOnlineStatus", "ownerId": ownerId}
             
        response = sendRequest(self.clientSocket, request)

        if response["status"] == "success":
               
             if response["userOnline"]:
                 self.showMessageBox("Online Status", f"Owner {ownerId} is currently online.")
                 return True
                
             else:
                 print("failure2")
                 self.showMessageBox("Online Status", f"Owner {ownerId} is currently offline.")
                 return False
                 
        else:
             self.showMessageBox("Error", response["message"])
             print("failure 3")
             return None
            
    def handleAddProduct(self):
        """Handle Add Product Request"""
        productName, ok = QInputDialog.getText(self, "Product Name", "Enter product name:")
        if not ok or not productName.strip():
           return

        productPrice, ok = QInputDialog.getText(self, "Price", "Enter product price:")
        if not ok or not productPrice.strip():
           return

        productDescription, ok = QInputDialog.getText(self, "Description", "Enter product description:")
        if not ok or not productDescription.strip():
           return

        imagePath, ok = QInputDialog.getText(self, "Image Path", "Enter image path:")
        if not ok or not imagePath.strip():
           return

        currency, ok = QInputDialog.getText(self, "Currency", "Enter currency (USD, EUR, etc.):")
        if not ok or not currency:
           return
       
        quantity, ok = QInputDialog.getText(self, "Quantity", "Enter quantity:")
        if not ok or not quantity:
           return

        if not productName or not productPrice or not productDescription or not imagePath or not currency:
            self.showMessageBox("Error", "Please fill in all fields.")
            return

        try:
            productPrice = float(productPrice)
        
            request = {
            "action": "addProduct",
            "userId": self.userId,
            "productName": productName.strip(),
            "productPrice": productPrice,
            "productDescription": productDescription.strip(),
            "imagePath": imagePath.strip(),
            "quantity": quantity,
            "currency": currency
         }

            response = sendRequest(self.clientSocket, request)

            if response["status"] == "success":
                self.showMessageBox("Success", response["message"])
                
            else:
                self.showMessageBox("Error", response["message"])

        except ValueError:
            self.showMessageBox("Error", "Invalid price. Please enter a valid number.")
        except Exception as e:
            self.showMessageBox("Error", f"Failed to add product: {str(e)}")
  
    def handleBuyProduct(self):
        """Handle Product Purchase Request"""
        productId, ok = QInputDialog.getInt(self, "Enter Product ID", "Product ID:")
    
        if ok:
            request = {"action": "buyProduct", "userId": self.userId, "productId": productId}
            try:
                response = sendRequest(self.clientSocket, request)
                self.showMessageBox("Purchase Status", response["message"])
                
            except Exception as e:
                self.showMessageBox("Error", f"Failed to buy product: {str(e)}")
                
    def handleSendMessage(self):

        ownerUsername, ok = QInputDialog.getText(self, "Enter Owner Username", "Owner Username:")
    
        if ok and ownerUsername:
            onlineStatus = self.handleCheckOnlineStatus()
        
            if onlineStatus is True:
                message, ok = QInputDialog.getText(self, "Enter Your Message", "message:")
                print("success 1")

                if ok and message:
                    
                    request = {"action": "sendMessage", "recipient": ownerUsername, "message": message}
                    response = sendRequest(self.clientSocket, request)
                    self.showMessageBox("Message Status", response["message"])
                    print("success 2")
                else:
                    self.showMessageBox("Error", "Message cannot be found")
                    print("failure 4")

           
            elif onlineStatus is False:
                self.showMessageBox("Error", f"Cannot send message. Owner with username {ownerUsername} is offline.")
                print("failure 5")
           
            else:
                self.showMessageBox("Error", "Owner not found.")
                print("failure 6")

    def handleViewBuyers(self):
        """Handle View Buyers Request"""
        productId, ok = QInputDialog.getInt(self, "Enter Product ID", "Product ID:")
    
        if ok:
            request = {"action": "viewBuyers", "productId": productId}
        
            try:
                response = sendRequest(self.clientSocket, request)
            
                if response["status"] == "success":
                    message = response.get("message", "Buyers retrieved successfully.")
                    buyers = response.get("buyers", [])
                    
                    if buyers:
                        buyersList = "\n".join([f"User ID: {buyer['userId']}, Username: {buyer['username']}" for buyer in buyers])
                        self.showMessageBox("Buyers", f"{message}\n\nThe buyers for this product are:\n{buyersList}")
                   
                    else:
                        self.showMessageBox("Buyers", f"{message}\n\nNo buyers found.")
                        
                else:
                    self.showMessageBox("Error", f"Error: {response.get('message', 'Unknown error')}")
            
            except Exception as e:
                self.showMessageBox("Error", f"Failed to view buyer: {str(e)}")
                
    def handleSearchProducts(self):
        """Handle Product Search Request"""
        searchTerm, ok = QInputDialog.getText(self, "Search Products", "Enter product search term:")

        if ok and searchTerm.strip():
            request = {"action": "searchProducts", "query": searchTerm.strip()}
        
            try:
                response = sendRequest(self.clientSocket, request)
            
                if response["status"] == "success" and response["products"]:
                    products_message = "Search Results:\n\n"
                
                    for product in response["products"]:
                        products_message += f"ID: {product['productId']}\n"
                        products_message += f"Name: {product['productName']}\n"
                        products_message += f"Description: {product['productDescription']}\n"
                        products_message += f"Price: ${product['productPrice']:.2f}\n"
                        products_message += f"Owner ID: {product['ownerId']}\n\n"
                 
                    self.showMessageBox("Search Results", products_message)
                else:
                    self.showMessageBox("No Results", "No products found matching your search.")
        
            except Exception as e:
                self.showMessageBox("Error", f"Search failed: {str(e)}")
        else:
            self.showMessageBox("Error", "Search term cannot be empty.")
    
    def handleAddRating(self): 
        
        productId, ok = QInputDialog.getInt(self, "Add Rating", "Enter Product ID:")
      
        if not ok:
            return
        
        rating, ok = QInputDialog.getInt(self, "Add Rating", "Enter a rating from 1 to 5:")
        
        if not ok:
            return

        request = {"action": "addRating", "productId": productId, "userId": self.userId, "rating": rating}

        response = sendRequest(self.clientSocket, request)
        self.showMessageBox("Add Rating", response.get('message', "Unknown error occurred."))

    def handleViewAverageRating(self): 
        
        productId, ok = QInputDialog.getInt(self, "View Average Rating", "Enter Product ID:")
        if not ok:
            return
        
        request = {"action": "viewAverageRating", "productId": productId}

        response = sendRequest(self.clientSocket, request)
        
        if response["status"] == "success": 
            averageRating = response.get("averageRating", 0.0)  
            self.showMessageBox("Average Rating", f"The average rating for product {productId} is {averageRating:.2f}")
            
        else: 
            self.showMessageBox("Error", f"An error occurred: {response.get('message', 'Unknown error')}")
            
    def handleGetBestSellers(self): 
        request = {"action": "getBestSellers"}

        try: 
            response = sendRequest(self.clientSocket, request)

            if response['status'] == 'success' and 'bestSellers' in response:
                
                bestSellersMessage = "Top 2 Best Sellers:\n\n"

                for product in response['bestSellers']: 
                    bestSellersMessage += f"Product ID: {product['productId']}\n"
                    bestSellersMessage += f"Product Name: {product['productName']}\n"
                    bestSellersMessage += f"Price: ${product['productPrice']:.2f}\n"
                    bestSellersMessage += "-" * 35 + "\n"
                self.showMessageBox("Best Sellers", bestSellersMessage)
                
            else: 
                self.showMessageBox("Error", response.get('message', "Unknown error occurred."))
                
        except Exception as e: 
            print(f"An error occured when getting the best sellers: {str(e)}")

                
    def updateMessageArea(self, message):
        if self.messageArea.toPlainText() == "Messages will appear here...":
            self.messageArea.clear()
        self.messageArea.append(message)
        self.messageArea.moveCursor(QTextCursor.End)

    def handleDisplayIncomingMessages(self):
        if messages:
            for message in messages:
                self.updateMessageArea(message)
            messages.clear()
        else:
            self.updateMessageArea("No new messages.")
    
    def listenForMessages(self,clientSocket):
        
        print("Listening for messages...")
        
        clientSocket.settimeout(5)
        
        while not self.stopListening:
            try:
                json_response = clientSocket.recv(1024).decode('utf-8')
               
                if json_response:
                    response = json.loads(json_response)
                    
                    if response['status'] == 'success' and 'from' in response and 'message' in response:
                        messages.append(f"Message from {response['from']}: {response['message']}")
            
            except socket.timeout:
                continue
            
            except Exception as e:
                print("An error occurred while receiving messages:", str(e))
                break

    def showMessageBox(self, title, message):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(QMessageBox.Information)
        msg.setStyleSheet("QLabel { font-size: 24px; color: #ff69b4; } QPushButton { font-size: 14px; }")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msg.exec_()


app = QApplication(sys.argv)
window = ClientApp()
window.show()
sys.exit(app.exec_())
