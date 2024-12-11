import React, { useState } from "react";
import "../Assets/Styles/styles.css";
import M1A from "../Layouts/M1A/index.js";
import M1C from "../Layouts/M1C/index.js";
import Cages from "../Layouts/Cages/index.js";
import CageStatusBar from "../Layouts/CageStatusBar/index.js";

function DisplayModeLeftColumn() {
  return (
    <div className="columns-container" style={{ width: "22%" }}>
      <M1A displayButtons={false} />
      <M1C />
      <CageStatusBar />
    </div>
  );
}

function DisplayModeRightColumn({ isSelected, setIsSelected, toggleSelected, maintainenceFlag }) {
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

function Display() {
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
      <DisplayModeLeftColumn />
      <DisplayModeRightColumn
        isSelected={isSelected}
        setIsSelected={setIsSelected}
        toggleSelected={toggleSelected}
        maintainenceFlag={false}
      />
    </div>
  );
}

export default Display;
