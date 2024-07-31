const DEFAULT_MSG = "⏳";
const DEFAULT_BOOL = false;
let _alertTimeout;

function toggleDebugMode(bool) {
  const debugContainers = document.querySelectorAll(".debug-container");
  if (bool) {
    debugContainers.forEach(function (container) {
      container.classList.remove("hidden");
    });
  } else {
    debugContainers.forEach(function (container) {
      container.classList.add("hidden");
    });
  }
}

function getColor(colour) {
  switch (colour) {
    case "GREEN":
      return "rgba(189, 213, 104, 0.57)";
    case "RED":
      return "rgba(255, 35, 0, 0.57)";
    case "YELLOW":
      return "rgba(249, 213, 49, 0.57)";
    case "BLUE":
      return "rgba(0, 114, 255, 0.57)";
    default:
      return "rgba(148, 148, 148, 1)";
  }
}

function openLink(link) {
  console.log(link);
  window.open(link, "_blank");
}

async function fetchJSON(url) {
  try {
    const response = await fetch(url, {
      method: "GET",
    });

    if (!response.ok) {
      throw new Error("Network response was not ok");
    }

    return await response.json();
  } catch (error) {
    throw error;
  }
}

async function httpPOST(url, data = null) {
  const options = {
    method: "POST",
    headers: {},
  };

  if (data !== null) {
    options.headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(data);
  }

  return fetch(url, options)
    .then((response) => {
      if (response.ok) {
        return response.text();
      } else {
        console.log("Error");
        throw new Error("Network response was not ok");
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      throw error;
    });
}

function _showAlert(message, timeout = 3000) {
  const alertDiv = document.getElementById("alert-box");
  try {
    alertDiv.innerText = message;
    alertDiv.style.display = "block";

    if (_alertTimeout) {
      clearTimeout(_alertTimeout);
    }

    _alertTimeout = setTimeout(() => {
      alertDiv.style.display = "none";
      alertDiv.style.background = getColor("GREY");
    }, timeout);
  } catch (error) {
    console.log(error);
  }
}

async function exec(operationName, func, ...args) {
  const message = "Executing " + operationName + "...";

  _showAlert(message);

  try {
    const result = await func(...args);
    _showAlert(`✔️ ${result}`);
  } catch (error) {
    _showAlert(`❌ Failed to execute ${operationName}`);
  }
}

export { toggleDebugMode, getColor, openLink, fetchJSON, httpPOST, exec, DEFAULT_MSG, DEFAULT_BOOL };
