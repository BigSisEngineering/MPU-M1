document.addEventListener("DOMContentLoaded", function () {
    setupPageElements();
    fetchCageStatus();
    // simulateFetchCageStatus();
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
      {
        name: "Star Wheel",
        className: "sw-gear-cell",
        symbol: "fa-solid fa-gear"
      },
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
    const actionCheckboxes = document.querySelectorAll(
      '.action-checkboxes input[type="checkbox"]'
    );
  
    executeButton.addEventListener("click", function () {
      const cagesSelected = Array.from(cageCheckboxes).some((chk) => chk.checked);
      const actionsSelected = Array.from(actionCheckboxes).filter(
        (chk) => chk.checked
      );
  
      if (!cagesSelected) {
        alert("Please select at least one cage.");
      } else if (actionsSelected.length === 0) {
        alert("Please select an action.");
      } else if (actionsSelected.length > 1) {
        alert("Only one action can be selected at a time.");
      }
    });
  }
  
//    function fetchCageStatus() {
    //     setInterval(() => {
    //     fetch('/get_all_cages_status')
    //         .then(response => {
    //         if (!response.ok) {
    //             throw new Error('Network response was not ok: ' + response.statusText);
    //         }
    //         return response.json();
    //         })
    //         .then(data => {
    //         // updateModeIndicators(data);
    //         // updateSensorIndicators(data);
    //         const statusUpdater = new CageStatusUpdater(data);
    //         statusUpdater.updateAllStatuses();
    //         })
    //         .catch(error => {
    //         console.error('Error fetching cage status:', error);
    //         });
    //     }, 3000); // Fetch every 3 seconds
    // }
    function fetchCageStatus() {
        setInterval(() => {
            // Adjust the path to point to the location of the JSON file relative to the HTML file
            fetch('./static/js/cage_status.json')
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok: ' + response.statusText);
                    }
                    return response.json();
                })
                .then(data => {
                    const statusUpdater = new CageStatusUpdater(data);
                    statusUpdater.updateAllStatuses();
                })
                .catch(error => {
                    console.error('Error fetching cage status:', error);
                });
        }, 3000); // Fetch every 3 seconds
    }
    
    
  class CageStatusUpdater {
    constructor(data) {
      this.data = data;
    }
  
    updateAllStatuses() {
      this.updateModeIndicators();
      this.updateSensorIndicators();
      this.updateGearStatuses();
    }
  
    updateModeIndicators() {
      Object.keys(this.data).forEach((cage) => {
        const modeIndicator = document.querySelector(`#${cage}_mode-cell`);
        if (modeIndicator) {
          modeIndicator.classList.remove(
            "indicator-pnp",
            "indicator-dummy",
            "indicator-idle",
            "indicator-offline"
          );
          const statusClass = "indicator-" + (this.data[cage].mode || "offline");
          modeIndicator.classList.add(statusClass);
        } else {
          console.error("No mode indicator found for " + cage);
        }
      });
    }
  
    updateSensorIndicators() {
      Object.keys(this.data).forEach((cage) => {
        if (
          typeof this.data[cage] === "string" ||
          this.data[cage].sensors_values === undefined ||
          this.data[cage].sensors_values.startsWith("<error>")
        ) {
          const sensorCells = [
            document.querySelector(`#${cage}_load-sensor-cell`),
            document.querySelector(`#${cage}_unload-sensor-cell`),
            document.querySelector(`#${cage}_buffer-sensor-cell`)
          ];
          sensorCells.forEach((cell) => {
            if (cell) {
              cell.classList.remove("indicator-sensor");
              cell.classList.add("indicator-not-triggered");
            } else {
              console.error(`No sensor cell found for ${cage}`);
            }
          });
          return;
        }
        const sensors = this.data[cage].sensors_values
          .replace(/[()]/g, "")
          .split(",")
          .map(Number);
        this.updateSensorIndicator(`${cage}_load-sensor-cell`, sensors, 0);
        this.updateSensorIndicator(`${cage}_unload-sensor-cell`, sensors, 1);
        this.updateSensorIndicator(`${cage}_buffer-sensor-cell`, sensors, 2);
      });
    }
  
    updateSensorIndicator(elementId, sensors, index) {
      const sensorCell = document.querySelector(`#${elementId}`);
      if (sensorCell) {
        sensorCell.classList.remove(
          "indicator-sensor",
          "indicator-not-triggered"
        );
        if (sensors.length > index && sensors[index] > 100) {
          sensorCell.classList.add("indicator-sensor");
        }
      } else {
        console.error(`No sensor cell found for ${elementId}`);
      }
    }
  
    updateGearStatuses() {
      Object.keys(this.data).forEach((cage) => {
        this.updateGearColor(
          cage,
          "star_wheel",
          this.data[cage].star_wheel_status
        );
        this.updateGearColor(cage, "unloader", this.data[cage].unloader_status);
      });
    }
  
    updateGearColor(cage, gearType, status) {
      const gearMap = {
        star_wheel: "_sw-gear-cell",
        unloader: "_ul-gear-cell"
      };
      const iconSelector = `#${cage}${gearMap[gearType]} i`;
      const icon = document.querySelector(iconSelector);
      if (icon) {
        icon.style.color = "black"; // Default color for undefined or unexpected statuses
        if (status === "normal") {
          icon.style.color = "#00ff00"; // Green for normal
        } else if (status === "overload") {
          icon.style.color = "red"; // Red for overload
        }
      } else {
        console.error(`No ${gearType} icon found for ${cage}`);
      }
    }
  }
  