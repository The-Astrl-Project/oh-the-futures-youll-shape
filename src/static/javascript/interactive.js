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
const dom_submit_button = document.getElementById("submit-button");
const dom_settings_button = document.getElementById("settings-button");

// Public Variables

// Private Variables

// Constructor

// Public Static Methods

// Public Inherited Methods

// Private Static Methods

// Private Inherited Methods
function _hydrate_webpage() {
  // Make buttons interactive
  user_profile_button.addEventListener("click", () => _on_click_event_handler("user-profile-button"));
  dom_submit_button.addEventListener("click", () => _on_click_event_handler("dom-submit-button"));
  dom_settings_button.addEventListener("click", () => _on_click_event_handler("dom-settings-button"));

  // Request the current user's profile image
  send_message({ request_type: "data", request_data: "user-profile-image" });
}

function _on_click_event_handler(from_component) {
  // Check the component
  if (from_component === "user-profile-button") {
    // Request for an OAuth session
    send_message({ request_type: "oauth", request_data: "register" });
  }

  if (from_component === "dom-submit-button") {
    // Temporary variable to hold user data
    let args = {};

    // Retrieve inputted data
    args.target_state = document.getElementById("target-state").value;
    args.current_state = document.getElementById("current-state").value;
    args.study_target = document.getElementById("study-target").value;
    args.use_queer_score = document.getElementById("use-queer-score").checked;

    // Submit data (Verification is done on the server)
    send_message({ request_type: "data", request_data: "search", request_args: args });
  }

  if (from_component === "dom-settings-button") {
    // Retrieve the settings container
    const container = document.querySelector(".container-settings");

    // Toggle the containers "active" property
    container.classList.toggle("active");

    // Check wether to fade-in or ease-out
    if (container.classList.contains("active")) {
      // Fade-in animation
      container.style.animation = "container-settings-fade-in 0.3s ease-in-out";
    } else {
      // Fade out
      container.style.animation = "container-settings-fade-out 0.3s ease-in-out";
      container.style.animationFillMode = "forwards";
    }
  }
}

window.addEventListener("transport_connected", () => {
  // Hydrate the web page
  _hydrate_webpage();
});

// Handle incoming server(backend) messages
window.addEventListener("transport_server_message", (args) => {
  // Redefine args
  args = args.detail;

  // Parse the message contents
  const message_response_type = args.response_type;
  const message_response_data = args.response_data;
  const message_response_args = args.response_args;

  // Server -> Client || Response to our request
  if (message_response_type === "data") {
    // Server sent the current user's profile image (if applicable)
    if (message_response_data === "user-profile-image") {
      // Modify the user badge
      console.log(args);
      if (message_response_args !== null) {
        user_profile_image.src = `${message_response_args}`;
      }
    }
  }

  // Server -> Client || Response to an OAuth request
  if (message_response_type === "oauth") {
    // Server sent the appropriate login/register url
    if (message_response_data === "register") {
      // Check that a url was returned
      if (message_response_args !== null) {
        // Redirect the user
        window.location.href = message_response_args;
      }
    }
  }
});
