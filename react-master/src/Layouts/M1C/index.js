import React from "react";
import { useState, useEffect } from "react";
import "../../Assets/Styles/styles.css";
import { useDict, Dicts } from "../../Middleware/get-api.js";
import { toggleDebugMode, getColor, DEFAULT_MSG, DEFAULT_BOOL, httpPOST, exec } from "../../Utils/Utils.js";
import { Info, Gap, HorizontalLine, Button, SubcontentTitle, InfoSameRow } from "../../Components/index.js";

function M1C() {
  const [mode, setMode] = useState(DEFAULT_MSG);
  const [debug, setDebug] = useState(DEFAULT_BOOL);

  /* ---------------------------------------------------------------------------------- */
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
      <div
        className="subcontent-container"
        style={{
          fontSize: "16px",
          letterSpacing: "0.05em",
        }}
      >
        <SubcontentTitle text={"Chimney Sorter"} />
        <HorizontalLine />
        <InfoSameRow title="ⓘ Status" text="NORMAL" color={getColor("GREEN")} />
        <Gap height="20" />
        <SubcontentTitle text={"Chimney Capper"} />
        <HorizontalLine />
        <InfoSameRow title="ⓘ Status" text="NORMAL" color={getColor("GREEN")} />
      </div>
    </>
  );
}

export default M1C;
