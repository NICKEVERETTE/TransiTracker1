#Author:                Trevor Strobel

from flask import request, render_template, flash, redirect, url_for
from transitracker import app, db, bcrypt
from transitracker.forms import CreateAccountForm, LoginForm, EmployeeSearchForm, CreateItemForm
from transitracker.models import Employee, Item, Transaction, employeeCols, itemCols, transactionCols
from flask_login import login_user,  logout_user, current_user



#------------------------------Account Routes--------------------------------

#default page
@app.route("/", methods=["GET", "POST"])
#Login Page
@app.route("/login", methods=["GET", "POST"])
def login():
    #redirect when logged in
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm() #loads the form from forms.py


    if form.validate_on_submit():
        user = Employee.query.filter_by(email=form.email.data).first() #grabs first entry with that email

        #TODO: Flask throws an error when the wrong password is given instead of just saying "wrong password".
        #if the user exists and the password matches the hashed password in the db
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('dashboard'))
        else:
            flash('Login attempt unsuccessful. Check Email and Password', 'danger')

    return render_template('login.html', title='Login', form = form)


#Create Account Page
@app.route("/createAccount", methods=["GET", "POST"])
def createAccount():
    #redirect when logged in
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = CreateAccountForm() #loads the form from forms.py
    if form.validate_on_submit():
        #hash the password from the form to store in the db
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        user = Employee(firstName=form.firstName.data, lastName=form.lastName.data, email=form.email.data, password = hashed_password)

        db.session.add(user)
        db.session.commit()

        #flash a message on successful create
        flash(f'Account Created for {form.firstName.data} {form.lastName.data}. You may now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('create_account.html', title='Create Account', form = form)



#Log out user
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))




#------------------------------Dashboard Routes--------------------------------
#Dashboard page
@app.route("/dashboard")
def dashboard():
    #redirect user if they're not logged in
    if not(current_user.is_authenticated):
        return redirect(url_for('login'))

    #TODO: fetch last 10 transactions and return with render_template
    #TODO: fetch items that need attention from inventory (below or near threshold). return with render_template
   
    return render_template('dashboard.html', title ='Dashboard') # alertInv = alertInventory, recentTrans = recentTransactions)


#------------------------------Inventory Routes--------------------------------
#Inventory Page
@app.route("/inventory")
def inventory():
    #redirect user if they're not logged in
    if not(current_user.is_authenticated):
        return redirect(url_for('login'))

    inventory = Item.query.with_entities(Item.name, Item.inStock, Item.threshold, Item.vendor).all()
    print(inventory)
    return render_template('inventory.html', title='Inventory', column_html=itemCols,  data_html = inventory)

@app.route("/createItem", methods=['GET', 'POST'])
def createItem():
    #redirect user if they're not logged in
    if not(current_user.is_authenticated):
        return redirect(url_for('login'))
    #load form
    form = CreateItemForm()

    if form.validate_on_submit():
        #submit the data to the database
        #create item object that represents a row in the Item table. 
        item = Item(name=form.name.data, inStock=form.inStock.data, threshold=form.threshold.data, vendor=form.vendor.data)

        #add and commit the new item object.
        db.session.add(item)
        db.session.commit()

        #flash a message on successful create
        flash(f'Item  {form.name.data} created. ', 'success')
        return redirect(url_for('inventory'))
    


    return render_template('create_item.html', title='Create Item', form = form)




#------------------------------Transaction Routes--------------------------------
#Transaction Page
@app.route("/transactions")
def transactions():
    #redirect user if they're not logged in
    if not(current_user.is_authenticated):
        return redirect(url_for('login'))

    transactions = Transaction.query.all()
    return render_template('transactions.html', title='Transactions', data = transactions)


#------------------------------Employee Routes--------------------------------
#Employees Page
@app.route("/employees", methods=["GET", "POST"])
def employees():
    #redirect user if they're not logged in
    if not(current_user.is_authenticated):
        return redirect(url_for('login'))

    #define the search form
    search = EmployeeSearchForm()
    #Define Default search params (All employees)
    users = Employee.query.with_entities(Employee.firstName, Employee.lastName, Employee.email).all()
    
    #if the user submits a search, search the db for users with first or last name that matches.
    if search.validate_on_submit(): #check for form validation (in this case, just need any input)
        
        if search.searchBtn.data:  # if the searchBtn is pressed...
            
            param = search.searchStr.data #search parameters

            #first we get all entries that match first name, then last name.
            users = Employee.query.with_entities(Employee.firstName, Employee.lastName, Employee.email).filter(Employee.firstName.like(param)).all()
            users2 = Employee.query.with_entities(Employee.firstName, Employee.lastName, Employee.email).filter(Employee.lastName.like(param)).all()
            
            #add the two lists together
            for user in users2:
                users.append(user)

            #TODO: remove duplicates if there's time. 
            #TODO: maybe use REGEX
            

    
    print(users)
    return render_template('employees.html', title='Employees', column_html = employeeCols, data_html = users, search = search) 

#Employee Edit Page
@app.route("/editEmployee", methods=["GET", "POST"])
def editEmployee():
    return render_template('employees.html', title='Employees', column_html = employeeCols, data_html = users, search = search) 
