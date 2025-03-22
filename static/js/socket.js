var socket = io()

function updateLog(sender, content) {
  const log = document.getElementById("logArea")
  log.innerHTML += `<div><strong>${sender}:</strong> ${content}</div>`
  log.scrollTop = log.scrollHeight
}

// Alice sends a key
function sendAliceKey() {
  updateLog('Alice', 'send Key: ' + getEncryptionModel() + ' - eavesdropping: ' + isEavesdroppingEnabled())
  socket.emit("alice_key", { encryption: getEncryptionModel(), eavesdropping: isEavesdroppingEnabled() })
}

// Listen for key to be sent
socket.on("key_reconciled", (data) => {
  updateLog('Alice', 'sent key: ' + data.encryption + ' - eavesdropping: ' + data.eavesdropping)
})

// Alice asking to reconcile the key
function reconcileKey() {
  updateLog('Alice + Bob', 'Key reconciliation: ' + getEncryptionModel() + ' - eavesdropping: ' + isEavesdroppingEnabled())
  socket.emit("reconcile_key", { encryption: getEncryptionModel(), eavesdropping: isEavesdroppingEnabled() })
}

// Listen for key reconciliation to complete
socket.on("key_reconciled", (data) => {
  updateLog('Alice', 'reconciled key: ' + data.reconciled)
})

// Alice sends a message
function sendAliceMessage() {
  const message = document.getElementById("aliceInput").value
  updateLog('Alice', 'send Message: ' + message + ' - model: ' + getEncryptionModel() + ' - eavesdropping: ' + isEavesdroppingEnabled())
  socket.emit("alice_message", { message, encryption: getEncryptionModel(), eavesdropping: isEavesdroppingEnabled() })
}

// Listen for Bob receiving a message
socket.on("bob_receive_encrypted", (data) => {
  updateLog('Bob', 'received encrypted: ' + data.message)
  document.getElementById("bobReceivedEncrypted").value = data.message
})

// Bob decodes a message
function decodeBobMessage() {
  const message = document.getElementById("bobReceivedEncrypted").value
  updateLog('Bob', 'decode: ' + message)
  socket.emit("bob_decode", { message, encryption: getEncryptionModel() })
}

// Listen for Bob receiving a message
socket.on("bob_receive", data => {
  updateLog('Bob', 'received decoded: ' + data.message)
  document.getElementById("bobDecoded").value = data.message
})

// Eve is eavesdropping
socket.on("eve_receive_encrypted", (data) => {
  updateLog('Eve', 'received encrypted: ' + data.message)
  document.getElementById("eveEavesdrop").value = data.message
  socket.emit("eve_received_encrypted", data)
})

// Eve decodes a message
function decodeEveMessage() {
  const message = document.getElementById("eveEavesdrop").value
  updateLog('Eve', 'decode: ' + message)
  socket.emit("eve_decode", { message, encryption: getEncryptionModel() })
}

// Listen for Eve receiving a message
socket.on("eve_receive", data => {
  updateLog('Eve', 'received decoded: ' + data.message)
  document.getElementById("eveDecoded").value = data.message
})

function getEncryptionModel() {
  return document.getElementById("encryptionModel").value
}

function isEavesdroppingEnabled() {
  return document.getElementById("eavesdropping").checked
}
