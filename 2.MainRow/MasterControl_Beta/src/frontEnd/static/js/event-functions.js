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
        { name: "Buffer Sensor", className: "sensor-cell", symbol: "" },
        { name: "Load Sensor", className: "sensor-cell", symbol: "" },
        { name: "Unload Sensor", className: "sensor-cell", symbol: "" }
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
    fetch('http://localhost:8080/get_all_cages_status')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok: ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            updateCageIndicators(data);
        })
        .catch(error => {
            console.error('Error fetching cage status:', error);
        });
}

function updateCageIndicators(data) {
    Object.keys(data).forEach(cage => {
        const cageStatus = data[cage];
        // Convert 'cage0x0008' to 'cage08'
        const cageId = 'cage' + parseInt(cage.match(/0x(\d+)/)[1], 16).toString().padStart(2, '0');
        const modeIndicator = document.querySelector('#' + cageId + ' .mode-cell span');

        if (modeIndicator) {
            modeIndicator.className = 'status-circle'; // Reset the class to default
            switch (cageStatus.mode) {
                case 'pnp':
                    modeIndicator.classList.add('green');
                    break;
                case 'dummy':
                    modeIndicator.classList.add('blue');
                    break;
                case 'idle':
                    modeIndicator.classList.add('grey');
                    break;
                default:
                    modeIndicator.classList.add('black');
            }
        }
    });
}
