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
import { send_as_json } from "./transport.js";

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

// Public Variables
let text_input = {};
let action_buttons = {};

// Private Variables

// Constructor

// Public Static Methods

// Public Inherited Methods

// Private Static Methods

// Private Inherited Methods
function _hydrate_webpage() {
  // Aggregate all found buttons
  action_buttons.submit_button = document.getElementById("submit-button");
  action_buttons.settings_button = document.getElementById("settings-button");
  action_buttons.user_profile_button = document.getElementById("user-profile-button");
  action_buttons.toggle_queer_scoring = document.getElementById("use-queer-scoring");
  action_buttons.toggle_location_button = document.getElementById("toggle-location-button");

  // Aggregate all found text inputs
  text_input.target_state = document.getElementById("target-state");
  text_input.study_target = document.getElementById("study-target");
  text_input.current_state = document.getElementById("current-state");

  // Make buttons interactive
  action_buttons.submit_button.addEventListener("click", () => _on_click_event_handler("submit-button"));
  action_buttons.settings_button.addEventListener("click", () => _on_click_event_handler("settings-button"));
  action_buttons.user_profile_button.addEventListener("click", () => _on_click_event_handler("user-profile-button"));
  action_buttons.toggle_location_button.addEventListener("click", () =>
    _on_click_event_handler("toggle-location-button")
  );

  // Request the current user's profile image
  send_as_json("data", "user-profile-image");
}

function _on_click_event_handler(from_component) {
  switch (from_component) {
    case "submit-button":
      // Exit
      break;

    case "settings-button":
      // Retrieve the settings container
      const container = document.querySelector(".container-settings");

      // Toggle the container's "active" property
      container.classList.toggle("active");

      // Check wether to fade-in or fade-out
      switch (container.classList.contains("active")) {
        case true:
          // Fade-in animation
          container.style.animation = "container-settings-fade-in 0.3s ease-in-out";

          // Exit
          break;

        case false:
          // Fade-out animation
          container.style.animation = "container-settings-fade-out 0.3s ease-in-out";
          container.style.animationFillMode = "forwards";

          // Exit
          break;
      }

      // Exit
      break;

    case "user-profile-button":
      // Request for an OAuth session
      send_as_json("oauth", "user-register");

      // Exit
      break;

    case "toggle-location-button":
      // Exit
      break;
  }
}

window.addEventListener("transport_connected", (_) => {
  // Hydrate the webpage
  _hydrate_webpage();
});

// Handle incoming server(backend) messages
window.addEventListener("transport_server_message", (args) => {
  // Redefine args
  args = args.detail;

  // Data response or OAuth response?
  const response_type = args.response_type;
  // What specific data was returned
  const response_data = args.response_data;
  // Supplied information from the server
  const response_args = args.response_args;

  switch (response_type) {
    case "data":
      switch (response_data) {
        case "user-profile-image":
          // Check that a url was returned
          if (response_args !== null) {
            // Replace the user badge with the new image
            document.getElementById("user-profile-image").src = `${response_args.url}`;

            // Exit
            break;
          }
          // Fallback to default badge
          document.getElementById("user-profile-image").src = "../static/images/user_profile_fallback_icon.svg";

          // Exit
          break;
      }

      // Exit
      break;

    case "oauth":
      switch (response_data) {
        case "user-register":
          // Check that a url was returned
          if (response_args !== null) {
            // Redirect the user
            window.location.href = response_args.url;

            // Exit
            break;
          }

          // Exit
          break;
        case "user-unregister":
          // Exit
          break;
      }

    default:
      // Malformed or invalid response
      break;
  }
});
