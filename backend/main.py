from flask import Flask, Response, redirect, request
from dotenv import load_dotenv
import os
from dataclasses import dataclass
import requests as req
from oauthlib.oauth2 import WebApplicationClient

server = Flask(__name__)

GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')

oauth = WebApplicationClient(client_id=GOOGLE_CLIENT_ID)

@dataclass
class GoogleHosts:
    authorization_endopoint: str
    token_endpoint: str
    userinfo_endpoint: str
    cert: str

def get_google_oauth_hosts() -> GoogleHosts:
    hosts = req.get('https://accounts.google.com/.well-known/openid-configuration')
    if hosts.status_code != 200:
        raise Exception('Não foi possível recuperar os endpoints de autenticação do Google')
    
    data = hosts.json()
    
    return GoogleHosts(authorization_endopoint=data.get('authorization_endpoint'),
                       token_endpoint=data.get('token_endpoint'),
                       userinfo_endpoint=data.get('userinfo_endpoint'),
                       cert=data.get('jwks_uri'))

@server.route('/auth/login', methods=['GET'])
def login() -> Response:
    hosts = get_google_oauth_hosts()
    redirect_uri = oauth.prepare_authorization_request(authorization_url=hosts.authorization_endopoint,
                                                       redirect_url='https://localhost:8081/auth/callback',
                                                       scope=['openid', 'email', 'profile'])
    return redirect(redirect_uri[0])

@server.route('/auth/callback')
def callback() -> Response:
    code = request.args.get('code')
    hosts = get_google_oauth_hosts()

    token_url, headers, body = oauth.prepare_token_request(
        hosts.token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = req.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_SECRET),
    )
    oauth.parse_request_body_response(token_response.text)

    userinfo_endpoint = hosts.userinfo_endpoint
    uri, headers, body = oauth.add_token(userinfo_endpoint)
    userinfo_response = req.get(uri, headers=headers, data=body)
    user_info = userinfo_response.json()

    user_name = user_info['name']
    user_email = user_info['email']

    # Redirecionar para o servidor de front-end com as informações do usuário
    return redirect(f'https://localhost:8080/profile?user_name={user_name}&user_email={user_email}')

if __name__ == "__main__":
    server.run(port=8081, debug=True, ssl_context='adhoc')
