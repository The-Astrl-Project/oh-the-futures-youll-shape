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
let text_inputs = {};
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
  action_buttons.astrl_legal_button = document.getElementById("astrl-legal-button");

  // Aggregate all found text inputs
  text_inputs.target_state = document.getElementById("target-state");
  text_inputs.current_state = document.getElementById("current-state");
  text_inputs.majoring_target = document.getElementById("majoring-target");

  // Make buttons interactive
  action_buttons.submit_button.addEventListener("click", (_) => _on_click_event_handler("submit-button"));
  action_buttons.settings_button.addEventListener("click", (_) => _on_click_event_handler("settings-button"));
  action_buttons.user_profile_button.addEventListener("click", (_) => _on_click_event_handler("user-profile-button"));
  action_buttons.astrl_legal_button.addEventListener("click", (_) => _on_click_event_handler("astrl-legal-button"));

  // Make text boxes interactive
  text_inputs.target_state.addEventListener("change", (_) => _on_change_event_handler("target-state"));
  text_inputs.current_state.addEventListener("change", (_) => _on_change_event_handler("current-state"));
  text_inputs.majoring_target.addEventListener("change", (_) => _on_change_event_handler("majoring-target"));

  // Request the current user's profile image
  send_as_json("data", "user-profile-image");
}

function _on_click_event_handler(from_component) {
  switch (from_component) {
    case "submit-button":
      // Extract all applicable data
      const target_state = text_inputs.target_state.value;
      const current_state = text_inputs.current_state.value;
      const majoring_target = text_inputs.majoring_target.value;
      const use_queer_scoring = action_buttons.toggle_queer_scoring.checked;

      // Send to server for validation and submission
      send_as_json("data", "search", {
        target_state: target_state,
        current_state: current_state,
        majoring_target: majoring_target,
        use_queer_scoring: use_queer_scoring,
      });

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

    case "astrl-legal-button":
      // Redirect to legal
      window.location.pathname = "/legal/privacy";
  }
}

function _on_change_event_handler(from_component) {
  // Switch on component
  switch (from_component) {
    case "target-state":
      // Send autocomplete request
      send_as_json("data", "autocomplete", { input: text_inputs.target_state.value, target: "target-state" });

      // Exit
      break;

    case "current-state":
      // Send autocomplete request
      send_as_json("data", "autocomplete", { input: text_inputs.current_state.value, target: "current-state" });

      // Exit
      break;

    case "majoring-target":
      // Send autocomplete request
      send_as_json("data", "autocomplete", { input: text_inputs.majoring_target.value, target: "majoring-target" });

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
          // Replace the user badge with the new image
          document.getElementById("user-profile-image").src = `${response_args.url}`;

          // Exit
          break;

        case "autocomplete":
          // Extract the autocomplete target and results
          const text = response_args.results;
          const target = response_args.target;

          // Match the target
          switch (target) {
            case "target-state":
              // Update text
              text_inputs.target_state.value = text;

              // Break
              break;
            case "current-state":
              // Update text
              text_inputs.current_state.value = text;

              // Break
              break;

            case "majoring-target":
              // Update text
              text_inputs.majoring_target.value = text;

              // Break
              break;
          }

        case "search":
          // Extract the response
          const response = response_args.response;

          // Match the response message
          switch (response) {
            // Invalid session
            case "INVALID_SESSION":
              // Alert the user to login to their Google account
              alert("Please login to a Google Account before using this site");

              // Request for an OAuth session
              send_as_json("oauth", "user-register");

              // Break
              break;

            // Processing request
            case "PROCESSING_REQUEST":
              // List of possible messages
              const messages = [
                "Searching the cosmos...",
                "Exploring distant galaxies...",
                "Researching anomalies...",
                "Planning your future...",
                "Contemplating the meaning of existence...",
                "Checking in with the locals...",
                "Unraveling the unknown...",
                "Charting new frontiers...",
                "Redefining the impossible...",
                "Building bridges to the future...",
                "Synchronizing with the quantum realm...",
              ];

              // Local function for generating messages
              function displayNewLoadingMessage() {
                // Create a new message object
                const message_object = document.createElement("div");

                // Retrieve a random message
                const message_content = messages[Math.round(Math.random() * messages.length)];

                // Set size, location, and content
                message_object.style.fontSize = `${Math.random() * 32 + 12}px`;
                message_object.style.top = `${20 + Math.random() * 60}vh`;
                message_object.textContent = message_content;

                // Add to loading-message class
                message_object.classList.add("loading-message");

                // Parent to the DOM
                document.body.appendChild(message_object);

                setTimeout(() => message_object.remove(), 4.5 * 1000);
              }

              // Hide content
              document.getElementById("content").style.visibility = "hidden";

              // Trigger loading
              document.body.classList.add("loading");

              // Set interval
              setInterval(displayNewLoadingMessage, 0.3 * 1000);

              // Break
              break;

            // Processing done
            case "PROCESSING_FINISHED":
              // Redirect
              window.location.href = response_args.url;

              // Break
              break;
          }

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
