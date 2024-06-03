document.addEventListener("DOMContentLoaded", function () {
    setupPageElements();
    // fetchCageStatus();
    // fetchPotSorterStatus(); 
    // simulateFetchCageStatus();
    fetchStatuses(); 
    const controller = new Controller_1A_1C();
  });
  
  function setupPageElements() {
    const tableHead = document.querySelector("thead tr");
    const tableBody = document.querySelector("tbody");
  
    // Define specific ranges
    const cages = [
      ...Array.from({ length: 9 }, (_, i) => i + 1), // Generates 1 to 9
      ...Array.from({ length: 5 }, (_, i) => i + 14) // Generates 16 to 21
    ].map((i) => `cage1x${i.toString(14).padStart(4, "0")}`);
  
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
    const actionCheckboxes = document.querySelectorAll('.action-checkboxes input[type="checkbox"]');
    const post_request_dict = {
        "star-wheel-init": "STAR_WHEEL_INIT",
        "unloader-init": "UNLOADER_INIT",
        "clear-star-wheel-error": "CLEAR_STAR_WHEEL_ERROR",
        "clear-unloader-error": "CLEAR_UNLOADER_ERROR",
        "enable-dummy": "ENABLE_DUMMY",
        "disable-dummy": "DISABLE_DUMMY",
        "enable-pnp": "ENABLE_PNP",
        "disable-pnp": "DISABLE_PNP",
        "move-star-wheel-cw": 'MOVE_CW',
        "move-star-wheel-ccw": 'MOVE_CCW'
    };

    executeButton.addEventListener("click", function () {
        const selectedCages = Array.from(cageCheckboxes).filter(chk => chk.checked).map(chk => chk.id);
        const selectedActions = Array.from(actionCheckboxes).filter(chk => chk.checked).map(chk => post_request_dict[chk.value]);

        if (selectedCages.length === 0) {
            alert("Please select at least one cage.");
        } else if (selectedActions.length === 0) {
            alert("Please select an action.");
        } else if (selectedActions.length > 1) {
            alert("Only one action can be selected at a time.");
        } else {
            // Assuming only one action can be selected and is being handled here
            sendCagesAndActionToBackend(selectedCages, selectedActions[0]);
        }
    });
  }

  function sendCagesAndActionToBackend(cages, action) {
    fetch('/execute_actions', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ cages: cages, action: action })
    })
    .then(response => {
      if (!response.ok) {
          throw new Error(`HTTP error, status = ${response.status}`);
      }
      return response.json();
    })
    .then(data => console.log('Server response:', data))
    .catch(error => console.error('Error sending data to the server:', error));
}

   
  class CageStatusUpdater {
    constructor(data) {
      this.data = data;
    }
  
    updateAllStatuses() {
      this.ModeIndicators();
      this.SensorIndicators();
      this.GearStatuses();
    }
  
    ModeIndicators() {
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
  
    SensorIndicators() {
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
        this.SensorIndicator(`${cage}_load-sensor-cell`, sensors, 0);
        this.SensorIndicator(`${cage}_unload-sensor-cell`, sensors, 1);
        this.SensorIndicator(`${cage}_buffer-sensor-cell`, sensors, 2);
      });
    }
  
    SensorIndicator(elementId, sensors, index) {
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
  
    GearStatuses() {
      Object.keys(this.data).forEach((cage) => {
        this.GearColor(
          cage,
          "star_wheel",
          this.data[cage].star_wheel_status
        );
        this.GearColor(cage, "unloader", this.data[cage].unloader_status);
      });
    }
  
    GearColor(cage, gearType, status) {
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

  class PotSorterStatusUpdater {
    constructor(a1Data) {
        this.a1Data = a1Data;
    }

    updateStatus() {
        this.PotSorterMode();
        this.PotSorterConnection();
    }

    PotSorterConnection() {
      const connectionIndicator = document.querySelector('.pot-sorter-connection');
      if (this.a1Data.connected === "True") {
          connectionIndicator.textContent = 'Connected';
          connectionIndicator.style.backgroundColor = '#4caf50'; // Green for connected
      } else {
          connectionIndicator.textContent = 'Disconnected';
          connectionIndicator.style.backgroundColor = 'grey'; // Grey for disconnected
      }
    }

    PotSorterMode() {
        const potSorterIndicator = document.querySelector('.pot-sorter-mode'); 
        if (this.a1Data.connected === "True" && this.a1Data.running === "True" && this.a1Data.buff_out === "True") {
            potSorterIndicator.textContent = 'Running';
            potSorterIndicator.style.backgroundColor = '#4caf50'; // Green for running
        } else if (this.a1Data.connected === "True" && this.a1Data.running === "True" && this.a1Data.buff_out === "False") {
            potSorterIndicator.textContent = 'Waiting';
            potSorterIndicator.style.backgroundColor = 'orange'; // Yellow for waiting
        } else if (this.a1Data.connected === "True" && this.a1Data.running === "False" || this.a1Data.connected === "False") {
            potSorterIndicator.textContent = 'Idle';
            potSorterIndicator.style.backgroundColor = 'grey'; // Grey for idle
        } else {
            potSorterIndicator.textContent = 'Unknown'; // Fallback status
            potSorterIndicator.style.backgroundColor = 'red'; // Red for unknown or error states
        }
    }
  }

  class DietDispenserStatusUpdater {
    constructor(a2Data) {
        this.a2Data = a2Data;
    }

    updateStatus() {
        this.DietDispenserMode();
        this.DietDispenserConnection();
    }

    DietDispenserConnection() {
      const connectionIndicator = document.querySelector('.diet-dispenser-connection');
      if (this.a2Data.connected === "True") {
          connectionIndicator.textContent = 'Connected';
          connectionIndicator.style.backgroundColor = '#4caf50'; // Green for connected
      } else {
          connectionIndicator.textContent = 'Disconnected';
          connectionIndicator.style.backgroundColor = 'grey'; // Grey for disconnected
      }
    }

    DietDispenserMode() {
        const DDIndicator = document.querySelector('.diet-dispenser-mode'); 
        if (this.a2Data.connected === "True" && 
          this.a2Data.running === "True" && 
          this.a2Data.dispenser_homed === "True" && 
          this.a2Data.sw_error === "False" && 
          this.a2Data.sw_homed === "True" &&
          this.a2Data.buff_in === "False" &&
          this.a2Data.buff_out === "True"
          ) {
            DDIndicator.textContent = 'Running';
            DDIndicator.style.backgroundColor = '#4caf50'; // Green for running
            
        } else if (this.a2Data.connected === "True" && 
          this.a2Data.running === "True" && 
          this.a2Data.dispenser_homed === "True" && 
          this.a2Data.sw_error === "False" && 
          this.a2Data.sw_homed === "True" &&
          (this.a2Data.buff_in === "True" || this.a2Data.buff_out === "False")) {
            DDIndicator.textContent = 'Waiting';
            DDIndicator.style.backgroundColor = 'orange'; // Yellow for waiting

        } else if (this.a2Data.running === "False") {
            DDIndicator.textContent = 'Idle';
            DDIndicator.style.backgroundColor = 'grey'; // Grey for idle

        } else if (this.a2Data.connected === "True" && this.a2Data.sw_error === "True") {
          DDIndicator.textContent = 'SW Fault';
          DDIndicator.style.backgroundColor = 'red'; 
      } 
    }
  }

  class PotDispenserStatusUpdater {
    constructor(a3Data) {
        this.a3Data = a3Data;
    }

    updateStatus() {
        this.PotDispenserMode();
        this.PotDispenserConnection();
    }

    PotDispenserConnection() {
      const connectionIndicator = document.querySelector('.pot-dispenser-connection');
      if (this.a3Data.connected === "True") {
          connectionIndicator.textContent = 'Connected';
          connectionIndicator.style.backgroundColor = '#4caf50'; // Green for connected
      } else {
          connectionIndicator.textContent = 'Disconnected';
          connectionIndicator.style.backgroundColor = 'grey'; // Grey for disconnected
      }
    }

    PotDispenserMode() {
        const PDIndicator = document.querySelector('.pot-dispenser-mode'); 
        if (this.a3Data.connected === "True" && 
          this.a3Data.running === "True" && 
          this.a3Data.sw_error === "False" && 
          this.a3Data.sw_homed === "True" &&
          this.a3Data.buff_in === "False") {
            PDIndicator.textContent = 'Running';
            PDIndicator.style.backgroundColor = '#4caf50'; // Green for running
            
        } else if (this.a3Data.connected === "True" && 
          this.a3Data.running === "True" && 
          this.a3Data.sw_error === "False" && 
          this.a3Data.sw_homed === "True" &&
          this.a3Data.buff_in === "True" ) {
            PDIndicator.textContent = 'Waiting';
            PDIndicator.style.backgroundColor = 'orange'; // orange for waiting

        } else if ((this.a3Data.connected === "True" && this.a3Data.running === "False") ||  this.a3Data.connected === "False") {
            PDIndicator.textContent = 'Idle';
            PDIndicator.style.backgroundColor = 'grey'; // Grey for idle

        } else if (this.a3Data.connected === "True" && this.a3Data.sw_error === "True") {
          PDIndicator.textContent = 'SW Fault';
          PDIndicator.style.backgroundColor = 'red'; 

        } else if (this.a3Data.connected === "True" && this.a3Data.sw_error === "False" &&  this.a3Data.sw_homed === "false" ) {
          PDIndicator.textContent = 'SW Not Homed';
          PDIndicator.style.backgroundColor = 'red'; 
        } 
    }
  }


  class ChimneySorterStatusUpdater {
    constructor(c1Data) {
        this.c1Data = c1Data;
    }

    updateStatus() {
        this.ChimneySorterMode();
        this.ChimneySorterConnection();
        this.ChimneySorterChannels();
    }

    ChimneySorterConnection() {
      const connectionIndicator = document.querySelector('.chimney-sorter-connection');
      if (this.c1Data.connected === "True") {
          connectionIndicator.textContent = 'Connected';
          connectionIndicator.style.backgroundColor = '#4caf50'; // Green for connected
      } else {
          connectionIndicator.textContent = 'Disconnected';
          connectionIndicator.style.backgroundColor = 'grey'; // Grey for disconnected
      }
    }

    ChimneySorterMode() {
        const chimenySorterIndicator = document.querySelector('.chimney-sorter-mode'); 
        if (this.c1Data.connected === "True" && this.c1Data.running === "True" && this.c1Data.buff_out === "True") {
          chimenySorterIndicator.textContent = 'Running';
          chimenySorterIndicator.style.backgroundColor = '#4caf50'; // Green for running

        } else if (this.c1Data.connected === "True" && this.c1Data.running === "True" && this.c1Data.buff_out === "False") {
          chimenySorterIndicator.textContent = 'Waiting';
          chimenySorterIndicator.style.backgroundColor = 'orange'; // Yellow for waiting

        } else if ((this.c1Data.connected === "True" && this.c1Data.running === "False") || this.c1Data.connected === "False") {
          chimenySorterIndicator.textContent = 'Idle';
          chimenySorterIndicator.style.backgroundColor = 'grey'; // Grey for idle
        }
      }

      ChimneySorterChannels() {
        const SensorStatus = (selector, status) => {
          const element = document.querySelector(selector);
          element.style.backgroundColor = status === "True" ? '#4caf50' : 'grey';
        };
      
        SensorStatus('.status-channel-1', this.c1Data.ch1_sensor);
        SensorStatus('.status-channel-2', this.c1Data.ch2_sensor);
        SensorStatus('.status-channel-3', this.c1Data.ch3_sensor);
      }
      
    
    }
  
  class ChimneyPlacerStatusUpdater {
      constructor(c3Data) {
          this.c3Data = c3Data;
      }
  
      updateStatus() {
          this.ChimneyPlacerMode();
          this.ChimneyPlacerConnection();
          this.ChimneyPlacerSensors();
      }
  
      ChimneyPlacerConnection() {
        const connectionIndicator = document.querySelector('.chimney-placer-connection');
        if (this.c3Data.connected === "True") {
            connectionIndicator.textContent = 'Connected';
            connectionIndicator.style.backgroundColor = '#4caf50'; // Green for connected
        } else {
            connectionIndicator.textContent = 'Disconnected';
            connectionIndicator.style.backgroundColor = 'grey'; // Grey for disconnected
        }
      }
  
      ChimneyPlacerMode() {
          const chimenySorterIndicator = document.querySelector('.chimney-sorter-mode'); 
          if (this.c3Data.connected === "True" && this.c3Data.running === "True" && this.c3Data.pot_sensor === "True" && this.c3Data.chimney_sensor === "True") {
            chimenySorterIndicator.textContent = 'Running';
            chimenySorterIndicator.style.backgroundColor = '#4caf50'; // Green for running
  
          } else if (this.c3Data.connected === "True" && this.c3Data.running === "True" && (this.c3Data.pot_sensor === "False" || this.c3Data.chimney_sensor === "False")) {
            chimenySorterIndicator.textContent = 'Waiting';
            chimenySorterIndicator.style.backgroundColor = 'orange'; // Yellow for waiting
  
          } else if ((this.c3Data.connected === "True" && this.c3Data.running === "False") || this.c3Data.connected === "False") {
            chimenySorterIndicator.textContent = 'Idle';
            chimenySorterIndicator.style.backgroundColor = 'grey'; // Grey for idle
          }
        }
  
        ChimneyPlacerSensors() {
          const SensorStatus = (selector, status) => {
            const element = document.querySelector(selector);
            element.style.backgroundColor = status === "True" ? '#4caf50' : 'grey';
          };
        
          SensorStatus('.status-chimney-sensor', this.c3Data.chimney_sensor);
          SensorStatus('.status-pot-sensor', this.c3Data.pot_sensor);
        }
        
      
      }
  


  function fetchStatuses() {
    setInterval(() => {
        fetch('./static/js/cage_status.json')  // Ensure the path matches where your JSON is served
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok: ' + response.statusText);
                }
                return response.json();
            })
            .then(data => {
                // Update cage statuses
                const cageStatusUpdater = new CageStatusUpdater(data.b);
                cageStatusUpdater.updateAllStatuses();

                // Update pot sorter status
                const potSorterStatusUpdater = new PotSorterStatusUpdater(data.a1);
                potSorterStatusUpdater.updateStatus();

                const  dietDispenserStatusUpdater  = new  DietDispenserStatusUpdater(data.a2);
                dietDispenserStatusUpdater.updateStatus();

                const  potDispenserStatusUpdater  = new  PotDispenserStatusUpdater(data.a3);
                potDispenserStatusUpdater.updateStatus();

                const  chimneySorterStatusUpdater  = new  ChimneySorterStatusUpdater(data.c1);
                chimneySorterStatusUpdater.updateStatus();

                const  chimneyPlacerStatusUpdater  = new  ChimneyPlacerStatusUpdater(data.c1);
                chimneyPlacerStatusUpdater.updateStatus();
            })
            .catch(error => {
                console.error('Error fetching statuses:', error);
            });
    }, 3500); // Fetch and update every 3000 milliseconds (3 seconds)
  }



class Controller_1A_1C {
  constructor() {
      this.is1AActive = false;
      this.is1CActive = false;
      this.addTen = false;
      this.setZero = false;
      this.setupEventListeners();
  }

  setupEventListeners() {
      const start1AButton = document.getElementById('start-1A');
      const stop1AButton = document.getElementById('stop-1A');
      const start1CButton = document.getElementById('start-1C');
      const stop1CButton = document.getElementById('stop-1C');
      const addTenButton = document.getElementById('add');
      const setZeroButton = document.getElementById('zero');

      if (start1AButton && stop1AButton && start1CButton && stop1CButton && addTenButton && setZeroButton) {
          start1AButton.addEventListener('click', () => this.start1A());
          stop1AButton.addEventListener('click', () => this.stop1A());
          start1CButton.addEventListener('click', () => this.start1C());
          stop1CButton.addEventListener('click', () => this.stop1C());
          addTenButton.addEventListener('click', () => this.addTenPots());
          setZeroButton.addEventListener('click', () => this.setZeroPots());
      } else {
          console.error('One or more buttons not found. Please check your button IDs.');
      }
  }

  sendState() {
      fetch('/control_1A_1C', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
          },
          body: JSON.stringify({
              is1AActive: this.is1AActive,
              is1CActive: this.is1CActive,
              addTen: this.addTen,
              setZero: this.setZero
          })
      }).then(response => response.json())
        .then(data => console.log(data))
        .catch(error => console.error('Error:', error));
  }

  start1A() {
      this.is1AActive = true;
      console.log("1A started:", this.is1AActive);
      this.sendState();
  }

  stop1A() {
      this.is1AActive = false;
      console.log("1A stopped:", this.is1AActive);
      this.sendState();
  }

  start1C() {
      this.is1CActive = true;
      console.log("1C started:", this.is1CActive);
      this.sendState();
  }

  stop1C() {
      this.is1CActive = false;
      console.log("1C stopped:", this.is1CActive);
      this.sendState();
  }
  addTenPots() {
    this.addTen = true;
    console.log("Added 10 Pots:", this.addTen);
    this.sendState();
    this.addTen = false;
  }

  setZeroPots() {
    this.setZero = true;
    console.log("Set to 0:", this.setZero);
    this.sendState();
    this.setZero = false;
  }
}
