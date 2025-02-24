from config.Config import SERVER_CRT, SERVER_KEY
from handlers.Handlers import app
from threading import Thread

app.run(debug=False, host="0.0.0.0", port=8443, ssl_context=(SERVER_CRT, SERVER_KEY))
