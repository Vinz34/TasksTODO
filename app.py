from flask import Flask, render_template, request, url_for, redirect, session
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from datetime import date
import secrets


current_date = date.today()

app = Flask(__name__)
# client = MongoClient('localhost', 27017)
# client = MongoClient('localhost', 27017, username='username', password='password')

client = MongoClient("mongodb+srv://Vinz:Vincent2003@cluster0.ge2mprs.mongodb.net/?retryWrites=true&w=majority")
db = client.test
users_collection = db.users

db = client.flask_db
todos = db.todos

app.secret_key = 'your_secret_key'
app.secret_key = secrets.token_hex(16)

app.permanent_session_lifetime = timedelta(minutes=10)


@app.route('/', methods=('GET', 'POST'))
def index():
    if 'username' in session:

        # Retrieve all todos from the database
        todos_ = db.todos.find()
        # Filter out the past tasks
        past_tasks = []
        # Updates dates based on the current date
        for todo in todos_:
            days_left = days_until(str(current_date), todo['date'])
            todo['days_left'] = days_left
            if todo['days_left'] < 0:
                past_tasks.append(todo)
        # Sort and reverse the order of the past tasks so that the most recent ones appear first
        past_tasks.sort(key=lambda x: x['date'])
        past_tasks.reverse()

        if request.method == 'POST':
            # Retrieve the form data
            content = request.form['content']
            degree = request.form['degree']
            date = request.form['date']
            # Calculate the number of days left until the task's due date
            days_left = days_until(str(current_date), date)

            # Insert the new task into the database
            todos.insert_one({'content': content, 'degree': degree, 'date': date, 'days_left': days_left})
            # Redirect to the home page
            return redirect(url_for('index'))

        all_todos = todos.find()
        # Update the days_left value for each todo task
        for todo in all_todos:
            days_left = days_until(str(current_date), todo['date'])
            db.todos.update_one({'_id': todo['_id']}, {'$set': {'days_left': days_left}})
        # Retrieve all tasks from the database
        all_todos = todos.find()
        # Render the home page template with the tasks and past tasks
        return render_template('index.html', todos=all_todos, current_date=current_date, past_tasks=past_tasks)
    else:
        return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Retrieve the form data
        username = request.form['username']
        password = request.form['password']
        # Check if the username and password are correct
        user = db.users.find_one({'username': username, 'password': password})
        if user:
            # Set the username in the session
            session['username'] = username
            # Set the session to be permanent
            session.permanent = True
            # Redirect to the index page
            return redirect(url_for('index'))
        else:
            # Display an error message if the username or password is incorrect
            return render_template('login.html', error='Invalid username or password')
    else:
        # Render the login page template
        return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Retrieve the form data
        username = request.form.get('username')
        password = request.form.get('password')
        # Check if the username already exists in the database
        if db.users.find_one({'username': username}):
            # Display an error message if the username already exists
            return render_template('register.html', error='Username already taken')
        else:
            # Insert the new user into the database
            db.users.insert_one({'username': username, 'password': password})
            # Redirect to the login page
            return redirect(url_for('login'))
    else:
        # Render the register page template
        return render_template('register.html')



@app.route('/logout')
def logout():
    # Clear the session
    session.clear()
    # Redirect to the login page
    return redirect(url_for('login'))




@app.post('/<id>/delete/')
def delete(id):
    """
    Deletes a todo item with the given ID.
    :param id: A string representing the ID of the todo item to delete
    :return: A redirect to the homepage ('index')
    """
    # Delete the todo item with the given ID
    todos.delete_one({"_id": ObjectId(id)})
    # Redirect the user to the homepage
    return redirect(url_for('index'))


def days_until(date1, date2):
    """
    Calculates the number of days between two dates.
    :param date1: A string representing the start date in the format YYYY-MM-DD
    :param date2: A string representing the end date in the format YYYY-MM-DD
    :return: An integer representing the number of days between the two dates
    """
    # Convert the string dates to datetime objects
    date1_obj = datetime.strptime(date1, '%Y-%m-%d')
    date2_obj = datetime.strptime(date2, '%Y-%m-%d')
    # Calculate the difference between the two dates and return the number of days
    days_left = (date2_obj - date1_obj).days
    return days_left


@app.route('/edit/<string:id>', methods=['GET', 'POST'])
# Define a route for the '/edit/<id>' URL path with the id parameter
def edit(id):
    # Define a function that takes in the id parameter
    todo = todos.find_one({'_id': ObjectId(id)})
    # Retrieve a single document from the 'todos' collection that matches the '_id' field with the 'id' parameter
    if request.method == 'POST':
        # Check if the HTTP request method is 'POST'
        degree = request.form['degree']
        # Extract the value of the 'degree' field from the form data submitted in the POST request
        date = request.form['date']
        # Extract the value of the 'date' field from the form data submitted in the POST request
        days_left = days_until(str(current_date), date)
        # Calculate the number of days between the current date and the date field using the 'days_until' function
        todos.update_one({'_id': ObjectId(id)},
                         {'$set': {'content': request.form['content'], 'degree': request.form['degree'], 'date': date,
                                   'days_left': days_left}})
        # Update the document in the 'todos' collection that matches the '_id' field with the 'id' parameter with the new values
        return redirect(url_for('index'))
        # Redirect the user to the 'index' page
    return render_template('edit.html', todo=todo)
    # If the HTTP request method is not 'POST', render the 'edit.html' template and pass in the 'todo' document


@app.route('/edit-profile', methods=['GET', 'POST'])
def edit_profile():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Retrieve the form data
        name = request.form['name']
        password = request.form['password']

        # Update the user's profile in the database
        db.users.update_one({'username': session['username']}, {'$set': {'name': name, 'password': password}})

        # Set the new username in the session
        session['name'] = name

        # Redirect to the index page
        return redirect(url_for('index'))

    # Retrieve the user's profile from the database
    user = db.users.find_one({'username': session['username']})

    # Render the edit profile page template
    return render_template('edit_profile.html', user=user)


@app.route('/delete-account', methods=['GET', 'POST'])
def delete_account():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Delete the user's account from the database
        db.users.delete_one({'username': session['username']})

        # Clear the session and redirect to the login page
        session.clear()
        return redirect(url_for('login'))

    # Render the delete account page template
    return render_template('delete_account.html')


@app.route('/profile')
def profile():
    # Retrieve the user's name from the session
    name = session.get('username')

    if name is None:
        # Redirect to the login page if the user is not logged in
        return redirect(url_for('login'))

    return render_template('profile.html', name=name)


if __name__ == '__main__':
    app.run()
