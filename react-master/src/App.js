import React from "react";
import { useState, useEffect } from "react";
import { ContentProvider, useDict, Dicts } from "./Middleware/get-api.js";
import "./Assets/Styles/styles.css";
import Header from "./Layouts/Header/index.js";
import AlertBox from "./Layouts/AlertBox/index.js";
import DisplayModeContent from "./Layouts/MainView-DisplayMode/index.js";
import OperationModeContent from "./Layouts/MainView-OperationMode/index.js";

// DEBUG FLAG
// let DEBUG = true;
let DEBUG = false;

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

function Main() {
  const [moduleNumber, setModuleNumber] = useState(null);
  const [rowNumber, setRowNumber] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isError, setIsError] = useState(false);
  const [isTimeout, setIsTimeout] = useState(false);
  const [isDisplayOnly, setIsDisplayOnly] = useState(false);
  const [isCageActionMode, setIsCageActionMode] = useState(true);

  const dictInfo = useDict(Dicts.info);
  const dictSession = useDict(Dicts.session);
  const dictLastPing = useDict(Dicts.lastping);
  const dictExperiment = useDict(Dicts.experiment);

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

  if (isDisplayOnly) {
    return (
      <>
        <AlertBox />
        <Header
          module={moduleNumber}
          unit={"Master (Display Mode)"}
          row={rowNumber}
          isDisplayOnly={isDisplayOnly}
          setIsDisplayOnly={setIsDisplayOnly}
        />
        <DisplayModeContent
          rowNumber={rowNumber}
          dictExperiment={dictExperiment}
          isCageActionMode={isCageActionMode}
          setIsCageActionMode={setIsCageActionMode}
        />
      </>
    );
  }

  return (
    <>
      <AlertBox />
      <Header
        module={moduleNumber}
        unit={"Master (Operation Mode)"}
        row={rowNumber}
        isDisplayOnly={isDisplayOnly}
        setIsDisplayOnly={setIsDisplayOnly}
      />
      <OperationModeContent
        rowNumber={rowNumber}
        isCageActionMode={isCageActionMode}
        setIsCageActionMode={setIsCageActionMode}
      />
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
