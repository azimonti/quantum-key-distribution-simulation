'''
/***************/
/*   app.py    */
/* Version 1.0 */
/*  2025/03/23 */
/***************/
'''
import base64
import json
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import logging
from types import SimpleNamespace
from encryptlib import NoEncryption

with open('config.json', 'r') as f:
    cfg = json.load(f, object_hook=lambda d: SimpleNamespace(**d))

cache = SimpleNamespace(protocol=None)

app = Flask(cfg.APP_NAME)
app.config['SECRET_KEY'] = cfg.SECRET_KEY
log_level = logging.INFO if cfg.VERBOSE else logging.ERROR

logging.basicConfig(
    level=log_level,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%d/%b/%Y %H:%M:%S"
)
logger = logging.getLogger()
socketio = SocketIO(app)


def init_protocol(encryption):
    cache.protocol = encryption
    if encryption == "No Protocol":
        cache.enc = NoEncryption(cfg.NoEncryption)
        cache.enc.generateKey()
    elif encryption == "BB84 Protocol":
        # TODO
        pass
    elif encryption == "Ekert Protocol":
        # TODO
        pass


def check_protocol(encryption):
    print(cache.protocol)
    print(encryption)
    return encryption == cache.protocol


def encode_message(message, encryption):
    if not check_protocol(encryption):
        logger.warning(f"Invalid protocol {encryption}")
        return (f"Invalid protocol \"{encryption}\" - expecting "
                f"{cache.protocol}")
    if encryption == "No Protocol":
        cache.enc_message = cache.enc.encrypt(message)
        # convert to b64 for display
        message = base64.b64encode(cache.enc_message).decode()
    elif encryption == "BB84 Protocol":
        message = f"ENC[BB84]{message}"
    elif encryption == "Ekert Protocol":
        message = f"ENC[Ekert]{message}"
    return message


def decode_message_bob(message, encryption):
    if not check_protocol(encryption):
        logger.warning(f"Invalid protocol {encryption}")
        return (f"Invalid protocol \"{encryption}\" - expecting "
                f"{cache.protocol}")
    if encryption == "No Protocol":
        message = cache.enc.decrypt(cache.enc_message)
    elif encryption == "BB84 Protocol":
        message = message[len("ENC[BB84]"):]
    elif encryption == "Ekert Protocol":
        message = message[len("ENC[Ekert]"):]
    return message


def decode_message_eve(message, encryption):
    if not check_protocol(encryption):
        logger.warning(f"Invalid protocol {encryption}")
        return (f"Invalid protocol \"{encryption}\" - expecting "
                f"{cache.protocol}")
    if encryption == "No Protocol":
        message = cache.enc.decrypt(cache.enc_message)
    elif encryption == "BB84 Protocol":
        message = message[len("ENC[BB84]"):]
    elif encryption == "Ekert Protocol":
        message = message[len("ENC[Ekert]"):]
    return message


@app.route('/')
def index():
    logger.info("Index route called")
    return render_template('index.html')


@socketio.on("alice_key")
def handle_alice_key(data):
    # initialize the key
    init_protocol(data["encryption"])
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
    emit("eve_receive_encrypted", {
        "message": encoded_message, "encryption": data["encryption"],
        "sender": "Alice"}, broadcast=True)
    emit("bob_receive_encrypted", {
        "message": encoded_message, "encryption": data["encryption"]},
        broadcast=True)


@socketio.on("bob_decode")
def handle_bob_encrypted(data):
    decoded_message = decode_message_bob(data["message"], data["encryption"])
    logger.info(f"Bob decrypt message: {decoded_message}")
    emit("bob_receive", {"message": decoded_message}, broadcast=True)


@socketio.on("eve_decode")
def handle_eve_encrypted(data):
    if data['eavesdropping']:
        message = decode_message_eve(data["message"], data["encryption"])
        logger.info(f"Eve decrypt message: {message}")
    else:
        message = 'Evesdropping disabled'
        logger.info(f"Eve can't decrypt message: {message}")
    emit("eve_receive", {"message": message}, broadcast=True)


if __name__ == '__main__':
    socketio.run(app, debug=True, use_reloader=True)
