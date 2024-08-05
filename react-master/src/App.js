import React from "react";
import { useState, useEffect } from "react";
import { useDict, Dicts } from "./Middleware/get-api.js";
import "./Assets/Styles/styles.css";
import Header from "./Layouts/Header/index.js";
import AlertBox from "./Layouts/AlertBox/index.js";
import M1A from "./Layouts/M1A/index.js";
import M1C from "./Layouts/M1C/index.js";
import Cages from "./Layouts/Cages/index.js";
import CageControl from "./Layouts/CageControl/index.js";
import OperationControl from "./Layouts/OperationControl/index.js";
import { DEFAULT_BOOL } from "./Utils/Utils.js";

/* ---------------------------------------------------------------------------------- */
let moduleNumber;
let rowNumber;

function generateDocumentTitle(module, row) {
  switch (module) {
    case 1:
      return `🥚 M1-${row} Master`;
    case 2:
      return `🪰 M2-${row} Master`;
    case 3:
      return `⚤ M3-${row} Master`;
    case 4:
      return `🛁 M4-${row} Master`;
    case 5:
      return `🩻 M5-${row} Master`;
    default:
      return `❓ MODULE NOT FOUND`;
  }
}

function getLocalHostname() {
  const hostname = window.location.hostname;
  console.log("Hostname:", hostname);

  const match = hostname.match(/^m(\d+)-(\d+)-m$/);

  if (match) {
    moduleNumber = 1;
    rowNumber = parseInt(match[2], 10);
  } else {
    moduleNumber = 1;
    rowNumber = 3;
  }
  console.log(rowNumber);
  return hostname;
}

document.addEventListener("DOMContentLoaded", function () {
  getLocalHostname();
  document.title = generateDocumentTitle(moduleNumber, rowNumber);
});

/* ================================================================================== */
/*                                     Main Blocks                                    */
/* ================================================================================== */
function MainContent() {
  // cage select
  const [isSelected, setIsSelected] = useState(Array(14).fill(false));
  const toggleSelected = (index) => () => {
    setIsSelected((prevSelected) => {
      const newIsSelected = [...prevSelected];
      newIsSelected[index] = !newIsSelected[index];
      return newIsSelected;
    });
  };

  const selectAll = () => {
    setIsSelected(Array(14).fill(true));
  };

  const clearAll = () => {
    setIsSelected(Array(14).fill(false));
  };

  // data update
  const [m1aRunning, setM1aRunning] = useState(DEFAULT_BOOL);
  const [m1cRunning, setM1cRunning] = useState(DEFAULT_BOOL);
  const dictSystem = useDict(Dicts.system);

  useEffect(() => {
    if (dictSystem) {
      setM1aRunning(dictSystem["1a"]);
      setM1cRunning(dictSystem["1c"]);
    } else {
      setM1aRunning(DEFAULT_BOOL);
      setM1cRunning(DEFAULT_BOOL);
    }
  }, [dictSystem]);

  /* ---------------------------------------------------------------------------------- */

  return (
    <div className="mains-container">
      <LeftColumn
        isSelected={isSelected}
        selectAll={selectAll}
        clearAll={clearAll}
        m1aRunning={m1aRunning}
        m1cRunning={m1cRunning}
      />
      <RightColumn isSelected={isSelected} setIsSelected={setIsSelected} toggleSelected={toggleSelected} />
    </div>
  );
}

function LeftColumn({ isSelected, selectAll, clearAll, m1aRunning, m1cRunning }) {
  return (
    <div className="columns-container" style={{ width: "22%" }}>
      <M1A row={rowNumber} m1aRunning={m1aRunning} />
      <M1C row={rowNumber} m1cRunning={m1cRunning} />
      <OperationControl m1aRunning={m1aRunning} m1cRunning={m1cRunning} />
      <CageControl selectAll={selectAll} clearAll={clearAll} isSelectedArray={isSelected} />
    </div>
  );
}

function RightColumn({ isSelected, setIsSelected, toggleSelected }) {
  return (
    <div
      className="columns-container"
      style={{ width: "76%", padding: "0px 0px", marginBottom: "0px", alignItems: "center" }}
    >
      <Cages row={rowNumber} isSelected={isSelected} setIsSelected={setIsSelected} toggleSelected={toggleSelected} />
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
