import React from "react";
import { useState } from "react";
import "./Assets/Styles/styles.css";
import Header from "./Layouts/Header/index.js";
import AlertBox from "./Layouts/AlertBox/index.js";
import M1A from "./Layouts/M1A/index.js";
import M1C from "./Layouts/M1C/index.js";
import Cages from "./Layouts/Cages/index.js";
import CageControl from "./Layouts/CageControl/index.js";
import OperationControl from "./Layouts/OperationControl/index.js";

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
    rowNumber = 5;
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

  /* ---------------------------------------------------------------------------------- */

  return (
    <div className="mains-container">
      <LeftColumn isSelected={isSelected} selectAll={selectAll} clearAll={clearAll} />
      <RightColumn isSelected={isSelected} setIsSelected={setIsSelected} toggleSelected={toggleSelected} />
    </div>
  );
}

function LeftColumn({ isSelected, selectAll, clearAll }) {
  return (
    <div className="columns-container" style={{ width: "22%" }}>
      <M1A />
      <M1C />
      <OperationControl />
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
