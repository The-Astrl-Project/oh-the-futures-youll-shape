/**
 * Copyright (c) 2024 Astrl.
 *
 * This file is part of oh-the-futures-youll-shape. It is subject to the license terms in
 * the LICENSE file found in the top-level directory of this project and at
 * https://github.com/The-Astrl-Project/oh-the-futures-youll-shape/blob/HEAD/LICENSE.
 *
 * This file may not be copied, modified, propagated, or distributed
 * except according to the terms contained in the LICENSE file.
 */

// File Docstring
/**
 * Oh, the Futures You'll Shape || transport.js
 *
 * A simple, bi-directional, communication transport for sending data to
 * and from the web server.
 *
 * @author @MaxineToTheStars <https://github.com/MaxineToTheStars>
 */

// Enums

// Interfaces

// Constants
const _transport_client_id = location.protocol.endsWith("s:") == true ? crypto.randomUUID().toString() : "LOCAL_HOST";
const _transport_client_socket = location.protocol.endsWith("s:") == true ? new WebSocket(`wss://${location.host}/transport`) : new WebSocket(`ws://${location.host}/transport`);

// Public Variables

// Private Variables

// Constructor

// Public Static Methods

// Public Inherited Methods
export function send_as_json(request_type, request_data, request_args = null) {
  // Convert to a JSON string
  const args = JSON.stringify({
    request_type: request_type,
    request_data: request_data,
    request_args: request_args,
    transport_client_id: _transport_client_id,
  });

  // Send to the server
  _transport_client_socket.send(args);
}

// Private Static Methods
_transport_client_socket.addEventListener("open", (_) => {
  // Log
  console.log("[LOG] Socket connection opened!");

  // Emit connection event
  window.dispatchEvent(new Event("transport_connected"));
});

_transport_client_socket.addEventListener("close", (_) => {
  // Log
  console.log("[ERR] Connection to backend has ceased! Please refresh the tab.");

  // Emit disconnection event
  window.dispatchEvent(new Event("transport_disconnected"));
});

_transport_client_socket.addEventListener("message", (event) => {
  // Redefine event
  event = JSON.parse(event.data);

  // Check if the received transport ID does not match the local transport ID
  if (event.transport_client_id !== _transport_client_id) {
    // Ignore this message
    return;
  }

  // Emit
  window.dispatchEvent(new CustomEvent("transport_server_message", { detail: event }));
});

// Private Inherited Methods
