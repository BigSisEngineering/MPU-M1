// Function to update the slider value
function updateSliderValue(sliderId, valueId) {
    var slider = document.getElementById(sliderId);
    var output = document.getElementById(valueId);
    output.innerHTML = slider.value + '%';
    
    slider.oninput = function() {
      output.innerHTML = this.value + '%';
    };
  }
  
// Function to toggle button text and change Mode circle color
function toggleButtonTextAndColor(buttonElement, modeCircle) {
  buttonElement.addEventListener('click', function() {
    if (this.textContent.includes('Enable')) {
      this.textContent = this.textContent.replace('Enable', 'Disable');
      // Check which button was pressed and change Mode circle color accordingly
      if (this.textContent.includes('P&P')) {
        modeCircle.style.backgroundColor = 'green';
      } else if (this.textContent.includes('Dummy')) {
        modeCircle.style.backgroundColor = 'blue';
      }
    } else {
      this.textContent = this.textContent.replace('Disable', 'Enable');
      // Revert Mode circle color to original grey
      modeCircle.style.backgroundColor = '#555';
    }
  });
}




function loadCameraFeed() {
  const cameraImage = document.getElementById('camera-feed');
  cameraImage.onload = function() {
      // Refresh the image periodically to get the latest frame
      setTimeout(loadCameraFeed, 50); // Adjust the timeout to your needs
  };
  cameraImage.onerror = function() {
      console.error("Failed to load camera feed.");
      // Retry loading the feed or provide feedback to the user
      setTimeout(loadCameraFeed, 5000); // Adjust the retry timeout to your needs
  };
  // Set the src to the dedicated endpoint for the camera feed
  cameraImage.src = '/dev/video10?' + new Date().getTime();
}

// Call this function when the document is ready
document.addEventListener('DOMContentLoaded', function() {
  loadCameraFeed(); // This will start the process of loading the camera feed
});



// DOMContentLoaded to ensure HTML is fully loaded before executing
document.addEventListener('DOMContentLoaded', function() {
  // Initialize slider values
  updateSliderValue('pp-confidence', 'pp-confidence-value');
  updateSliderValue('unload-probability', 'unload-probability-value');
  
  // Find the Mode circle
  var modeCircle = Array.from(document.querySelectorAll('.circle')).find(function(circle) {
    return circle.textContent.includes('Mode');
  });
  
  // Find buttons by text and apply toggle functionality and color change
  var buttons = document.querySelectorAll('button');
  buttons.forEach(function(button) {
    if (button.textContent.includes('Enable P&P') || button.textContent.includes('Enable Dummy')) {
      toggleButtonTextAndColor(button, modeCircle);
    }
  });
  // Load the camera feed
  loadCameraFeed();
});
  

// document.addEventListener('DOMContentLoaded', function() {
//   var starWheelInitButton = document.getElementById('sw-init-button'); // Make sure the button has this ID
//   starWheelInitButton.addEventListener('click', function() {
//       var xhr = new XMLHttpRequest();
//       xhr.open('POST', '/STAR_WHEEL_INIT', true); // Modify URL if necessary
//       xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
      
//       xhr.onload = function() {
//           if (xhr.status === 200) {
//               // Handle successful response
//               console.log(xhr.responseText);
//           } else {
//               // Handle error response
//               console.error('Error initializing star wheel');
//           }
//       };
//       xhr.send();
//   });
// });


// document.addEventListener('DOMContentLoaded', function() {
//   var starWheelInitButton = document.getElementById('unloader-init-button'); // Make sure the button has this ID
//   starWheelInitButton.addEventListener('click', function() {
//       var xhr = new XMLHttpRequest();
//       xhr.open('POST', '/UNLOADER_INIT', true); // Modify URL if necessary
//       xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
      
//       xhr.onload = function() {
//           if (xhr.status === 200) {
//               // Handle successful response
//               console.log(xhr.responseText);
//           } else {
//               // Handle error response
//               console.error('Error initializing star wheel');
//           }
//       };
//       xhr.send();
//   });
// });


// document.addEventListener('DOMContentLoaded', function() {
//   var starWheelInitButton = document.getElementById('unload-button'); // Make sure the button has this ID
//   starWheelInitButton.addEventListener('click', function() {
//       var xhr = new XMLHttpRequest();
//       xhr.open('POST', '/UNLOAD', true); // Modify URL if necessary
//       xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
      
//       xhr.onload = function() {
//           if (xhr.status === 200) {
//               // Handle successful response
//               console.log(xhr.responseText);
//           } else {
//               // Handle error response
//               console.error('Error initializing star wheel');
//           }
//       };
//       xhr.send();
//   });
// });


document.addEventListener('DOMContentLoaded', function() {
  // Function to initialize a button with an XMLHttpRequest to a specified endpoint
  function setupButton(buttonId, endpoint) {
    var button = document.getElementById(buttonId);
    button.addEventListener('click', function() {
      var xhr = new XMLHttpRequest();
      xhr.open('POST', endpoint, true);
      xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
      
      xhr.onload = function() {
        if (xhr.status === 200) {
          console.log(xhr.responseText);
        } else {
          console.error('Error with request to ' + endpoint);
        }
      };
      xhr.send();
    });
  }

  // Initialize each button with the appropriate action
  setupButton('sw-init-button', '/STAR_WHEEL_INIT');
  setupButton('unloader-init-button', '/UNLOADER_INIT');
  setupButton('clear-sw-error-button', '/CLEAR_STAR_WHEEL_ERROR');
  setupButton('clear-unloader-error-button', '/CLEAR_UNLOADER_ERROR');
  setupButton('unload-button', '/UNLOAD');
  setupButton('move-sw-cw-button', '/MOVE_CW');
  setupButton('move-sw-ccw-button', '/MOVE_CCW');
  setupButton('enable-pnp-button', '/ENABLE_PNP');
  setupButton('enable-dummy-button', '/ENABLE_DUMMY');
});
