from pymongo import MongoClient
from flask import Flask, request, jsonify, redirect, Response, render_template
from pymongo.errors import DuplicateKeyError
from datetime import date
import json
import os

#1.  Connect  MongoDB Database
mongodb_hostname = os.environ.get("MONGO_HOSTNAME", "localhost")
client = MongoClient('mongodb://'+mongodb_hostname+':27017/')

# Choose application database
db = client["DSMarkets"]
users = db["users"]
products = db["products"]
cart=db["cart"]

# Begin Flask App
app = Flask(__name__)


@app.route("/")
def main_page():
    return render_template("base.html")

#2.  Insert new user
@app.route("/user_insertion", methods=["POST", "GET"])
def user_insert():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        if not name or not email or not password:
            return Response("Fields are required", status=500, mimetype="application/json")

        users_find_email = list(users.find({"email": email}))

        if len(users_find_email) == 0:
         #   get_all_users = list(users.find({}))
            

            

            user = {"name": name,
                    "email": email,
                    "password": password,
                    "orderHistory": [],
                    "connected": False,
                    }

            users.insert_one(user)

            return Response("New user was added to DSMarkets DB successfully", status=200, mimetype='application/json')
        else:
            return Response("This user already exists in DSMarkets DB", status=200, mimetype='application/json')

    return render_template("user_insertion.html")
#--------------------------------------------------------------------------------------------------
#3. User connection
@app.route("/user_connection", methods=["POST","GET"])
def user_connect():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        if not email or not password:
            return Response("Users email and password are required", status=500, mimetype="application/json")
        user=users.find_one({"email": email, "password": password})
        if user!=None:
            users.update_one(
                {"email": email, "password": password},
                {"$set":
                    {
                        "connected": True,
                    }
                 }
            )

            return Response("User connected successfully", status=500, mimetype="application/json")
        else:
            return Response("The values in the fields - email,password-  are not correct", status=500, mimetype="application/json")

    return render_template("user_connection.html")
#------------------------------------------------------------------------------------------------------------------
#4.  Search product by code
@app.route("/find_product_with_name", methods=["POST", "GET"])
def find_product_by_name():
    if request.method == "POST":
        email = request.form["email"]
        name = request.form["name"]

        if not email or not name :
            return Response("Values in email and name are required", status=500, mimetype='application/json')

        user = users.find_one({"email": email})
	
        found_product = list(products.find({"name": name}))

	
        if user == None:
            return Response("No user found with the given email " + email, status=500, mimetype="application/json")

        if len(found_product) == 0:
            return Response("No product found with the name " + name, status=500, mimetype="application/json")

        connected = user["connected"]==True

        if not connected:
            return Response("You must connect to search a product by name", status=500, mimetype="application/json")

    

        
        

        

        return render_template("find_product_with_name.html",found_product=found_product)
    else:
     found_product=None   
     return render_template("find_product_with_name.html")  
#-----------------------------------------------------------------------------------------
#5.  Search product by category
@app.route("/find_product_with_category", methods=["POST", "GET"])

def find_product_by_category():
    if request.method == "POST":
        email = request.form["email"]
        category = request.form["category"]

        if email == None or category == None:
            return Response("Values in email and category are required", status=500, mimetype='application/json')

        user = users.find_one({"email": email})
	
        found_products = list(products.find({"category": category}))
	

	
        if user == None:
            return Response("No user found with the given email " + email, status=500, mimetype="application/json")

        if len(found_products) == 0:
            return Response("No products found with the category " + category, status=500, mimetype="application/json")

        connected = user["connected"]==True

        if not connected:
            return Response("You must connect to search a product by category", status=500, mimetype="application/json")

    
        return render_template("find_product_with_category.html",found_products=found_products)
    else:
      found_product=None   
      return render_template("find_product_with_category.html") 
        
        

        

    

#-------------------------------------------------------------------------------------------
#6.  Search product by code
@app.route("/find_product_with_code", methods=["POST", "GET"])

def find_product_by_code():
    if request.method == "POST":
        email = request.form["email"]
        code = request.form["code"]

        if email == None or code == None:
            return Response("Values in email and product code are required", status=500, mimetype='application/json')

        user = users.find_one({"email": email})
	
        found_product = list(products.find({"code": code}))
	

	
        if user == None:
            return Response("No user found with the given email " + email, status=500, mimetype="application/json")

        if len(found_product) == 0:
            return Response("No product found with the given code " + code, status=500, mimetype="application/json")

        connected = user["connected"]

        if not connected:
            return Response("You must connect to search a product by category", status=500, mimetype="application/json")

    

        
        return render_template("find_product_with_code.html",found_product=found_product)
    else:
        found_product=None   
        return render_template("find_product_with_code.html") 

       


#-------------------------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------
#7.  Insert new product
@app.route("/product_insertion", methods=["POST", "GET"])
def insert_product():
    if request.method == "POST":
        email = request.form["email"]
        code = request.form["code"]

        admin=False
        
        if email == None:
            return Response("User email is required", status=500, mimetype='application/json')

        user = users.find_one({"email": email})

        if (user == None):
            return Response("No user found with the email " + email, status=500, mimetype="application/json")
        else:
            admin = user["category"]=="admin"

        if admin==False:
            return Response("You have not administrator priviledges to perform product insertion", status=500, mimetype="application/json")

    
        else:
            name = request.form["name"]
            price = float(request.form["price"]);
            description = request.form["description"]
            category = request.form["category"]
            stock = int(request.form["stock"])
            code = request.form["code"]
        
            if not name or not price or not description or not category or not stock or not code:
                return Response("You must insert values in all fields to perform product insertion", status=500, mimetype="application/json")

        
            product = {"name": name,
                 "price": price,
                 "description": description,
                 "category": category,
				 "stock": stock,
                 "code":code
				 }

            products.insert_one(product)

            return Response("The new product successfully added in Database", status=200, mimetype='application/json')
    
    return render_template("product_insertion.html")

#-----------------------------------------------------------------------------------------------------------------
#8.  Delete a product
@app.route("/product_delete", methods=["POST", "GET","DELETE"])
def delete_product():
    if request.method=="POST":
        email = request.form["email"]
        code = request.form["code"]


        if email == None or code == None:
            return Response("All values in the fields are required", status=500, mimetype="application/json")

        user = users.find_one({"email": email})
        found_product =products.find_one({"code": code})

        if user == None:
            return Response("No user found with the email " + email, status=500, mimetype="application/json")

        

        admin = user["category"]=="admin"

        if not admin:
            return Response("You have not the priviledge to perform the deletion operation", status=500, mimetype="application/json")

        if found_product == None:  
            return Response("No product found with the given code " +code, status=500, mimetype="application/json")
        else:    
            index= found_product["_id"]
        

            products.delete_one({"_id": index})
        
            return Response("The product deleted successfully from Database", status=500, mimetype="application/json")
    if request.method=="GET":
        found_product=None   
        return render_template("product_delete.html")    
    else:
        found_product=None 
        return render_template("product_delete.html")      
#-----------------------------------------------------------------------------------------------------------------
#9. Update a product 
@app.route("/product_update", methods=["POST", "GET"])
def update_product():
    if request.method=="POST":
        email = request.form["email"]
        code = request.form["code"]
        name = request.form["name"]
        
        if name=='':
            if email == None or code == None:
                return Response({"Values are required!!!"}, status=500, mimetype="application/json")

            user = users.find_one({"email": email})
            product = products.find_one({"code": code})

            if user == None:
                return Response("No user found with the given email " + email, status=500, mimetype="application/json")

            if product == None:
                return Response("No product found in DataBase with the name " + name, status=500, mimetype="application/json")

            admin = user["category"]=="admin"

            if not admin:
                return Response("You have not the permission to perform update operation", status=500, mimetype="application/json")

            return render_template("product_update.html",product=product)


        else:
            code = request.form["code"]
            name = request.form["name"]
            price = float(request.form["price"])
            description = request.form["description"];
            category = request.form["category"];
            stock = int(request.form["stock"])

       

            if not name or not price or not description or not category or not stock:
                return Response("Values in all the are required!!!!", status=500, mimetype="application/json")

        
            products.update_one(
        {"code": code},
            {"$set":
                {
                    "name": name,
                    "price": price,
                    "description": description,
                    "category": category,
					"stock": stock
                }
             }
        )

        return Response("The product with name:"+name + "  updated in the Database successfully", status=200, mimetype='application/json')
    if request.method=="GET":
         product=None
         return render_template("product_update.html",product=product)

#----------------------------------------------------------------------------------------------------------
#10.  Make a simple-user admin
@app.route("/create_new_admin", methods=["POST", "GET"])
def admin_creation():
    if request.method=="POST":
        email = request.form["email"]
        password=request.form["password"]
        user_name = request.form["name"]
        if email == None or password==None:
            return Response("Your email and password are  needed to perform  new admin action", status=500, mimetype='application/json')

        user = users.find_one({"email": email,"password":password})

        if user == None:
            return Response("Wrong email address or password.Try again!!!! " + email, status=500, mimetype="application/json")

        admin = user["category"]=="admin"

        if not admin:
            return Response("You are not permitted to perform new admin action", status=500, mimetype="application/json")

    
        
    

        if not email or not user_name or not password:
            return Response("Values in all the fields are requested", status=500, mimetype="application/json")

        if users.find_one({"name":user_name}):
            users.update_one(
                {"name": user_name},
                {"$set":
                    {
                        "admin": True,
                    }
                 }
            )

        return Response("The user with user name:"+user_name +" is now administrator", status=200, mimetype='application/json')

    return render_template("create_new_admin.html")

#11.  add a product to shopping cart
@app.route("/add_product_to_cart", methods=["POST", "GET"])
def cart_add():
    if request.method=="POST":
        email = request.form["email"]
        code=request.form["code"]
        items=int(request.form["items"])
        
        if email == None or code==None or items==None:
            return Response("Your email, product code and quantity are  needed to perform  new admin action", status=500, mimetype='application/json')

        user = users.find_one({"email": email})

        if user == None:
            return Response("Wrong email address.Try again!!!! " + email, status=500, mimetype="application/json")
        connected = user["connected"]

        if not connected:
            return Response("Not connected, connect first and try again", status=500, mimetype="application/json")
        admin = user["category"]=="admin"

        if admin:
            return Response("You are not permitted shop products", status=500, mimetype="application/json")

    
        
    

        if not email or not code or not items:
            return Response("Values in all the fields are requested", status=500, mimetype="application/json")

        search_product=products.find_one({"code":code})
        if search_product==None:
            return Response("The selected product with code:"+code+" doesnt exist in shop", status=500, mimetype="application/json")
        else:
            if int(search_product["stock"])>items:
                total=items*float(search_product["price"])
                add_to_cart = {"user_email": user["email"],
                 "date":str(date.today()),
                 "product_code": search_product["code"],
                 "quantity": items,
                 "value": total
				 
				 }
                new_stock=int(search_product["stock"])-items
                products.update_one(
                    {"code": code},
                    {"$set":
                    {
                        "stock":new_stock ,
                    }
                    })
                cart.insert_one(add_to_cart)


                return Response("The product with code:"+code+" added to users cart(items="+str(items)+")--Value="+str(total), status=200, mimetype='application/json')
            else:
                return Response("The product isnt existed with enough items in DB", status=200, mimetype='application/json')
    return render_template("add_product_to_cart.html")
#-------------------------------------
#12.  delete a product from shopping cart
@app.route("/delete_product_from_cart", methods=["POST", "GET"])
def cart_del():
    if request.method=="POST":
        email = request.form["email"]
        code=request.form["code"]
        
        
        if email == None or code==None :
            return Response("Your email and product code  are  needed to perform  new admin action", status=500, mimetype='application/json')

        user = users.find_one({"email": email})

        if user == None:
            return Response("Wrong email address.Try again!!!! " + email, status=500, mimetype="application/json")

        connected = user["connected"]

        if not connected:
            return Response("Not connected, connect first and try again", status=500, mimetype="application/json")

        
        admin = user["category"]=="admin"

        if admin:
            return Response("You are not permitted shop products", status=500, mimetype="application/json")

    
        
    

        if not email or not code :
            return Response("Values in all the fields are requested", status=500, mimetype="application/json")
        d=str(date.today())
        
        search_product=cart.find_one({"$or":[{"code":code},{"date":d},{"email":email}]})
        if search_product==None:
            return Response("The selected product with code:"+code+" doesnt exist in the current cart", status=500, mimetype="application/json")
        else:
                index= search_product["_id"]
                search_product1=products.find_one({"code":code})
                new_stock=str(int(search_product["quantity"])+int(search_product1["stock"]))
                products.update_one(
                    {"code": code},
                    {"$set":
                    {
                        "stock": new_stock,
                    }
                    })
                cart.delete_one({"_id": index})
                


                return Response("The product with code:"+code+" deleted from users current cart", status=200, mimetype='application/json')
            
    return render_template("delete_product_from_cart.html")
#13 show user's cart history
@app.route("/show_cart_history", methods=["GET","POST"])
def show_all_from_cart():

    if request.method=="POST":
        email = request.form["email"]

        user = users.find_one({"email": email})

        if user == None:
            return Response("No user found with the email " + email, status=500, mimetype="application/json")

        connected = user["connected"]

        if not connected:
           return Response("Not connected, connect first and try again", status=500, mimetype="application/json")

        cart_history = list(cart.find({"user_email":email}))

        return render_template("show_cart_history.html", cart_history=cart_history)
    else:

        cart_history=None   
        return render_template("show_cart_history.html")

#14.  Delete a  user from DB
@app.route("/user_delete", methods=["POST", "GET"])
def user_del():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        if not name or not email or not password:
            return Response("Fields are required", status=500, mimetype="application/json")

        users_find_email = users.find_one({"email": email})

        if users_find_email!=None:
         
            
            index=users_find_email["_id"]
            

            users.delete_one({"_id": index})

            return Response("The user:"+name+" deleted himself from DSMarkets DB successfully", status=200, mimetype='application/json')
        else:
            return Response("This user doesn't exist in DSMarkets DB", status=200, mimetype='application/json')

    return render_template("user_delete.html")

# Run Flask App
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

{
    // Use IntelliSense to learn about possible attributes.
    // Hover to view descriptions of existing attributes.
    // For more information, visit: https://go.microsoft.com/fwlink/?linkid=830387
    "version": "0.2.0",
    "configurations": [

        

        
        
        {
            "name": "Python: Flask",
            "type": "python",
            "request": "launch",
            "module": "flask",
            "env": {
                "FLASK_APP": "app.py",
                "FLASK_ENV": "development"
            },
            "args": [
                "run",
                "--no-debugger"
            ],
            "jinja": true
        }
    ]
}

