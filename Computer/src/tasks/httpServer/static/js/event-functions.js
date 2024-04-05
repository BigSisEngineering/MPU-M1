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
  });
  


// Assuming you have an <img> element with id="camera-feed"
const cameraFeed = document.getElementById('camera-feed');

function refreshCameraFeed() {
    // Append a timestamp to the camera feed URL to prevent caching
    cameraFeed.src = '/dev/video10?' + new Date().getTime();
}

function setupCameraFeed() {
    let retries = 0;
    const maxRetries = 3; // Maximum number of retries before giving up

    // Load the camera feed for the first time
    refreshCameraFeed();

    // Add an error event listener to the image
    cameraFeed.addEventListener('error', function onCameraError() {
        // If there is an error (e.g., the connection was closed), wait a second and try to reconnect
        if (retries < maxRetries) {
            setTimeout(() => {
                console.log('Attempting to reconnect to camera feed...');
                refreshCameraFeed();
                retries++;
            }, 10); // Wait for 1 second before retrying
        } else {
            cameraFeed.removeEventListener('error', onCameraError);
            console.error('Camera feed cannot be loaded after several retries.');
            // Optionally, display an error message to the user
        }
    });
}

// Call this function when the document is ready
// setupCameraFeed();


document.addEventListener('DOMContentLoaded', function() {
  var starWheelInitButton = document.getElementById('star-wheel-init-button'); // Make sure the button has this ID
  starWheelInitButton.addEventListener('click', function() {
      var xhr = new XMLHttpRequest();
      xhr.open('POST', '/STAR_WHEEL_INIT', true); // Modify URL if necessary
      xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
      
      xhr.onload = function() {
          if (xhr.status === 200) {
              // Handle successful response
              console.log(xhr.responseText);
          } else {
              // Handle error response
              console.error('Error initializing star wheel');
          }
      };
      xhr.send();
  });
});
