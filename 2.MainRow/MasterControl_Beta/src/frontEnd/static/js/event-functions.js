document.addEventListener("DOMContentLoaded", function () {
    // Initial setup tasks
    setupPageElements();

    // Fetch and update cage statuses
    fetchCageStatus();
});

function setupPageElements() {
    const tableHead = document.querySelector("thead tr");
    const tableBody = document.querySelector("tbody");

    // Generate headers for cages
    for (let i = 2; i <= 15; i++) {
        let th = document.createElement("th");
        let a = document.createElement("a");
        let cageNum = `cage${i.toString().padStart(2, "0")}`;
        a.textContent = cageNum;
        a.href = `http://${cageNum}:8080`;
        a.target = "_blank"; // Opens link in a new tab
        th.appendChild(a);
        tableHead.appendChild(th);
    }

    // Define and generate rows
    generateRows(tableBody);

    // Setup checkboxes for cage selection
    setupCageSelection();
  
    // Setup action execution
    setupActionExecution();
}

function generateRows(tableBody) {
    const rows = [
        { name: "Mode", className: "mode-cell", symbol: "" },
        { name: "Star Wheel", className: "gear-cell", symbol: "fa-solid fa-gear" },
        { name: "Unloader", className: "gear-cell", symbol: "fa-solid fa-gear" },
        { name: "Load Sensor", className: "load-sensor-cell", symbol: "" },
        { name: "Unload Sensor", className: "unload-sensor-cell", symbol: "" },
        { name: "Buffer Sensor", className: "buffer-sensor-cell", symbol: "" }
    ];

    rows.forEach(row => {
        let tr = document.createElement("tr");
        let tdName = document.createElement("td");
        tdName.textContent = row.name;
        tr.appendChild(tdName);

        for (let i = 2; i <= 15; i++) {
            let td = document.createElement("td");
            td.id = `cage${i.toString().padStart(2, "0")}`;
            td.className = row.className;
            if (row.symbol) {
                let icon = document.createElement("i");
                icon.className = row.symbol;
                td.appendChild(icon);
            }
            tr.appendChild(td);
        }
        tableBody.appendChild(tr);
    });
}

function setupCageSelection() {
    const container = document.getElementById("cage-checkboxes");
    for (let i = 2; i <= 15; i++) {
        const cageNum = `cage${i.toString().padStart(2, "0")}`;
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
    }

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
        const cagesSelected = Array.from(cageCheckboxes).some(chk => chk.checked);
        const actionsSelected = Array.from(actionCheckboxes).filter(chk => chk.checked);

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
    Object.keys(data).forEach(cage => {
        const cageStatus = data[cage];
        if (typeof cageStatus === 'string' && cageStatus.startsWith("<urlopen error")) {
            console.log(cage + " has an error: " + cageStatus);
            return;
        }

        const cageId = 'cage' + parseInt(cage.match(/0x(\d+)/)[1], 16).toString().padStart(2, '0');
        const modeIndicator = document.querySelector('#' + cageId);

        if (modeIndicator) {
            // Remove previous color classes
            modeIndicator.classList.remove('indicator-pnp', 'indicator-dummy', 'indicator-idle', 'indicator-offline');

            // Add the appropriate class based on the mode
            let statusClass = '';
            switch (cageStatus.mode) {
                case 'pnp':
                    statusClass = 'indicator-pnp';
                    break;
                case 'dummy':
                    statusClass = 'indicator-dummy';
                    break;
                case 'idle':
                    statusClass = 'indicator-idle';
                    break;
                default:
                    statusClass = 'indicator-offline'; // Use for unknown or error states
                    break;
            }
            modeIndicator.classList.add(statusClass);
        } else {
            console.error("No mode indicator found for " + cageId);
        }
    });
}


function updateSensorIndicators(data) {
    console.log("Updating sensor indicators with data:", data); // Check incoming data
    Object.keys(data).forEach(cage => {
        const cageStatus = data[cage];
        console.log(`Processing cage: ${cage}`, cageStatus); // Log each cage's status

        if (typeof cageStatus === 'string' && cageStatus.startsWith("<urlopen error")) {
            console.error(cage + " has an error: " + cageStatus);
            return;
        }

        const cageId = `cage${parseInt(cage.match(/0x(\d+)/)[1], 16).toString().padStart(2, '0')}`;
        const sensorElementsExist = document.querySelector(`#${cageId} .load-sensor-cell`) !== null;
        console.log(`Sensor elements exist for ${cageId}:`, sensorElementsExist); // Verify element selection

        const sensors = cageStatus.sensors_values ? cageStatus.sensors_values.slice(1, -1).split(',').map(Number) : [];
        console.log(`Sensor values for ${cageId}:`, sensors); // Log parsed sensor values

        updateSensorIndicator(document.querySelector(`#${cageId} .load-sensor-cell`), sensors[0]);
        updateSensorIndicator(document.querySelector(`#${cageId} .unload-sensor-cell`), sensors[1]);
        updateSensorIndicator(document.querySelector(`#${cageId} .buffer-sensor-cell`), sensors[2]);
    });
}


function updateSensorIndicator(sensorElement, value) {
    if (sensorElement) {
        sensorElement.classList.remove('indicator-sensor');
        if (value > 100) {
            sensorElement.classList.add('indicator-sensor');
        }
    }
}



