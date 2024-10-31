import { createContext, useContext, useState, useEffect } from "react";
// import { fetchJSON } from "../Utils/Utils.js";
import io from "socket.io-client";

const socket = io();
socket.on("connect", function () {});
socket.on("disconnect", function () {});

/* ---------------------------------------------------------------------------------- */
class Dicts {
  static m1a = 1;
  static m1c = 2;
  static cages = 3;
  static system = 4;
  static info = 5;
  static session = 6;
  static lastping = 7;
}

const dictsContext = createContext({
  [Dicts.m1a]: null,
  [Dicts.m1c]: null,
  [Dicts.cages]: null,
  [Dicts.system]: null,
  [Dicts.info]: null,
  [Dicts.session]: null,
  [Dicts.lastping]: null,
});

const ContentProvider = ({ children }) => {
  const [dictValues, setDictValues] = useState({
    [Dicts.m1a]: null,
    [Dicts.m1c]: null,
    [Dicts.cages]: null,
    [Dicts.system]: null,
    [Dicts.info]: null,
    [Dicts.session]: null,
    [Dicts.lastping]: null,
  });

  useEffect(() => {
    // Socket event listeners
    const handleM1A = (data) => {
      setDictValues((prev) => ({ ...prev, [Dicts.m1a]: data }));
    };

    const handleM1C = (data) => {
      setDictValues((prev) => ({ ...prev, [Dicts.m1c]: data }));
    };

    const handleCages = (data) => {
      setDictValues((prev) => ({ ...prev, [Dicts.cages]: data }));
    };

    const handleSystem = (data) => {
      setDictValues((prev) => ({ ...prev, [Dicts.system]: data }));
    };

    const handleInfo = (data) => {
      setDictValues((prev) => ({ ...prev, [Dicts.info]: data }));
    };

    const handleSession = (data) => {
      updateLastPing();
      setDictValues((prev) => ({ ...prev, [Dicts.session]: data }));
    };

    function updateLastPing() {
      const lastPing = Math.floor(Date.now() / 1000);
      setDictValues((prev) => ({ ...prev, [Dicts.lastping]: { time: lastPing } }));
    }

    // Register socket event listeners
    socket.on("m1a", handleM1A);
    socket.on("m1c", handleM1C);
    socket.on("cages", handleCages);
    socket.on("system", handleSystem);
    socket.on("info", handleInfo);
    socket.on("session", handleSession);

    // Cleanup function to remove the event listeners
    return () => {
      socket.off("m1a", handleM1A);
      socket.off("m1c", handleM1C);
      socket.off("cages", handleCages);
      socket.off("system", handleSystem);
      socket.off("info", handleInfo);
      socket.off("session", handleSession);
    };
  }, []); // Empty dependency array to run only once on mount

  return <dictsContext.Provider value={{ dictValues, setDictValues }}>{children}</dictsContext.Provider>;
};

// Custom hook for easy access to context
const useDict = (dict) => {
  const context = useContext(dictsContext); // Get the entire context

  if (!context) {
    throw new Error("useDict must be used within a ContentProvider");
  }

  return context.dictValues[dict]; // Return the specific value for the provided key
};

export { ContentProvider, useDict, Dicts };
