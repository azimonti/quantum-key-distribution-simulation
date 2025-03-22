import json
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import logging

with open('config.json', 'r') as f:
    cfg = json.load(f)

app = Flask(cfg['APP_NAME'])
app.config['SECRET_KEY'] = cfg['SECRET_KEY']
log_level = logging.INFO if cfg['VERBOSE'] else logging.ERROR

logging.basicConfig(
    level=log_level,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%d/%b/%Y %H:%M:%S"
)
logger = logging.getLogger()
socketio = SocketIO(app)


@app.route('/')
def index():
    logger.info("Index route called")
    return render_template('index.html')


def encode_message(message, encryption):
    if encryption == "BB84 Protocol":
        return f"ENC[BB84]{message}"
    elif encryption == "Ekert Protocol":
        return f"ENC[Ekert]{message}"
    return message  # No encryption


def decode_message(message, encryption):
    if message.startswith("ENC[BB84]"):
        return message[len("ENC[BB84]"):]
    elif message.startswith("ENC[Ekert]"):
        return message[len("ENC[Ekert]"):]
    return message  # No encryption


def eve_encode_decode_message(message, encryption):
    if message.startswith("ENC[BB84]"):
        return message[len("ENC[BB84]"):]
    elif message.startswith("ENC[Ekert]"):
        return message[len("ENC[Ekert]"):]
    return message  # No encryption


@socketio.on("alice_key")
def handle_alice_key(data):
    if data["eavesdropping"]:
        logger.info("Eve is eavesdropping the key")
    else:
        logger.info("Eve isn't eavesdropping the key")
    emit("key_sent", {"encryption": data["encryption"],
                      "eavesdropping": data["eavesdropping"]}, broadcast=True)


@socketio.on("reconcile_key")
def handle_reconcile_key(data):
    reconciled = True
    logger.info(f"Key reconciled: {reconciled}")
    emit("key_reconciled", {"encryption": data["encryption"],
                            "reconciled": reconciled}, broadcast=True)


@socketio.on("alice_message")
def handle_alice(data):
    encoded_message = encode_message(data["message"], data["encryption"])
    logger.info(f"Alice sent: {encoded_message}")
    if data["eavesdropping"]:
        emit("eve_receive_encrypted", {
            "message": encoded_message, "encryption": data["encryption"],
            "sender": "Alice"}, broadcast=True)
    emit("bob_receive_encrypted", {
        "message": encoded_message, "encryption": data["encryption"]},
        broadcast=True)


@socketio.on("bob_decode")
def handle_bob_encrypted(data):
    decoded_message = decode_message(data["message"], data["encryption"])
    logger.info(f"Bob received encrypted: {decoded_message}")
    emit("bob_receive", {"message": decoded_message}, broadcast=True)


@socketio.on("eve_decode")
def handle_eve_encrypted(data):
    decoded_message = decode_message(data["message"], data["encryption"])
    logger.info(f"Bob received encrypted: {decoded_message}")
    emit("eve_receive", {"message": decoded_message}, broadcast=True)


if __name__ == '__main__':
    socketio.run(app, debug=True, use_reloader=True)
