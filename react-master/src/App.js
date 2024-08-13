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
      return `❓ NOT FOUND`;
  }
}

async function getSetupInfo() {
  let infoDict = null;
  let moduleNumber;
  let rowNumber;

  try {
    const response = await fetch("/get_status/info", {
      method: "GET",
    });

    if (!response.ok) {
      throw new Error("Network response was not ok");
    }

    infoDict = await response.json();
  } catch (error) {
    console.error(error);
  }

  if (infoDict) {
    moduleNumber = infoDict["module"];
    rowNumber = infoDict["row"];
  } else {
    // moduleNumber = 1;
    // rowNumber = 6;
    moduleNumber = null;
    rowNumber = null;
  }

  return { moduleNumber, rowNumber };
}

/* ================================================================================== */
/*                                     Main Blocks                                    */
/* ================================================================================== */
function MainContent({ rowNumber }) {
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
        rowNumber={rowNumber}
        isSelected={isSelected}
        selectAll={selectAll}
        clearAll={clearAll}
        m1aRunning={m1aRunning}
        m1cRunning={m1cRunning}
      />
      <RightColumn
        rowNumber={rowNumber}
        isSelected={isSelected}
        setIsSelected={setIsSelected}
        toggleSelected={toggleSelected}
      />
    </div>
  );
}

function LeftColumn({ rowNumber, isSelected, selectAll, clearAll, m1aRunning, m1cRunning }) {
  return (
    <div className="columns-container" style={{ width: "22%" }}>
      <M1A row={rowNumber} m1aRunning={m1aRunning} />
      <M1C row={rowNumber} m1cRunning={m1cRunning} />
      <OperationControl m1aRunning={m1aRunning} m1cRunning={m1cRunning} />
      <CageControl selectAll={selectAll} clearAll={clearAll} isSelectedArray={isSelected} />
    </div>
  );
}

function RightColumn({ rowNumber, isSelected, setIsSelected, toggleSelected }) {
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
  const [moduleNumber, setModuleNumber] = useState(null);
  const [rowNumber, setRowNumber] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isError, setIsError] = useState(false);

  useEffect(() => {
    async function fetchData() {
      const result = await getSetupInfo();
      setModuleNumber(result.moduleNumber);
      setRowNumber(result.rowNumber);
      document.title = generateDocumentTitle(result.moduleNumber, result.rowNumber);
      setIsLoading(false);
      result.rowNumber ? setIsError(false) : setIsError(true);
    }

    fetchData();

    const intervalId = setInterval(fetchData, 10000);

    return () => clearInterval(intervalId);
  }, [setIsError]);

  if (isLoading) {
    return <div className="full-display">Page loading...</div>;
  }

  if (isError) {
    return <div className="full-display">Connection lost. Reboot if refreshing does not work.</div>;
  }

  return (
    <>
      <AlertBox />
      <Header module={moduleNumber} unit={"Master"} row={rowNumber} />
      <MainContent rowNumber={rowNumber} />
    </>
  );
}
