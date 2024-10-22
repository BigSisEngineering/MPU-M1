import React from "react";
import { useState, useEffect } from "react";
import { ContentProvider, useDict, Dicts } from "./Middleware/get-api.js";
import "./Assets/Styles/styles.css";
import Header from "./Layouts/Header/index.js";
import AlertBox from "./Layouts/AlertBox/index.js";
import M1A from "./Layouts/M1A/index.js";
import M1C from "./Layouts/M1C/index.js";
import Cages from "./Layouts/Cages/index.js";
import CageControl from "./Layouts/CageControl/index.js";
import OperationControl from "./Layouts/OperationControl/index.js";
import { DEFAULT_BOOL } from "./Utils/Utils.js";

// DEBUG FLAG
let DEBUG = false;

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
      <LeftColumn
        rowNumber={rowNumber}
        isSelected={isSelected}
        selectAll={selectAll}
        clearAll={clearAll}
        m1aRunning={m1aRunning}
        m1cRunning={m1cRunning}
        toggleMaintainence={toggleMaintainence}
      />
      <RightColumn
        rowNumber={rowNumber}
        isSelected={isSelected}
        setIsSelected={setIsSelected}
        toggleSelected={toggleSelected}
        maintainenceFlag={maintainenceFlag}
      />
    </div>
  );
}

function LeftColumn({ rowNumber, isSelected, selectAll, clearAll, m1aRunning, m1cRunning, toggleMaintainence }) {
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
      />
    </div>
  );
}

function RightColumn({ rowNumber, isSelected, setIsSelected, toggleSelected, maintainenceFlag }) {
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
      />
    </div>
  );
}

function Main() {
  const [moduleNumber, setModuleNumber] = useState(null);
  const [rowNumber, setRowNumber] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isError, setIsError] = useState(false);
  const [isTimeout, setIsTimeout] = useState(false);

  const dictInfo = useDict(Dicts.info);
  const dictSession = useDict(Dicts.session);
  const dictLastPing = useDict(Dicts.lastping);

  useEffect(() => {
    async function isLoaded() {
      if (dictInfo != null) {
        setModuleNumber(dictInfo.module);
        setRowNumber(dictInfo.row);
        document.title = generateDocumentTitle(dictInfo.module, dictInfo.row);
        setIsLoading(false);
      } else {
        setIsLoading(true);
      }
    }

    async function isError() {
      if (dictLastPing) {
        const timeStamp = Math.floor(Date.now() / 1000);
        timeStamp - dictLastPing.time > 10 ? setIsError(true) : setIsError(false);
      } else {
        setIsError(true);
      }
    }

    async function isTimeout() {
      if (dictSession) dictSession.session_timeout ? setIsTimeout(true) : setIsTimeout(false);
    }

    isLoaded();
    isTimeout();
    const intervalId = setInterval(isError, 1000);

    return () => clearInterval(intervalId);
  }, [setIsLoading, setIsError, setIsTimeout, dictInfo, dictSession, dictLastPing]);

  if (!DEBUG) {
    if (isTimeout) {
      return <div className="full-display">Too many sessions! You have been timedout.</div>;
    } else if (isError) {
      return <div className="full-display">Connection lost. Reboot if refreshing does not work.</div>;
    } else if (isLoading) {
      return <div className="full-display">Page loading...</div>;
    }
  }

  return (
    <>
      <AlertBox />
      <Header module={moduleNumber} unit={"Master"} row={rowNumber} />
      <MainContent rowNumber={rowNumber} />
    </>
  );
}

export default function Webapp() {
  return (
    <>
      <ContentProvider>
        <Main />
      </ContentProvider>
    </>
  );
}
