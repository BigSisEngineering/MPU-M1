import React, { useState } from "react";
import "../Assets/Styles/styles.css";
import DebuggingM1A from "../Layouts/DebuggingM1A/index.js";
import M1C from "../Layouts/M1C/index.js";
import Cages from "../Layouts/Cages/index.js";

function LeftColumn() {
  return (
    <div className="columns-container" style={{ width: "50%" }}>
      <DebuggingM1A />
      <M1C />
    </div>
  );
}

function RightColumn({ isSelected, setIsSelected, toggleSelected, maintainenceFlag }) {
  return (
    <div
      className="columns-container"
      style={{ width: "76%", padding: "0px 0px", marginBottom: "0px", alignItems: "center" }}
    >
      <Cages
        isSelected={isSelected}
        setIsSelected={setIsSelected}
        toggleSelected={toggleSelected}
        maintainenceFlag={maintainenceFlag}
        isCageActionMode={false}
      />
    </div>
  );
}

function Debugging() {
  /* ================================ Dummy Cage Select =============================== */
  const [isSelected, setIsSelected] = useState(Array(14).fill(false));

  const toggleSelected = (index) => () => {
    setIsSelected((prevSelected) => {
      const newIsSelected = [...prevSelected];
      newIsSelected[index] = !newIsSelected[index];
      return newIsSelected;
    });
  };

  /* ================================== Maintainence ================================== */
  // ! not in use
  //   const [maintainenceFlag, setMaintainenceFlag] = useState(Array(14).fill(false));
  //   function toggleMaintainence(indexList, bool) {
  //     indexList.forEach(function (index) {
  //       setMaintainenceFlag((prevSelected) => {
  //         const newIsSelected = [...prevSelected];
  //         newIsSelected[index] = bool;
  //         return newIsSelected;
  //       });
  //     });
  //   }

  return (
    <div className="mains-container">
      <LeftColumn />
      <RightColumn
        isSelected={isSelected}
        setIsSelected={setIsSelected}
        toggleSelected={toggleSelected}
        maintainenceFlag={false}
      />
    </div>
  );
}

export default Debugging;
