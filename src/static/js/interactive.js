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

// Import Statements
import { send_message } from "./transport.js";

// File Docstring
/**
 * Oh, the Futures You'll Shape || interactive.js
 *
 * Provides the needed site functionality.
 *
 * @author @MaxineToTheStars <https://github.com/MaxineToTheStars>
 */

// Enums

// Interfaces

// Constants
const user_profile_image = document.getElementById("user-profile-image");
const user_profile_button = document.getElementById("user-profile-button");

// Public Variables

// Private Variables

// Constructor

// Public Static Methods

// Public Inherited Methods

// Private Static Methods

// Private Inherited Methods
function _hydrate_webpage() {
  // Make buttons interactive
  user_profile_button.addEventListener("click", _on_click_event_handler("user-profile-button"));

  // Request the current user's profile image
  send_message({ type: "request", data: "user_profile" });
}

function _on_click_event_handler(from_component) {
  // Check the component
  if (from_component === "user-profile-button") {
    // Request for an OAuth session
    send_message({ type: "oauth", data: "register" });
  }
}

window.addEventListener("transport_connected", () => {
  // Hydrate the web page
  _hydrate_webpage();
});

// Handle incoming server(backend) messages
window.addEventListener("transport_server_message", (arg) => {
  // Check the message type
  if (arg.type === "response") {
    // Check the response type
    if (arg.response_type === "user_profile") {
      // Modify the profile (if applicable)
      if (arg.data !== null) {
        user_profile_image.src = `${arg.data}`;
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
