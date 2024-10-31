// // Function to update the slider value and send it to the server
// function updateSliderValue(sliderId, valueId, endpoint) {
//     var slider = document.getElementById(sliderId);
//     var output = document.getElementById(valueId);
//     output.innerHTML = slider.value + '%'; // Initial display
    
//     slider.oninput = function() {
//         output.innerHTML = slider.value + '%'; // Update display on input
//         console.log(`Slider value for ${sliderId} updated to ${slider.value}%`);
//         sendSliderValue(this.value, endpoint); // Send the updated value to the server
//     };
// }

// // Function to send slider values to the server
// function sendSliderValue(value, endpoint) {
//     var xhr = new XMLHttpRequest();
//     xhr.open('POST', endpoint.replace('{value}', value), true);
//     xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');

//     xhr.onload = function() {
//         if (xhr.status === 200) {
//             console.log('Slider value set successfully:', xhr.responseText);
//         } else {
//             console.error('Failed to set slider value:', xhr.responseText);
//         }
//     };
//     xhr.onerror = function() {
//         console.error('Network error occurred while setting slider value');
//     };
//     xhr.send();
// }


// // Function to toggle button text, change Mode circle color, and send disable requests
// function productionMode(buttonElement, modeCircleId, otherButtonId) {
//     buttonElement.addEventListener('click', function() {
//         var otherButton = document.getElementById(otherButtonId);
//         var modeCircle = document.getElementById(modeCircleId);
  
//         console.log(`Attempting to toggle button: ${this.id}`);
  
//         // First, fetch the current status of the star wheel and unloader
//         fetch('/BoardData')
//           .then(response => response.json())
//           .then(data => {
//             if (data.star_wheel_status !== 'normal' || data.unloader_status !== 'normal') {
//                 alert('Both Star Wheel and Unloader must be in "normal" status to enable PnP or Dummy.');
//                 return; // Stop the function if the conditions aren't met
//             }
  
//             // Check if the other mode is already enabled
//             if (otherButton.dataset.state === 'enabled') {
//                 console.log(`Cannot enable ${this.id} as ${otherButton.id} is currently enabled.`);
//                 alert("You cannot enable " + (this.id.includes('pnp') ? "P&P" : "Dummy") + 
//                       " while " + (otherButton.id.includes('pnp') ? "P&P" : "Dummy") + " is enabled. Disable it first.");
//                 return;
//             }
  
//             // Toggle the state based on the existing state
//             if (this.dataset.state === 'disabled') {
//                 this.dataset.state = 'enabled';
//                 this.textContent = 'Disable ' + (this.id.includes('pnp') ? "P&P" : "Dummy");
//                 modeCircle.style.backgroundColor = (this.id.includes('pnp') ? 'green' : 'blue');
//                 sendRequestWithRetry('/ENABLE_' + (this.id.includes('pnp') ? 'PNP' : 'DUMMY'));
//             } else {
//                 this.dataset.state = 'disabled';
//                 this.textContent = 'Enable ' + (this.id.includes('pnp') ? "P&P" : "Dummy");
//                 modeCircle.style.backgroundColor = '#555';
//                 sendRequestWithRetry('/DISABLE_' + (this.id.includes('pnp') ? 'PNP' : 'DUMMY'));
//             }
//             console.log(`${this.id} toggled to ${this.dataset.state}`);
//           })
//           .catch(error => {
//             console.error('Error fetching status data:', error);
//             alert('Failed to fetch system status.');
//           });
//     });
// }

function productionMode(buttonElement, modeCircleId, otherButtonId1, otherButtonId2) {
    buttonElement.addEventListener('click', function() {
        var otherButton1 = document.getElementById(otherButtonId1);
        var otherButton2 = otherButtonId2 ? document.getElementById(otherButtonId2) : null;
        var modeCircle = document.getElementById(modeCircleId);

        console.log(`Attempting to toggle button: ${this.id}`);

        // Fetch the current status of the star wheel and unloader
        fetch('/BoardData')
            .then(response => response.json())
            .then(data => {
                if (data.star_wheel_status !== 'normal' || data.unloader_status !== 'normal') {
                    alert('Both Star Wheel and Unloader must be in "normal" status to enable this mode.');
                    return; // Stop the function if the conditions aren't met
                }

                // Check if this mode is currently disabled and we're trying to enable it
                if (this.dataset.state === 'disabled') {
                    // Check if any other mode is already enabled
                    if ((otherButton1 && otherButton1.dataset.state === 'enabled') ||
                        (otherButton2 && otherButton2.dataset.state === 'enabled')) {
                        console.log(`Cannot enable ${this.id} as another mode is currently enabled.`);
                        alert("You cannot enable this mode while another mode is enabled. Disable it first.");
                        return;
                    }

                    // Enable this mode
                    this.dataset.state = 'enabled';
                    this.textContent = 'Disable ' + this.textContent.split(' ')[1];
                    modeCircle.style.backgroundColor = 'green'; // You can change the color as needed
                    sendRequestWithRetry('/ENABLE_' + this.id.toUpperCase().split('-')[1]);
                } else {
                    // Disable this mode
                    this.dataset.state = 'disabled';
                    this.textContent = 'Enable ' + this.textContent.split(' ')[1];
                    modeCircle.style.backgroundColor = '#555';
                    sendRequestWithRetry('/DISABLE_' + this.id.toUpperCase().split('-')[1]);
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
async function CameraFeed() {
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
  cameraImage.src = '/video_feed?' + new Date().getTime();
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


// // Function to fetch sensor data and update the circles
// async function fetchAndUpdateBoardData() {
//     fetch('/BoardData').then(response => response.json()).then(data => {
//         const sensorValuesString = data.sensors_values.slice(1, -1); // Remove the parentheses
//         const sensorValues = sensorValuesString.split(', ').map(Number);

//         const sensorLoadCircle = document.getElementById('sensor-load-circle');
//         const sensorUnloadCircle = document.getElementById('sensor-unload-circle');
//         const sensorBufferCircle = document.getElementById('sensor-buffer-circle');
//         const starWheelCircle = document.getElementById('sw-init');
//         const unloaderCircle = document.getElementById('unloader-init');
//         const pnpButton = document.getElementById('enable-pnp-button');
//         const dummyButton = document.getElementById('enable-dummy-button');
//         const pnpCircle = document.getElementById('pnp-mode-circle');
//         const dummyCircle = document.getElementById('dummy-mode-circle');

//         sensorLoadCircle.style.backgroundColor = sensorValues[0] > 100 ? 'green' : '';
//         sensorUnloadCircle.style.backgroundColor = sensorValues[1] > 100 ? 'green' : '';
//         sensorBufferCircle.style.backgroundColor = sensorValues[2] > 100 ? 'green' : '';

//         // starWheelCircle.style.backgroundColor = data.star_wheel_status === "normal" ? 'green' :
//         //                                          data.star_wheel_status === "overload" ? 'red' : '';
//         starWheelCircle.style.backgroundColor = data.star_wheel_status === "normal" ? 'green' :
//                                         data.star_wheel_status === "overload" ? 'red' :
//                                         data.star_wheel_status === "not_init" ? 'grey' : '';


//         unloaderCircle.style.backgroundColor = data.unloader_status === "normal" ? 'green' :
//                                         data.unloader_status === "overload" ? 'red' :
//                                         data.unloader_status === "not_init" ? 'grey' : '';

//         // Update PnP and Dummy button states based on mode
//         if (data.mode === "pnp") {
//             pnpButton.textContent = 'Disable P&P';
//             dummyButton.textContent = 'Enable Dummy';
//             pnpCircle.style.backgroundColor = 'green';
//             dummyCircle.style.backgroundColor = '';
//             pnpButton.dataset.state = 'enabled';
//             dummyButton.dataset.state = 'disabled';
//         } else if (data.mode === "dummy") {
//             dummyButton.textContent = 'Disable Dummy';
//             pnpButton.textContent = 'Enable P&P';
//             dummyCircle.style.backgroundColor = 'blue';
//             pnpCircle.style.backgroundColor = '';
//             dummyButton.dataset.state = 'enabled';
//             pnpButton.dataset.state = 'disabled';
//         } else {
//             pnpButton.textContent = 'Enable P&P';
//             dummyButton.textContent = 'Enable Dummy';
//             pnpCircle.style.backgroundColor = '';
//             dummyCircle.style.backgroundColor = '';
//             pnpButton.dataset.state = 'disabled';
//             dummyButton.dataset.state = 'disabled';
//         }
//     }).catch(error => {
//         console.error('Failed to fetch sensor data:', error);
//     });
// }

async function fetchAndUpdateBoardData() {
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
        const experimentButton = document.getElementById('enable-experiment-button');
        const pnpCircle = document.getElementById('pnp-mode-circle');
        const dummyCircle = document.getElementById('dummy-mode-circle');
        const experimentCircle = document.getElementById('experiment-mode-circle');

        sensorLoadCircle.style.backgroundColor = sensorValues[0] > 100 ? 'green' : '';
        sensorUnloadCircle.style.backgroundColor = sensorValues[1] > 100 ? 'green' : '';
        sensorBufferCircle.style.backgroundColor = sensorValues[2] > 100 ? 'green' : '';

        starWheelCircle.style.backgroundColor = data.star_wheel_status === "normal" ? 'green' :
                                        data.star_wheel_status === "overload" ? 'red' :
                                        data.star_wheel_status === "not_init" ? 'grey' : '';

        unloaderCircle.style.backgroundColor = data.unloader_status === "normal" ? 'green' :
                                        data.unloader_status === "overload" ? 'red' :
                                        data.unloader_status === "not_init" ? 'grey' : '';

        // Update PnP, Dummy, and Experiment button states based on mode
        if (data.mode === "pnp") {
            pnpButton.textContent = 'Disable P&P';
            dummyButton.textContent = 'Enable Dummy';
            experimentButton.textContent = 'Enable Experiment';
            pnpCircle.style.backgroundColor = 'green';
            dummyCircle.style.backgroundColor = '';
            experimentCircle.style.backgroundColor = '';
            pnpButton.dataset.state = 'enabled';
            dummyButton.dataset.state = 'disabled';
            experimentButton.dataset.state = 'disabled';
        } else if (data.mode === "dummy") {
            dummyButton.textContent = 'Disable Dummy';
            pnpButton.textContent = 'Enable P&P';
            experimentButton.textContent = 'Enable Experiment';
            dummyCircle.style.backgroundColor = 'blue';
            pnpCircle.style.backgroundColor = '';
            experimentCircle.style.backgroundColor = '';
            dummyButton.dataset.state = 'enabled';
            pnpButton.dataset.state = 'disabled';
            experimentButton.dataset.state = 'disabled';
        } else if (data.mode === "experiment") {
            experimentButton.textContent = 'Disable Experiment';
            pnpButton.textContent = 'Enable P&P';
            dummyButton.textContent = 'Enable Dummy';
            experimentCircle.style.backgroundColor = 'orange'; 
            pnpCircle.style.backgroundColor = '';
            dummyCircle.style.backgroundColor = '';
            experimentButton.dataset.state = 'enabled';
            pnpButton.dataset.state = 'disabled';
            dummyButton.dataset.state = 'disabled';
        } else {
            pnpButton.textContent = 'Enable P&P';
            dummyButton.textContent = 'Enable Dummy';
            experimentButton.textContent = 'Enable Experiment';
            pnpCircle.style.backgroundColor = '';
            dummyCircle.style.backgroundColor = '';
            experimentCircle.style.backgroundColor = '';
            pnpButton.dataset.state = 'disabled';
            dummyButton.dataset.state = 'disabled';
            experimentButton.dataset.state = 'disabled';
        }
    }).catch(error => {
        console.error('Failed to fetch sensor data:', error);
    });
}

  

// function setupButtonWithInput(buttonId, inputId, endpointTemplate) {
//     var button = document.getElementById(buttonId);
//     var input = document.getElementById(inputId);
    
//     button.addEventListener('click', function() {
//         var num = input.value;
//         var endpoint = endpointTemplate.replace('{num}', num);

//         var xhr = new XMLHttpRequest();
//         xhr.open('POST', endpoint, true);
//         xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        
//         xhr.onload = function() {
//             if (xhr.status === 200) {
//                 console.log(xhr.responseText);
//             } else {
//                 console.error('Error with request to ' + endpoint);
//             }
//         };
//         xhr.send();
//     });
// }

function setupButtonWithInput(buttonId, inputId, endpointTemplate) {
    var button = document.getElementById(buttonId);
    var input = document.getElementById(inputId);

    if (!button) {
        console.error(`Button with ID ${buttonId} not found`);
        return;
    }
    if (!input) {
        console.error(`Input with ID ${inputId} not found`);
        return;
    }

    button.addEventListener('click', function() {
        var num = input.value;
        console.log(`Input value: ${num}`);

        if (num === "") {
            alert("Please enter a valid interval.");
            return;
        }

        var endpoint = endpointTemplate.replace('{num}', num);
        console.log(`Sending POST request to ${endpoint}`);

        var xhr = new XMLHttpRequest();
        xhr.open('POST', endpoint, true);
        xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');

        xhr.onload = function() {
            if (xhr.status === 200) {
                console.log('Request successful:', xhr.responseText);
            } else {
                console.error('Error with request to ' + endpoint + ':', xhr.responseText);
            }
        };
        xhr.onerror = function() {
            console.error('Network error occurred while attempting to request ' + endpoint);
        };
        xhr.send();
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

//   updateSliderValue('pp-confidence', 'pp-confidence-value', '/SET_PNP_CONFIDENCE_LEVEL/{value}');
//   updateSliderValue('unload-probability', 'unload-probability-value', '/SET_DUMMY_UNLOAD_PROBABILITY/{value}');
  
//   productionMode(document.getElementById('enable-pnp-button'), 'pnp-mode-circle', 'enable-dummy-button');
//   productionMode(document.getElementById('enable-dummy-button'), 'dummy-mode-circle', 'enable-pnp-button');
//   productionMode(document.getElementById('enable-experiment-button'), 'experiment-mode-circle', 'enable-experiment-button');
  productionMode(document.getElementById('enable-pnp-button'), 'pnp-mode-circle', 'enable-dummy-button', 'enable-experiment-button');
  productionMode(document.getElementById('enable-dummy-button'), 'dummy-mode-circle', 'enable-pnp-button', 'enable-experiment-button');
  productionMode(document.getElementById('enable-experiment-button'), 'experiment-mode-circle', 'enable-pnp-button', 'enable-dummy-button');

  setupButton('sw-init-button', '/STAR_WHEEL_INIT');
  setupButton('move-sw-ccw-button', '/MOVE_CCW');
  setupButton('clear-sw-error-button', '/CLEAR_STAR_WHEEL_ERROR');
  setupButton('clear-unloader-error-button', '/CLEAR_UNLOADER_ERROR');
  setupButton('unloader-init-button', '/UNLOADER_INIT');
  setupButton('unload-button', '/UNLOAD');
  setupButton('move-sw-cw-button', '/MOVE_CW');
  setupButton('set-zero', '/SAVE_STAR_WHEEL_ZERO');
  setupButtonWithInput('set-offset', 'sw-pos', '/SAVE_STAR_WHEEL_OFFSET/{num}');
  setupButtonWithInput('move-sw-pos', 'sw-pos', '/MOVE_STAR_WHEEL/{num}');
  setupButtonWithInput('confirm-interval', 'interval', '/SET_PAUSE_INTERVAL/{num}');
//   setupButtonWithInput('confirm-pos', 'sw-pos', '/SET_POS/{num}');
  CameraFeed(); 

  
//   fetch('/version')
//     .then(r => r.json())
//     .then(d => document.getElementById('software-version').textContent = d.version);
});


