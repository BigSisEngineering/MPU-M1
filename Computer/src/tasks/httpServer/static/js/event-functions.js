// Function to update the slider value
function updateSliderValue(sliderId, valueId) {
  var slider = document.getElementById(sliderId);
  var output = document.getElementById(valueId);
  output.innerHTML = slider.value + '%';
  
  slider.oninput = function() {
      console.log(`Slider value for ${sliderId} updated to ${slider.value}%`);
      output.innerHTML = slider.value + '%';
  };
}

// Function to toggle button text, change Mode circle color, and send disable requests
function toggleButtonTextAndColor(buttonElement, modeCircleId, otherButtonId) {
  buttonElement.addEventListener('click', function() {
      var otherButton = document.getElementById(otherButtonId);
      var modeCircle = document.getElementById(modeCircleId);
      console.log(`Attempting to toggle button: ${this.id}`);

      if (otherButton.dataset.state === 'enabled') {
          console.log(`Cannot enable ${this.id} as ${otherButton.id} is currently enabled.`);
          alert("You cannot enable " + (this.id.includes('pnp') ? "P&P" : "Dummy") + 
                " while " + (otherButton.id.includes('pnp') ? "P&P" : "Dummy") + " is enabled. Disable it first.");
      } else {
          if (this.dataset.state === 'disabled') {
              this.dataset.state = 'enabled';
              this.textContent = 'Disable ' + (this.id.includes('pnp') ? "P&P" : "Dummy");
              modeCircle.style.backgroundColor = (this.id.includes('pnp') ? 'green' : 'blue');
              sendRequestWithRetry('/ENABLE_' + (this.id.includes('pnp') ? 'PNP' : 'DUMMY'));
          } else {
              this.dataset.state = 'disabled';
              this.textContent = 'Enable ' + (this.id.includes('pnp') ? "P&P" : "Dummy");
              modeCircle.style.backgroundColor = '#555';
              sendRequestWithRetry('/DISABLE_' + (this.id.includes('pnp') ? 'PNP' : 'DUMMY'));
          }
      }
      console.log(`${this.id} toggled to ${this.dataset.state}`);
  });
}

// Function to send POST requests with retry logic
function sendRequestWithRetry(endpoint) {
  console.log(`Sending request to ${endpoint}`);
  var xhr = new XMLHttpRequest();
  xhr.open('POST', endpoint, true);
  xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');

  xhr.onload = function() {
      if (xhr.status === 200) {
          console.log('Request successful:', xhr.responseText);
      } else {
          console.error('Error with request to ' + endpoint);
      }
  };
  xhr.onerror = function() {
      console.error('Network error occurred while attempting to request ' + endpoint);
  };
  xhr.send();
}

// Function to load camera feed
function loadCameraFeed() {
  const cameraImage = document.getElementById('camera-feed');
  if (!cameraImage) {
      console.error("Camera feed element not found");
      return;
  }
  cameraImage.onload = function() {
      setTimeout(loadCameraFeed, 50);
      // console.log("Camera feed loaded successfully.");
  };
  cameraImage.onerror = function() {
      console.error("Failed to load camera feed.");
      setTimeout(loadCameraFeed, 5000);
  };
  cameraImage.src = '/video10?' + new Date().getTime();
  // console.log("Camera feed request sent.");
}

// General function to setup button to send POST requests
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

// DOMContentLoaded to ensure HTML is fully loaded before executing scripts
document.addEventListener('DOMContentLoaded', function() {
  updateSliderValue('pp-confidence', 'pp-confidence-value');
  updateSliderValue('unload-probability', 'unload-probability-value');
  
  toggleButtonTextAndColor(document.getElementById('enable-pnp-button'), 'pnp-mode-circle', 'enable-dummy-button');
  toggleButtonTextAndColor(document.getElementById('enable-dummy-button'), 'dummy-mode-circle', 'enable-pnp-button');

  setupButton('sw-init-button', '/STAR_WHEEL_INIT');
  setupButton('move-sw-ccw-button', '/MOVE_CCW');
  setupButton('clear-sw-error-button', '/CLEAR_SW_ERROR');
  setupButton('unloader-init-button', '/UNLOADER_INIT');
  setupButton('unload-button', '/UNLOAD');
  setupButton('move-sw-cw-button', '/MOVE_CW');
  // setupButton('enable-pnp-button', '/ENABLE_PNP');
  // setupButton('enable-dummy-button', '/ENABLE_DUMMY');

  loadCameraFeed(); // Start loading the camera feed
});
