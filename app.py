from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from pymongo import MongoClient
from datetime import datetime

cluster = MongoClient("mongodb+srv://ummi:DISLG29FS3woGPED@cluster0.0xfl2rq.mongodb.net/?retryWrites=true&w=majority")
db = cluster["bakery"]
users = db["users"]
orders = db["orders"]

app = Flask(__name__)

@app.route("/", methods=["get" , "post"])

def reply():
    text = request.form.get("Body")
    number = request.form.get("From")
    number = number.replace("whatsapp:" , "")

    response = MessagingResponse()

    user = users.find_one({"number" : number})

    if bool(user) == False :
        response.message("Hi Thanks for connecting *testsaathi*.\nYou have to choose from one option given below: \n1️⃣ Contact Us\n2️⃣ To *Order* Snakes\n3️⃣ To Know *About Us*\n4️⃣ To Get out *Address*")
        users.insert_one({"number" : number , "status":"main" , "messages" : []})
    elif user["status"] == "main" :
        try: 
            option = int(text)
        except:
            response.message("please enter a valid response")
            return str(response)

        if option == 1 :
            response.message("You can contact Us on +91-9817294314 and testsaathi@gmail.com")
        elif option == 2 : 
            response.message("You have entered *ordering mode*")
            users.update_one({"number":number} , {"$set" : {"status" : "ordering"}})
            response.message("Please select any one item from here :  \n1️⃣ Red Velvet\n2️⃣ Dark Forest\n3️⃣ Angel Cake\n4️⃣ Fruit Cake \n0️⃣ Go Back")
        elif option == 3 :
            response.message("We are working from *9AM to 6PM*")
        elif option == 4 :
            response.message("We are operating from *Kota, Rajasthan*")
        else :
            response.message("please enter a valid response")
    elif user["status"] == "ordering" :
        try: 
            option = int(text)
        except:
            response.message("please enter a valid response")
            return str(response)
        
        if option == 0 :
            users.update_one({"number":number} , {"$set" : {"status" : "main"}})
            response.message("Hi Thanks for connecting *testsaathi*.\nYou have to choose from one option given below: \n1️⃣ Contact Us\n2️⃣ To *Order* Snakes\n3️⃣ To Know *About Us*\n4️⃣ To Get out *Address*")
        elif 1 <= option <= 4 :
            cakes = ["Red Velvet" , "Dark Forest" , "Angel Cake" , "Fruit Cake" ]
            selected = cakes[option-1]
            users.update_one({"number":number} , {"$set" : {"status" : "address"}})
            users.update_one({"number":number} , {"$set" : {"item" : selected}})
            response.message("Excellent Choice 👌")
            response.message("Please enter your address to confirm the order")
        else :
            response.message("please enter a valid response")   
    elif user["status"] == "address" :
        selected = user["item"]
        response.message("Thanks from Ordering from Us")
        response.message(f"Your order {selected} has been delivered within 20 min")
        orders.insert_one({"number" : number , "item" : selected , "address": text , "order_time" : datetime.now()})
        users.update_one({"number":number} , {"$set" : {"status" : "ordered"}})
    elif user["status"] == "ordered" :
        response.message("Hi Thanks for connecting *testsaathi* Again.\nYou have to choose from one option given below: \n1️⃣ Contact Us\n2️⃣ To *Order* Snakes\n3️⃣ To Know *About Us*\n4️⃣ To Get out *Address*")
        users.update_one({"number":number} , {"$set" : {"status" : "main"}})
    # msg = response.message(f"Hey {text} and number {number}")
    # msg.media()

    users.update_one({"number" : number} , {"$push" : {"messages": {"text": text , "date" : datetime.now()}}})

    return str(response)

if __name__ == "__main__":
    app.run()

# nodemon --watch "main.py" --exec "lt --subdomain umesh --port 5000" --delay 2 
# we have to run this command to connect out 5000 port online/make available online 
