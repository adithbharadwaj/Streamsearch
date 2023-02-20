import secrets
from routes import app


if __name__ == '__main__':
    app.secret_key = secrets.token_bytes(32)

    app.debug = True
    app.run(host='0.0.0.0')
