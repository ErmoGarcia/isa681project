from flask import Flask
app = Flask(__name__)

@app.route('/')
def welcome():
    return 'Welcome!'

@app.route('/example')
def example():
    return 'This is an example'
