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
// NOTE: This should not be shipped to PROD like this
const _transport_client_id = location.protocol == "https" ? crypto.randomUUID().toString() : Math.random().toString();
const _transport_client_socket = new io();

// Public Variables

// Private Variables

// Constructor

// Public Static Methods

// Public Inherited Methods
/**
 * Sends a message to the server with the given
 * ``args``.
 * @param {*} args - The data to pass
 * @returns ``void``
 */
export function send_message(args) {
  // Modify the argument
  args.transport_client_id = _transport_client_id;

  // Emit
  _transport_client_socket.emit("client_message", args);
}

// Private Static Methods
_transport_client_socket.on("connect", () => {
  // Log
  console.log("[INF] Socket connection opened");

  // Emit connection event
  window.dispatchEvent(new Event("transport_connected"));
});

_transport_client_socket.on("disconnect", () => {
  // Log
  console.log("[ERR] Connection to backend has ceased! Please refresh the tab");

  // Emit disconnection event
  window.dispatchEvent(new Event("transport_disconnected"));
});

_transport_client_socket.on("server_message", (args, _) => {
  // Check if the client ID matches our local id
  if (args.transport_client_id !== _transport_client_id) {
    return;
  }

  // Emit
  window.dispatchEvent(new CustomEvent("transport_server_message", { detail: args }));
});

// Private Inherited Methods
