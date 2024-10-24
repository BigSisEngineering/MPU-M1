// Function to update the slider value and send it to the server
function updateSliderValue(sliderId, valueId, endpoint) {
    var slider = document.getElementById(sliderId);
    var output = document.getElementById(valueId);
    output.innerHTML = slider.value + '%'; // Initial display
    
    slider.oninput = function() {
        output.innerHTML = slider.value + '%'; // Update display on input
        console.log(`Slider value for ${sliderId} updated to ${slider.value}%`);
        sendSliderValue(this.value, endpoint); // Send the updated value to the server
    };
}

// Function to send slider values to the server
function sendSliderValue(value, endpoint) {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', endpoint.replace('{value}', value), true);
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');

    xhr.onload = function() {
        if (xhr.status === 200) {
            console.log('Slider value set successfully:', xhr.responseText);
        } else {
            console.error('Failed to set slider value:', xhr.responseText);
        }
    };
    xhr.onerror = function() {
        console.error('Network error occurred while setting slider value');
    };
    xhr.send();
}


// Function to toggle button text, change Mode circle color, and send disable requests
function productionMode(buttonElement, modeCircleId, otherButtonId) {
    buttonElement.addEventListener('click', function() {
        var otherButton = document.getElementById(otherButtonId);
        var modeCircle = document.getElementById(modeCircleId);
  
        console.log(`Attempting to toggle button: ${this.id}`);
  
        // First, fetch the current status of the star wheel and unloader
        fetch('/BoardData')
          .then(response => response.json())
          .then(data => {
            if (data.star_wheel_status !== 'normal' || data.unloader_status !== 'normal') {
                alert('Both Star Wheel and Unloader must be in "normal" status to enable PnP or Dummy.');
                return; // Stop the function if the conditions aren't met
            }
  
            // Check if the other mode is already enabled
            if (otherButton.dataset.state === 'enabled') {
                console.log(`Cannot enable ${this.id} as ${otherButton.id} is currently enabled.`);
                alert("You cannot enable " + (this.id.includes('pnp') ? "P&P" : "Dummy") + 
                      " while " + (otherButton.id.includes('pnp') ? "P&P" : "Dummy") + " is enabled. Disable it first.");
                return;
            }
  
            // Toggle the state based on the existing state
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
            console.log(`${this.id} toggled to ${this.dataset.state}`);
          })
          .catch(error => {
            console.error('Error fetching status data:', error);
            alert('Failed to fetch system status.');
          });
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
function CameraFeed() {
  const cameraImage = document.getElementById('camera-feed');
  if (!cameraImage) {
      console.error("Camera feed element not found");
      return;
  }
  cameraImage.onload = function() {
      setTimeout(CameraFeed, 50);
      // console.log("Camera feed loaded successfully.");
  };
  cameraImage.onerror = function() {
      console.error("Failed to load camera feed.");
      setTimeout(CameraFeed, 5000);
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


// Function to fetch sensor data and update the circles
function fetchAndUpdateBoardData() {
    fetch('/BoardData').then(response => response.json()).then(data => {
        const sensorValuesString = data.sensors_values.slice(1, -1); // Remove the parentheses
        const sensorValues = sensorValuesString.split(', ').map(Number);

        const sensorLoadCircle = document.getElementById('sensor-load-circle');
        const sensorUnloadCircle = document.getElementById('sensor-unload-circle');
        const sensorBufferCircle = document.getElementById('sensor-buffer-circle');
        const starWheelCircle = document.getElementById('sw-init');
        const unloaderCircle = document.getElementById('unloader-init');
        const pnpButton = document.getElementById('enable-pnp-button');
        const dummyButton = document.getElementById('enable-dummy-button');
        const pnpCircle = document.getElementById('pnp-mode-circle');
        const dummyCircle = document.getElementById('dummy-mode-circle');

        sensorLoadCircle.style.backgroundColor = sensorValues[0] > 100 ? 'green' : '';
        sensorUnloadCircle.style.backgroundColor = sensorValues[1] > 100 ? 'green' : '';
        sensorBufferCircle.style.backgroundColor = sensorValues[2] > 100 ? 'green' : '';

        // starWheelCircle.style.backgroundColor = data.star_wheel_status === "normal" ? 'green' :
        //                                          data.star_wheel_status === "overload" ? 'red' : '';
        starWheelCircle.style.backgroundColor = data.star_wheel_status === "normal" ? 'green' :
                                         data.star_wheel_status === "overload" ? 'red' :
                                         data.star_wheel_status === "not_init" ? 'grey' : '';


        unloaderCircle.style.backgroundColor = data.unloader_status === "normal" ? 'green' : '';

        // Update PnP and Dummy button states based on mode
        if (data.mode === "pnp") {
            pnpButton.textContent = 'Disable P&P';
            dummyButton.textContent = 'Enable Dummy';
            pnpCircle.style.backgroundColor = 'green';
            dummyCircle.style.backgroundColor = '';
            pnpButton.dataset.state = 'enabled';
            dummyButton.dataset.state = 'disabled';
        } else if (data.mode === "dummy") {
            dummyButton.textContent = 'Disable Dummy';
            pnpButton.textContent = 'Enable P&P';
            dummyCircle.style.backgroundColor = 'blue';
            pnpCircle.style.backgroundColor = '';
            dummyButton.dataset.state = 'enabled';
            pnpButton.dataset.state = 'disabled';
        } else {
            pnpButton.textContent = 'Enable P&P';
            dummyButton.textContent = 'Enable Dummy';
            pnpCircle.style.backgroundColor = '';
            dummyCircle.style.backgroundColor = '';
            pnpButton.dataset.state = 'disabled';
            dummyButton.dataset.state = 'disabled';
        }
    }).catch(error => {
        console.error('Failed to fetch sensor data:', error);
    });
}
  
  // Fetch and update sensor data every 1 seconds
setInterval(fetchAndUpdateBoardData, 1000);


// DOMContentLoaded to ensure HTML is fully loaded before executing scripts
document.addEventListener('DOMContentLoaded', function() {

  var hostname = window.location.hostname;
  // Update the device ID element with the hostname
  var deviceIdElement = document.getElementById('device-id');
  deviceIdElement.textContent = 'ID: ' + hostname;
  document.title = `🥚 ${hostname}`;

  updateSliderValue('pp-confidence', 'pp-confidence-value', '/SET_PNP_CONFIDENCE_LEVEL/{value}');
  updateSliderValue('unload-probability', 'unload-probability-value', '/SET_DUMMY_UNLOAD_PROBABILITY/{value}');
  
  productionMode(document.getElementById('enable-pnp-button'), 'pnp-mode-circle', 'enable-dummy-button');
  productionMode(document.getElementById('enable-dummy-button'), 'dummy-mode-circle', 'enable-pnp-button');

  setupButton('sw-init-button', '/STAR_WHEEL_INIT');
  setupButton('move-sw-ccw-button', '/MOVE_CCW');
  setupButton('clear-sw-error-button', '/CLEAR_STAR_WHEEL_ERROR');
  setupButton('unloader-init-button', '/UNLOADER_INIT');
  setupButton('unload-button', '/UNLOAD');
  setupButton('move-sw-cw-button', '/MOVE_CW');
  CameraFeed(); 
});


