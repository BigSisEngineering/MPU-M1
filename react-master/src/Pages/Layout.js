import { Outlet, NavLink } from "react-router-dom";
import { useState, useEffect } from "react";
import { useDict, Dicts } from "../Middleware/get-api.js";
import Header from "../Layouts/Header/index.js";
import faviconImg from "../Assets/Media/favicon.ico";
import Favicon from "react-favicon";

// DEBUG FLAG
// let DEBUG = false;
let DEBUG = true;

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

function Layout() {
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
      <Favicon url={faviconImg} />
      <Header module={moduleNumber} unit={"Master"} row={rowNumber} />{" "}
      <nav className="nav">
        <ul>
          <li>
            <NavLink to="/" className="link">
              Operation
            </NavLink>
          </li>
          <li>
            <NavLink to="/Display" className="link">
              Display
            </NavLink>
          </li>
        </ul>
      </nav>
      <Outlet />
    </>
  );
}

export default Layout;
