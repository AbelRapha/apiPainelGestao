from flask import Flask, render_template, request

server = Flask(__name__)

@server.route('/', methods=['GET'])
def index() -> str:
    return render_template('index.html')

@server.route('/profile', methods=['GET'])
def profile() -> str:
    user_name = request.args.get('user_name')
    user_email = request.args.get('user_email')
    return render_template('profile.html', user_name=user_name, user_email=user_email)

if __name__ == "__main__":
    server.run(port=8080, debug=True, ssl_context='adhoc')
