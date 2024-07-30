import React from "react";
import { useState, useEffect } from "react";
import "../../Assets/Styles/styles.css";
import Cage from "../Cage/index.js";
import CageControl from "../CageControl/index.js";
import { useDict, Dicts } from "../../Middleware/get-api.js";
import { toggleDebugMode, getColor, DEFAULT_MSG, DEFAULT_BOOL, httpPOST, exec } from "../../Utils/Utils.js";
import { Gap } from "../../Components/index.js";

function Cages({ row }) {
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

  /* ---------------------------------------------------------------------------------- */
  const [mode, setMode] = useState(DEFAULT_MSG);
  const [debug, setDebug] = useState(DEFAULT_BOOL);

  // data update
  const dictData = useDict(Dicts.system);

  useEffect(() => {
    if (dictData) {
      setMode(dictData["system_state"]);
      setDebug(dictData["debug_mode"]);
    } else {
      setMode(DEFAULT_MSG);
      setDebug(DEFAULT_BOOL);
    }
    toggleDebugMode(debug);
  }, [debug, dictData]);

  /* ---------------------------------------------------------------------------------- */

  function modeText(modeState, debugState) {
    if (debugState) {
      return "DEBUG MODE";
    } else {
      if (modeState.includes("NORMAL")) {
        return "RUNNING";
      } else if (modeState.includes("IDLE")) {
        return "IDLE";
      } else if (modeState.includes("ERROR")) {
        return "IDLE";
      } else {
        return "⏳";
      }
    }
  }

  function modeColor(modeState, debugState) {
    if (debugState) {
      return getColor("YELLOW");
    } else {
      if (modeState.includes("NORMAL")) {
        return getColor("GREEN");
      } else {
        return getColor("DEFAULT_COLOR");
      }
    }
  }

  function systemStatusColor(modeState) {
    if (modeState.includes("NORMAL")) {
      return getColor("GREEN");
    } else if (modeState.includes("IDLE")) {
      return getColor("YELLOW");
    } else if (modeState.includes("ERROR")) {
      return getColor("RED");
    } else {
      return getColor("DEFAULT_COLOR");
    }
  }

  return (
    <>
      <Gap height={50} />
      <div className="row-container">
        {Array.from({ length: 7 }, (_, i) => (
          <div className="columns-container">
            <Cage
              key={i}
              row={row}
              number={i + 1}
              isSelected={isSelected[i]}
              toggleSelected={toggleSelected(i)}
              getColor={getColor}
            />
          </div>
        ))}
      </div>
      <div className="row-container" style={{ padding: "0px 0px" }}>
        {Array.from({ length: 7 }, (_, i) => (
          <div className="columns-container">
            <Cage
              key={i + 7}
              row={row}
              number={i + 8}
              isSelected={isSelected[i + 7]}
              toggleSelected={toggleSelected(i + 7)}
              getColor={getColor}
            />
          </div>
        ))}
      </div>
      <CageControl selectAll={selectAll} clearAll={clearAll} />
    </>
  );
}

export default Cages;
