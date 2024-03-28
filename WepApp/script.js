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
  