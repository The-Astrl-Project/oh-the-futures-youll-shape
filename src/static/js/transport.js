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
const socket = new io();
const client_id = crypto.randomUUID();

// Public Variables

// Private Variables

// Constructor
document.getElementById("user_profile_btn").addEventListener("click", onclick_user_profile);

// Public Static Methods

// Public Inherited Methods
socket.on("connect", () => {
  // Debug
  console.log("[DBG] Socket connection opened!");

  // Hydrate the web page
  _request_user_profile();
});

socket.on("disconnect", () => {
  // Debug
  console.log("[DBG] Socket connection closed!");
});

socket.on("server_message", (arg, _) => {
  // Check if the client_id is the same one as ours
  if (arg.client_id !== client_id) {
    return;
  }

  // Check the message type
  if (arg.type === "response") {
    // Check the response type
    if (arg.response_type === "user_profile") {
      // Modify the profile (if applicable)
      if (arg.data !== null) {
        document.getElementById("user_profile_img").src = `${arg.data}`;
      }
    }
  }

  // Check the message type
  if (arg.type === "oauth") {
    // Check the response type
    if (arg.response_type === "oauth_redirect") {
      // Redirect the user
      window.location.href = arg.data;
    }
  }
});

// Private Static Methods

// Private Inherited Methods
function _request_user_profile() {
  // Send a socket message
  socket.emit("client_message", { type: "request", data: "user_profile", client_id: client_id });
}

function onclick_user_profile() {
  // Send a socket message to commence OAuth
  socket.emit("client_message", { type: "oauth", data: "register", client_id: client_id });
}
