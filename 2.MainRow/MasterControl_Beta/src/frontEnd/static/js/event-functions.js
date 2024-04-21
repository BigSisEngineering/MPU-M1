document.addEventListener('DOMContentLoaded', function() {
    const tableHead = document.querySelector('thead tr');
    const tableBody = document.querySelector('tbody');

    // Generate headers for cages
    for (let i = 2; i <= 15; i++) {
        let th = document.createElement('th');
        let a = document.createElement('a');
        let cageNum = `cage${i.toString().padStart(2, '0')}`;
        a.textContent = cageNum;
        a.href = `http://${cageNum}:8080`; // Set URL as needed
        a.target = "_blank"; // Opens link in a new tab
        th.appendChild(a);
        tableHead.appendChild(th);
    }

    // Define the rows and their respective classes and symbols
    const rows = [
        { name: 'Mode', className: 'mode-cell', symbol: '' },
        { name: 'Star Wheel', className: 'gear-cell', symbol: 'fa-solid fa-gear' },
        { name: 'Unloader', className: 'gear-cell', symbol: 'fa-solid fa-gear' },
        { name: 'Buffer Sensor', className: 'sensor-cell', symbol: '' },
        { name: 'Load Sensor', className: 'sensor-cell', symbol: '' },
        { name: 'Unload Sensor', className: 'sensor-cell', symbol: '' }
    ];

    // Generate the rows
    rows.forEach(row => {
        let tr = document.createElement('tr');
        let tdName = document.createElement('td');
        tdName.textContent = row.name;
        tr.appendChild(tdName);

        for (let i = 2; i <= 15; i++) {
            let td = document.createElement('td');
            td.className = row.className;
            if (row.symbol) {
                let icon = document.createElement('i');
                icon.className = row.symbol;
                td.appendChild(icon);
            }
            tr.appendChild(td);
        }
        tableBody.appendChild(tr);
    });

    // Adding checkboxes for cage selection
    const container = document.getElementById('cage-checkboxes');
    for (let i = 2; i <= 15; i++) {
        const cageNum = `cage${i.toString().padStart(2, '0')}`;
        const checkboxDiv = document.createElement('div');
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.id = cageNum;
        checkbox.className = 'cage-checkbox';
        const label = document.createElement('label');
        label.htmlFor = cageNum;
        label.textContent = cageNum;
        
        checkboxDiv.appendChild(checkbox);
        checkboxDiv.appendChild(label);
        container.appendChild(checkboxDiv);
    }

    // Function to select or deselect all cages
    const selectAllCheckbox = document.getElementById('select-all');
    selectAllCheckbox.addEventListener('change', function() {
        document.querySelectorAll('.cage-checkbox').forEach(chk => {
            chk.checked = this.checked;
        });
    });

    // Function to check execution conditions
    const executeButton = document.getElementById('execute-action');
    const cageCheckboxes = document.querySelectorAll('.cage-checkboxes input[type="checkbox"]');
    const actionCheckboxes = document.querySelectorAll('.action-checkboxes input[type="checkbox"]');

    executeButton.addEventListener('click', function() {
        const cagesSelected = Array.from(cageCheckboxes).some(checkbox => checkbox.checked);
        const actionsSelected = Array.from(actionCheckboxes).filter(checkbox => checkbox.checked);

        if (!cagesSelected) {
            alert('Please select at least one cage.');
        } else if (actionsSelected.length === 0) {
            alert('Please select an action.');
        } else if (actionsSelected.length > 1) {
            alert('Only one action can be selected at a time.');
        }
    });
});
