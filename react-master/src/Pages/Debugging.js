import React, { useState } from "react";
import "../Assets/Styles/styles.css";
import DebuggingM1A from "../Layouts/DebuggingM1A/index.js";
import DebuggingM1C from "../Layouts/DebuggingM1C/index.js";
// import Cages from "../Layouts/Cages/index.js";

function LeftColumn() {
  return (
    <div className="columns-container" style={{ width: "50%" }}>
      <DebuggingM1A />
    </div>
  );
}

function RightColumn() {
  return (
    <div className="columns-container" style={{ width: "50%" }}>
      <DebuggingM1C />
    </div>
  );
}

function Debugging() {
  return (
    <div className="mains-container">
      <LeftColumn />
      <RightColumn />
    </div>
  );
}

export default Debugging;
