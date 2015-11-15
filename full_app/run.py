from app import app
from app.central_server import central_server_app

#central_server_app.run(
#    host="0.0.0.0",
#    port=5003,
#    debug=True
#)
app.run(
    host="0.0.0.0",
    port=5000,
    debug=True
)
