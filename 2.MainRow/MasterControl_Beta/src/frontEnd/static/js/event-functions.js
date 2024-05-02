document.addEventListener("DOMContentLoaded", function () {
    setupPageElements();
    fetchCageStatus();
  });
  
  function setupPageElements() {
    const tableHead = document.querySelector("thead tr");
    const tableBody = document.querySelector("tbody");
  
    // Define specific ranges
    const cages = [
      ...Array.from({ length: 9 }, (_, i) => i + 1), // Generates 1 to 9
      ...Array.from({ length: 6 }, (_, i) => i + 16) // Generates 16 to 21
    ].map((i) => `cage0x${i.toString(16).padStart(4, "0")}`);
  
    cages.forEach((cageNum) => {
      let th = document.createElement("th");
      let a = document.createElement("a");
      a.textContent = cageNum;
      a.href = `http://${cageNum}:8080`;
      a.target = "_blank";
      th.appendChild(a);
      tableHead.appendChild(th);
    });
  
    generateRows(tableBody, cages);
    setupCageSelection(cages);
    setupActionExecution();
  }
  
  function generateRows(tableBody, cages) {
    const rows = [
      { name: "Mode", className: "mode-cell", symbol: "" },
      { name: "Star Wheel", className: "sw-gear-cell", symbol: "fa-solid fa-gear" },
      { name: "Unloader", className: "ul-gear-cell", symbol: "fa-solid fa-gear" },
      { name: "Load Sensor", className: "load-sensor-cell", symbol: "" },
      { name: "Unload Sensor", className: "unload-sensor-cell", symbol: "" },
      { name: "Buffer Sensor", className: "buffer-sensor-cell", symbol: "" }
    ];
  
    rows.forEach((row) => {
      let tr = document.createElement("tr");
      let tdName = document.createElement("td");
      tdName.textContent = row.name;
      tr.appendChild(tdName);
  
      cages.forEach((cageId) => {
        let td = document.createElement("td");
        td.id = `${cageId}_${row.className}`; // Unique ID for each cell
        td.className = row.className;
        if (row.symbol) {
          let icon = document.createElement("i");
          icon.className = row.symbol;
          td.appendChild(icon);
        }
        tr.appendChild(td);
      });
      tableBody.appendChild(tr);
    });
  }
  
  function setupCageSelection(cages) {
    const container = document.getElementById("cage-checkboxes");
    cages.forEach((cageNum) => {
      const checkboxDiv = document.createElement("div");
      const checkbox = document.createElement("input");
      checkbox.type = "checkbox";
      checkbox.id = cageNum;
      checkbox.className = "cage-checkbox";
      const label = document.createElement("label");
      label.htmlFor = cageNum;
      label.textContent = cageNum;
      checkboxDiv.appendChild(checkbox);
      checkboxDiv.appendChild(label);
      container.appendChild(checkboxDiv);
    });
  
    const selectAllCheckbox = document.getElementById("select-all");
    selectAllCheckbox.addEventListener("change", function () {
      document.querySelectorAll(".cage-checkbox").forEach((chk) => {
        chk.checked = this.checked;
      });
    });
  }
  
  function setupActionExecution() {
    const executeButton = document.getElementById("execute-action");
    const cageCheckboxes = document.querySelectorAll(".cage-checkbox");
    const actionCheckboxes = document.querySelectorAll('.action-checkboxes input[type="checkbox"]');
  
    executeButton.addEventListener("click", function () {
      const cagesSelected = Array.from(cageCheckboxes).some((chk) => chk.checked);
      const actionsSelected = Array.from(actionCheckboxes).filter((chk) => chk.checked);
  
      if (!cagesSelected) {
        alert("Please select at least one cage.");
      } else if (actionsSelected.length === 0) {
        alert("Please select an action.");
      } else if (actionsSelected.length > 1) {
        alert("Only one action can be selected at a time.");
      }
    });
  }

  function fetchCageStatus() {
    setInterval(() => {
      fetch('/get_all_cages_status')
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok: ' + response.statusText);
          }
          return response.json();
        })
        .then(data => {
          updateModeIndicators(data);
          updateSensorIndicators(data);
        })
        .catch(error => {
          console.error('Error fetching cage status:', error);
        });
    }, 3000); // Fetch every 3 seconds
  }
  
  function updateModeIndicators(data) {
    Object.keys(data).forEach((cage) => {
      const modeIndicator = document.querySelector(`#${cage}_mode-cell`);
      if (modeIndicator) {
        modeIndicator.classList.remove("indicator-pnp", "indicator-dummy", "indicator-idle", "indicator-offline");
        let statusClass = "indicator-" + (data[cage].mode || "offline");
        modeIndicator.classList.add(statusClass);
      } else {
        console.error("No mode indicator found for " + cage);
      }
    });
  }
  function updateSensorIndicators(data) {
    console.log("Updating sensor indicators with data:", data);
    Object.keys(data).forEach((cage) => {
      // Split and map the sensors_values string to an array of numbers
      const sensors = data[cage].sensors_values.replace(/[()]/g, "").split(",").map(Number);
  
      // Update Load Sensor Cell
      const loadSensorCell = document.querySelector(`#${cage}_load-sensor-cell`);
      if (loadSensorCell) {
        loadSensorCell.classList.remove("indicator-sensor");
        if (sensors.length > 0 && sensors[0] > 100) {
          loadSensorCell.classList.add("indicator-sensor");
        }
      } else {
        console.error(`No load sensor cell found for ${cage}`);
      }
  
      // Update Unload Sensor Cell
      const unloadSensorCell = document.querySelector(`#${cage}_unload-sensor-cell`);
      if (unloadSensorCell) {
        unloadSensorCell.classList.remove("indicator-sensor");
        if (sensors.length > 1 && sensors[1] > 100) {
          unloadSensorCell.classList.add("indicator-sensor");
        }
      } else {
        console.error(`No unload sensor cell found for ${cage}`);
      }
  
      // Update Buffer Sensor Cell
      const bufferSensorCell = document.querySelector(`#${cage}_buffer-sensor-cell`);
      if (bufferSensorCell) {
        bufferSensorCell.classList.remove("indicator-sensor");
        if (sensors.length > 2 && sensors[2] > 100) {
          bufferSensorCell.classList.add("indicator-sensor");
        }
      } else {
        console.error(`No buffer sensor cell found for ${cage}`);
      }
    });
  }
  
  
//   function updateSensorIndicators(data) {
//     console.log("Updating sensor indicators with data:", data);
//     Object.keys(data).forEach((cage) => {
//       const sensors = data[cage].sensors_values.replace(/[()]/g, "").split(",").map(Number);
//       const loadSensorCell = document.querySelector(`#${cage}_load-sensor-cell`);
//       if (loadSensorCell) {
//         loadSensorCell.classList.remove("indicator-sensor");
//         if (sensors.length > 0 && sensors[0] > 100) {
//           loadSensorCell.classList.add("indicator-sensor");
//         }
//       } else {
//         console.error(`No load sensor cell found for ${cage}`);
//       }
//     });
//   }
  