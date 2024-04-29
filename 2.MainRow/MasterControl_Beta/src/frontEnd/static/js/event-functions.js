document.addEventListener('DOMContentLoaded', function() {
    const tableHead = document.querySelector('thead tr');
    const tableBody = document.querySelector('tbody');

    // Ensure table elements are found
    if (!tableHead || !tableBody) {
        console.error('Table head or body elements are not found!');
        return;
    }

    // Generate headers for cages
    for (let i = 2; i <= 15; i++) {
        let th = document.createElement('th');
        let a = document.createElement('a');
        let cageNum = (i <= 9) ? `cage0x000${i}` : `cage0x00${i}`;
        a.textContent = cageNum;
        a.href = `http://${cageNum}:8080`;
        a.target = "_blank";
        th.appendChild(a);
        tableHead.appendChild(th);
    }

    // Define the rows and their respective classes and symbols
    const rows = [
        { name: 'Mode', className: 'mode-cell', symbol: '' },
        { name: 'Star Wheel', className: 'gear-cell star-wheel', symbol: 'fa-solid fa-gear' },
        { name: 'Unloader', className: 'gear-cell unloader', symbol: 'fa-solid fa-gear' },
        { name: 'Buffer Sensor', className: 'sensor-cell', symbol: '' },
        { name: 'Load Sensor', className: 'sensor-cell', symbol: '' },
        { name: 'Unload Sensor', className: 'sensor-cell', symbol: '' }
    ];

    rows.forEach(row => {
        let tr = document.createElement('tr');
        let tdName = document.createElement('td');
        tdName.textContent = row.name;
        tr.appendChild(tdName);

        for (let i = 2; i <= 15; i++) {
            let td = document.createElement('td');
            td.className = row.className;
            td.dataset.cage = `cage0x00${i <= 9 ? `0${i}` : i}`;
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
        let cageNum = (i <= 9) ? `cage0x000${i}` : `cage0x00${i}`;
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
    executeButton.addEventListener('click', function() {
        const cagesSelected = Array.from(document.querySelectorAll('.cage-checkbox:checked')).length;
        const actionsSelected = Array.from(document.querySelectorAll('.action-checkbox:checked')).length;

        if (cagesSelected === 0) {
            alert('Please select at least one cage.');
        } else if (actionsSelected === 0) {
            alert('Please select an action.');
        } else if (actionsSelected > 1) {
            alert('Only one action can be selected at a time.');
        }
    });
});
