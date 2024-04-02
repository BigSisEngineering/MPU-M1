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
  
  // document.addEventListener('DOMContentLoaded', function() {
  //   const videoElement = document.getElementById('camera');
  
  //   if (navigator.mediaDevices.getUserMedia) {
  //     navigator.mediaDevices.getUserMedia({ video: true })
  //       .then(function(stream) {
  //         videoElement.srcObject = stream;
  //       })
  //       .catch(function(error) {
  //         console.error("Error accessing the camera:", error);
  //       });
  //   } else {
  //     console.error("getUserMedia not supported by this browser.");
  //   }
  // });

  document.addEventListener('DOMContentLoaded', (event) => {
    // Your DOM is fully loaded. You can place event listeners or initialize components here.
    console.log('DOM fully loaded and parsed');

    // Example: Refresh the camera feed periodically
    const cameraFeed = document.getElementById('camera-feed');
    setInterval(() => {
        // This will force the img tag to refresh the camera feed by changing its src attribute.
        // Note that appending a unique query string prevents the browser from caching the image.
        cameraFeed.src = '/dev/video10' + new Date().getTime();
    }, 5000); // Refresh every 5000 milliseconds (5 seconds)
});

  
  