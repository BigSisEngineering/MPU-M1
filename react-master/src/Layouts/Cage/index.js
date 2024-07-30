import React from "react";
import { useState, useEffect } from "react";
import "../../Assets/Styles/styles.css";
import { useDict, Dicts } from "../../Middleware/get-api.js";
import { toggleDebugMode, getColor, DEFAULT_MSG, DEFAULT_BOOL, httpPOST, exec } from "../../Utils/Utils.js";
import {
  Info,
  Gap,
  HorizontalLine,
  Button,
  Subinfo,
  SubcontentTitle,
  InfoSameRow,
  DisplayImage,
  DisplayCustomEmoji,
  CustomEmoji,
} from "../../Components/index.js";

function Cage({ row = null, number = null, isSelected, toggleSelected }) {
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
      <div className={`subcontent-container ${isSelected ? "selected" : ""}`} onClick={toggleSelected}>
        <SubcontentTitle text={`Cage ${number}`} />
        <HorizontalLine />
        <DisplayImage link={`http://m3-${row}-g${number}2.local:8080/video_feed_1`} />
        <Gap />
        <HorizontalLine />
        <Info text="PNP" color={getColor("GREEN")} />
        <HorizontalLine />
        <div className="row-container" style={{ justifyContent: "left" }}>
          <Subinfo title={"SW"} content={"🟩"} />
          <Subinfo title={"UL"} content={"🟩"} />
        </div>
        <HorizontalLine />
        <div className="row-container" style={{ justifyContent: "left" }}>
          <Subinfo title={"Load"} content={"🟢"} />
          <Subinfo title={"Unload"} content={"🟢"} />
          <Subinfo title={"Buffer"} content={"🟢"} />
        </div>
        <HorizontalLine />
      </div>
    </>
  );
}

export default Cage;
