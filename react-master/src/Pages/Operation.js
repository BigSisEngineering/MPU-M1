import React, { useState } from "react";
import "../Assets/Styles/styles.css";
import M1A from "../Layouts/M1A/index.js";
import M1C from "../Layouts/M1C/index.js";
import Cages from "../Layouts/Cages/index.js";
import CageControl from "../Layouts/CageControl/index.js";
import OperationControl from "../Layouts/OperationControl/index.js";

function LeftColumn({ isSelected, selectAll, clearAll, toggleMaintainence, isCageActionMode, setIsCageActionMode }) {
  return (
    <div className="columns-container" style={{ width: "22%" }}>
      <M1A />
      <M1C />
      <OperationControl />
      <CageControl
        selectAll={selectAll}
        clearAll={clearAll}
        isSelectedArray={isSelected}
        toggleMaintainence={toggleMaintainence}
        isCageActionMode={isCageActionMode}
        setIsCageActionMode={setIsCageActionMode}
      />
    </div>
  );
}

function RightColumn({ isSelected, setIsSelected, toggleSelected, maintainenceFlag, isCageActionMode }) {
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
        isCageActionMode={isCageActionMode}
      />
    </div>
  );
}

function Operation() {
  /* =================================== Cage Select ================================== */
  const [isSelected, setIsSelected] = useState(Array(14).fill(false));
  const [isCageActionMode, setIsCageActionMode] = useState(true);

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

  /* ================================== Maintainence ================================== */
  // ! not in use
  const [maintainenceFlag, setMaintainenceFlag] = useState(Array(14).fill(false));
  function toggleMaintainence(indexList, bool) {
    indexList.forEach(function (index) {
      setMaintainenceFlag((prevSelected) => {
        const newIsSelected = [...prevSelected];
        newIsSelected[index] = bool;
        return newIsSelected;
      });
    });
  }

  return (
    <div className="mains-container">
      <LeftColumn
        isSelected={isSelected}
        selectAll={selectAll}
        clearAll={clearAll}
        toggleMaintainence={toggleMaintainence}
        isCageActionMode={isCageActionMode}
        setIsCageActionMode={setIsCageActionMode}
      />
      <RightColumn
        isSelected={isSelected}
        setIsSelected={setIsSelected}
        toggleSelected={toggleSelected}
        maintainenceFlag={maintainenceFlag}
        isCageActionMode={isCageActionMode}
        setIsCageActionMode={setIsCageActionMode}
      />
    </div>
  );
}

export default Operation;
