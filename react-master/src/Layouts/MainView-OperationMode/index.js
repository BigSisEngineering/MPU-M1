import React from "react";
import { useState, useEffect } from "react";
import { useDict, Dicts } from "../../Middleware/get-api.js";
import "../../Assets/Styles/styles.css";
import M1A from "../../Layouts/M1A/index.js";
import M1C from "../../Layouts/M1C/index.js";
import Cages from "../../Layouts/Cages/index.js";
import CageControl from "../../Layouts/CageControl/index.js";
import OperationControl from "../../Layouts/OperationControl/index.js";
import { DEFAULT_BOOL } from "../../Utils/Utils.js";

/* ====================================== Left ====================================== */
function OperationModeLeftColumn({
  rowNumber,
  isSelected,
  selectAll,
  clearAll,
  m1aRunning,
  m1cRunning,
  toggleMaintainence,
  isCageActionMode,
  setIsCageActionMode,
}) {
  return (
    <div className="columns-container" style={{ width: "22%" }}>
      <M1A row={rowNumber} m1aRunning={m1aRunning} />
      <M1C row={rowNumber} m1cRunning={m1cRunning} />
      <OperationControl m1aRunning={m1aRunning} m1cRunning={m1cRunning} />
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

/* ====================================== Right ===================================== */
function OperationModeRightColumn({
  rowNumber,
  isSelected,
  setIsSelected,
  toggleSelected,
  maintainenceFlag,
  isCageActionMode,
}) {
  return (
    <div
      className="columns-container"
      style={{ width: "76%", padding: "0px 0px", marginBottom: "0px", alignItems: "center" }}
    >
      <Cages
        row={rowNumber}
        isSelected={isSelected}
        setIsSelected={setIsSelected}
        toggleSelected={toggleSelected}
        maintainenceFlag={maintainenceFlag}
        isCageActionMode={isCageActionMode}
      />
    </div>
  );
}

/* ================================================================================== */
/*                                        Main                                        */
/* ================================================================================== */
function OperationModeContent({ rowNumber, isCageActionMode, setIsCageActionMode }) {
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

  // maintainence
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
      <OperationModeLeftColumn
        rowNumber={rowNumber}
        isSelected={isSelected}
        selectAll={selectAll}
        clearAll={clearAll}
        m1aRunning={m1aRunning}
        m1cRunning={m1cRunning}
        toggleMaintainence={toggleMaintainence}
        isCageActionMode={isCageActionMode}
        setIsCageActionMode={setIsCageActionMode}
      />
      <OperationModeRightColumn
        rowNumber={rowNumber}
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

export default OperationModeContent;
