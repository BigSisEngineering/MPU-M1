import React from "react";
import { useState, useEffect } from "react";
import "../../Assets/Styles/styles.css";
import { useDict, Dicts } from "../../Middleware/get-api.js";
import { getColor, DEFAULT_MSG, DEFAULT_BOOL } from "../../Utils/Utils.js";
import {
  Info,
  Gap,
  HorizontalLine,
  Subinfo,
  SubcontentTitle,
  DisplayImage,
  DisplayCustomEmoji,
  CustomEmoji,
} from "../../Components/index.js";

function Cage({ row = null, number = null, isSelected, toggleSelected }) {
  const [unloaderStatus, setUnloaderStatus] = useState(DEFAULT_MSG);
  const [starwheelStatus, setStarwheelStatus] = useState(DEFAULT_MSG);
  //
  const [loadSensor, setLoadSensor] = useState(-1);
  const [unloadSensor, setUnloadSensor] = useState(-1);
  const [bufferSensor, setBufferSensor] = useState(-1);
  //
  const [mode, setMode] = useState(DEFAULT_MSG);
  //
  const [isLoaded, setIsLoaded] = useState(DEFAULT_BOOL);

  const cageHostname = `cage${row - 1}x00${number.toString().padStart(2, "0")}`;

  /* ---------------------------------------------------------------------------------- */
  // data update
  const dictData = useDict(Dicts.cages);

  useEffect(() => {
    if (dictData) {
      try {
        setUnloaderStatus(dictData[cageHostname]["unloader_status"]);
        setStarwheelStatus(dictData[cageHostname]["star_wheel_status"]);
        //
        const sensors = dictData[cageHostname]["sensors_values"].replace(/[()]/g, "").split(",").map(Number);
        setLoadSensor(sensors[0]);
        setUnloadSensor(sensors[1]);
        setBufferSensor(sensors[2]);
        setMode(dictData[cageHostname]["mode"]);
        setIsLoaded(true);
      } catch {
        setUnloaderStatus(DEFAULT_MSG);
        setStarwheelStatus(DEFAULT_MSG);
        setLoadSensor(-1);
        setUnloadSensor(-1);
        setBufferSensor(-1);
        setMode(DEFAULT_MSG);
        setIsLoaded(false);
      }
      //
    } else {
      setUnloaderStatus(DEFAULT_MSG);
      setStarwheelStatus(DEFAULT_MSG);
      setLoadSensor(-1);
      setUnloadSensor(-1);
      setBufferSensor(-1);
      setMode(DEFAULT_MSG);
      setIsLoaded(false);
    }
  }, [dictData, cageHostname]);

  /* ---------------------------------------------------------------------------------- */

  function modeText(modeState) {
    switch (modeState) {
      case "idle":
        return "IDLE";
      case "pnp":
        return "PNP";
      case "dummy":
        return "DUMMY";
      default:
        return DEFAULT_MSG;
    }
  }

  function modeColor(modeState) {
    switch (modeState) {
      case "idle":
        return getColor("YELLOW");
      case "pnp":
        return getColor("GREEN");
      case "dummy":
        return getColor("BLUE");
      default:
        return getColor("DEFAULT");
    }
  }

  function servoEmoji(servoStatus) {
    // "overload"
    // "error"
    // "timeout"
    // "normal"
    // "idle"
    // "not_init"

    // switch (servoStatus) {
    //   case "overload":
    //     return "🟥";
    //   case "error":
    //     return "🟧";
    //   case "timeout":
    //     return "🟨";
    //   case "normal":
    //     return "🟩";
    //   case "idle":
    //     return "🌫️";
    //   case "not_init":
    //     return "⬛";
    //   default:
    //     return DEFAULT_MSG;
    // }
    switch (servoStatus) {
      case "overload":
        return CustomEmoji.red_rectangle;
      case "error":
        return CustomEmoji.red_rectangle;
      case "timeout":
        return CustomEmoji.red_rectangle;
      case "normal":
        return CustomEmoji.green_rectangle;
      case "idle":
        return CustomEmoji.green_rectangle;
      case "not_init":
        return CustomEmoji.grey_rectangle;
      default:
        return CustomEmoji.black_rectangle;
    }
  }

  function sensorEmoji(sensorValue) {
    const highThresh = 100;

    // if (sensorValue > highThresh) {
    //   return "🟢";
    // } else if (sensorValue > 0) {
    //   return "⭕";
    // } else {
    //   return DEFAULT_MSG;
    // }
    if (sensorValue > highThresh) {
      return CustomEmoji.green_circle;
    } else if (sensorValue > 0) {
      return CustomEmoji.red_hollow_circle;
    } else {
      return CustomEmoji.black_circle;
    }
  }

  function getbackgroundColor() {
    if (isLoaded && (unloaderStatus !== "normal" || starwheelStatus !== "normal")) {
      if (!isSelected) {
        return ["rgba(255, 61, 0, 0.4)", "rgba(125, 125, 125, 0.32)"];
      } else {
        return ["rgba(255, 61, 0, 0.62)", "rgba(170, 253, 214, 0.3)"];
      }
    } else if (isLoaded && (loadSensor < 100 || bufferSensor < 100)) {
      if (!isSelected) {
        return ["rgba(255, 189, 0, 0.4)", "rgba(125, 125, 125, 0.32)"];
      } else {
        return ["rgba(253, 187, 0, 0.62)", "rgba(170, 253, 214, 0.3)"];
      }
    } else {
      if (!isSelected) {
        return ["rgba(125, 125, 125, 0.4)", "rgba(125, 125, 125, 0.32)"];
      } else {
        return ["rgba(170, 253, 214, 0.3)", "rgba(170, 253, 214, 0.3)"];
      }
    }
  }

  function getOpacity() {
    if (!isLoaded) {
      if (!isSelected) {
        return 25;
      }
      return 75;
    }
    return 100;
  }

  return (
    <>
      <div
        className={`subcontent-container ${isSelected ? "selected" : ""}`}
        onClick={toggleSelected}
        style={{
          background: `linear-gradient(to bottom, ${getbackgroundColor()[0]}, ${getbackgroundColor()[1]}`,
          opacity: `${getOpacity()}%`,
          cursor: "cell",
        }}
      >
        <SubcontentTitle text={`Cage ${number}`} link={`http://${cageHostname}.local:8080`} />
        <HorizontalLine />
        <DisplayImage link={`http://${cageHostname}.local:8080/video_feed`} />
        <Gap />
        <HorizontalLine />
        <Info text={modeText(mode)} color={modeColor(mode)} />
        <HorizontalLine />
        <div className="row-container" style={{ justifyContent: "left" }}>
          <Subinfo title={"SW"} content={<DisplayCustomEmoji emoji={servoEmoji(starwheelStatus)} />} />
          <Subinfo title={"UL"} content={<DisplayCustomEmoji emoji={servoEmoji(unloaderStatus)} />} />
        </div>
        <HorizontalLine />
        <div className="row-container" style={{ justifyContent: "left" }}>
          <Subinfo title={"Load"} content={<DisplayCustomEmoji emoji={sensorEmoji(loadSensor)} />} />
          <Subinfo title={"Unload"} content={<DisplayCustomEmoji emoji={sensorEmoji(unloadSensor)} />} />
          <Subinfo title={"Buffer"} content={<DisplayCustomEmoji emoji={sensorEmoji(bufferSensor)} />} />
        </div>
        <HorizontalLine />
      </div>
    </>
  );
}

export default Cage;
