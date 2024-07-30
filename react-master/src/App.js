import React from "react";
import "./Assets/Styles/styles.css";
import Header from "./Layouts/Header/index.js";
import AlertBox from "./Layouts/AlertBox/index.js";
import M1A from "./Layouts/M1A/index.js";
import M1C from "./Layouts/M1C/index.js";
import Cages from "./Layouts/Cages/index.js";

// temp
import SystemStatus from "./Layouts/SystemStatus/index.js";
import ControlPanel from "./Layouts/ControlPanel/index.js";
import Settings from "./Layouts/Settings/index.js";
import ActuatorStatus from "./Layouts/ActuatorStatus/index.js";
import OperationControl from "./Layouts/OperationControl/index.js";
import CCTV from "./Layouts/CCTV/index.js";
import MainMessage from "./Layouts/MainMessage/index.js";
import EmergencyStop from "./Layouts/EmergencyStop/index.js";

/* ---------------------------------------------------------------------------------- */
let moduleNumber;
let rowNumber;

function getLocalHostname() {
  const hostname = window.location.hostname;
  console.log("Hostname:", hostname);

  const match = hostname.match(/^m(\d+)-(\d+)-m$/);

  if (match) {
    moduleNumber = parseInt(match[1], 10);
    rowNumber = parseInt(match[2], 10);
  } else {
    console.log("Debug");
    moduleNumber = 1;
    rowNumber = 1;
  }

  return hostname;
}

document.addEventListener("DOMContentLoaded", function () {
  const localHostname = getLocalHostname();
  document.title = `${localHostname}`;
});

document.addEventListener("DOMContentLoaded", function () {
  const localHostname = getLocalHostname();
  document.title = `${localHostname}`;
});

/* ================================================================================== */
/*                                     Main Blocks                                    */
/* ================================================================================== */
function MainContent() {
  return (
    <div className="mains-container">
      <LeftColumn />
      <RightColumn />
    </div>
  );
}

function LeftColumn() {
  return (
    <div className="columns-container" style={{ width: "22%" }}>
      <M1A />
      <M1C />
      <OperationControl />
      {/* <SystemStatus />
      <ControlPanel />
      <Settings />
      <EmergencyStop /> */}
    </div>
  );
}

function RightColumn() {
  return (
    <div
      className="columns-container"
      style={{ width: "76%", padding: "0px 0px", marginBottom: "0px", alignItems: "center" }}
    >
      <Cages row={1} />
      {/* <MainMessage /> */}
      {/* <CCTV /> */}
      {/* <ActuatorStatus /> */}
    </div>
  );
}

export default function Webapp() {
  return (
    <>
      <AlertBox content="Hello" />
      <Header module={moduleNumber} unit={"Master"} row={rowNumber} />
      <MainContent />
    </>
  );
}
