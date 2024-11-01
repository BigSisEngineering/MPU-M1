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

class StatusCode {
  static SW_INITIALIZING = 0;
  static PRIMING_CHANNELS = 1;
  static UL_INITIALIZING = 2;
  static IDLE = 3;
  static ERROR_SW = 4;
  static ERROR_UL = 5;
  static CLEARING_SERVO_ERROR = 6;
  static UNABLE_TO_CLEAR_ERROR = 7;
  static ERROR_CAMERA = 8;
  static NORMAL = 9;
  static LOADING = 10;
  static WAIT_ACK = 11;
  static SELF_FIX_PENDING = 12;
  static WAITING_FOR_BUFFER = 13;
  static WAITING_FOR_PASSIVE_LOAD = 14;
  static INIT_WAITING_FOR_BUFFER = 15;
  static INIT_WAITING_FOR_PASSIVE_LOAD = 16;
}

function Cage({ row = null, number = null, isSelected, toggleSelected, isCageActionMode }) {
  const [unloaderStatus, setUnloaderStatus] = useState(DEFAULT_MSG);
  const [starwheelStatus, setStarwheelStatus] = useState(DEFAULT_MSG);
  const [maintainenceFlag, setMaintainenceFlag] = useState(DEFAULT_BOOL);
  const [statusCode, setStatusCode] = useState(-1);
  //
  const [loadSensor, setLoadSensor] = useState(-1);
  const [unloadSensor, setUnloadSensor] = useState(-1);
  const [bufferSensor, setBufferSensor] = useState(-1);
  //
  const [mode, setMode] = useState(DEFAULT_MSG);
  //
  const [isLoaded, setIsLoaded] = useState(DEFAULT_BOOL);

  const cageHostname = `cage${row - 1}x00${number.toString().padStart(2, "0")}`;

  /* ================================================================================== */
  /*                                     Board Data                                     */
  /* ================================================================================== */
  // data update
  const dictData = useDict(Dicts.cages);

  useEffect(() => {
    if (dictData) {
      try {
        setUnloaderStatus(dictData[cageHostname]["unloader_status"]);
        setStarwheelStatus(dictData[cageHostname]["star_wheel_status"]);
        setStatusCode(parseInt(dictData[cageHostname]["status_code"]));
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
        setStatusCode(-1);
        setLoadSensor(-1);
        setUnloadSensor(-1);
        setBufferSensor(-1);
        setMode(DEFAULT_MSG);
        setIsLoaded(false);
      }
      //
      setMaintainenceFlag(dictData[cageHostname]["maintainence_flag"]);
    } else {
      setUnloaderStatus(DEFAULT_MSG);
      setStarwheelStatus(DEFAULT_MSG);
      setStatusCode(-1);
      setLoadSensor(-1);
      setUnloadSensor(-1);
      setBufferSensor(-1);
      setMode(DEFAULT_MSG);
      setIsLoaded(false);
    }
  }, [dictData, cageHostname]);

  /* ================================================================================== */
  /*                                   Experiment Dict                                  */
  /* ================================================================================== */
  // function getOperationMode(operationIndex) {
  //   switch (operationIndex) {
  //     case 0:
  //       return "Ai";
  //     case 1:
  //       return "Ai";
  //     case 2:
  //       return "Ai";
  //     case 3:
  //       return "Ai";
  //     case 4:
  //       return "Purge";
  //     default:
  //       return "n/a";
  //   }
  // }

  const dictExperiment = useDict(Dicts.experiment);

  // Read dict
  let sequenceNumber = null;
  let slots = null;
  let maxSlots = null;
  let timeElapsed = null;
  let timeInterval = null;

  if (dictExperiment) {
    sequenceNumber = dictExperiment[cageHostname]["sequence_number"];
    slots = dictExperiment[cageHostname]["slots"];
    maxSlots = dictExperiment[cageHostname]["max_slots"];
    timeElapsed = dictExperiment[cageHostname]["time_elapsed"];
    timeInterval = dictExperiment[cageHostname]["sequence_duration"];
  }

  const slotBarWidth = maxSlots ? (slots / maxSlots) * 100 : 0;
  const isUnderFourMinutes = timeElapsed ? (timeElapsed <= 4 * 60 ? true : false) : false; // temp hard code
  const isNotComplete = slots ? (slots !== 80 ? true : false) : false;
  // const currentMode = getOperationMode(operationIndex); // ignore first

  /* ---------------------------------------------------------------------------------- */

  function resolveStatusCodeOperatorAction() {
    switch (statusCode) {
      case StatusCode.SW_INITIALIZING:
        return "-";
      case StatusCode.PRIMING_CHANNELS:
        return "-";
      case StatusCode.UL_INITIALIZING:
        return "-";
      case StatusCode.IDLE:
        return "-";
      case StatusCode.ERROR_SW:
        return "SW Error! 'Servo init' to clear.";
      case StatusCode.ERROR_UL:
        return "UL Error! 'Servo init' to clear.";
      case StatusCode.CLEARING_SERVO_ERROR:
        return "-";
      case StatusCode.UNABLE_TO_CLEAR_ERROR:
        return "Arduino Error";
      case StatusCode.ERROR_CAMERA:
        return "Camera Error";
      case StatusCode.NORMAL:
        return "-";
      case StatusCode.LOADING:
        return "-";
      case StatusCode.WAIT_ACK:
        return "Frequent Errors! 'Servo init' to clear.";
      case StatusCode.SELF_FIX_PENDING:
        return "-";
      case StatusCode.WAITING_FOR_BUFFER:
        return "Check infeed. 'Add pots'?";
      case StatusCode.WAITING_FOR_PASSIVE_LOAD:
        return "Poke me!";
      case StatusCode.INIT_WAITING_FOR_BUFFER:
        return "Check infeed. 'Add pots'?";
      case StatusCode.INIT_WAITING_FOR_PASSIVE_LOAD:
        return "Poke me!";
      default:
        return "Offline";
    }
  }

  function modeText(modeState) {
    if (maintainenceFlag) return "FIX ME";

    switch (modeState) {
      case "idle":
        return "IDLE";
      case "pnp":
        return "PNP";
      case "dummy":
        return "DUMMY";
      case "experiment":
        return "EXPERIMENT";
      default:
        return DEFAULT_MSG;
    }
  }

  function modeColor(modeState) {
    if (maintainenceFlag) return getColor("RED");

    switch (modeState) {
      case "idle":
        return getColor("DEFAULT");
      case "pnp":
        return getColor("GREEN");
      case "dummy":
        return getColor("BLUE");
      case "experiment":
        return getColor("ORANGE");
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
    if (sensorValue > highThresh) {
      return CustomEmoji.green_circle;
    } else if (sensorValue > 0) {
      return CustomEmoji.red_hollow_circle;
    } else {
      return CustomEmoji.black_circle;
    }
  }

  function getbackgroundColor() {
    if (maintainenceFlag) return ["rgba(255, 61, 0, 0.8)", "rgba(255, 61, 0, 0.4)"];

    if (!isCageActionMode) {
      if (isLoaded && (unloaderStatus !== "normal" || starwheelStatus !== "normal")) {
        /*************** RED ****************/
        if (!isSelected) {
          return ["rgba(255, 61, 0, 0.4)", "rgba(125, 125, 125, 0.32)"];
        } else {
          return ["rgba(255, 61, 0, 0.62)", "rgba(170, 253, 214, 0.3)"];
        }
      } else if (isLoaded && (loadSensor < 100 || bufferSensor < 100)) {
        /************* YELLOW ***************/
        if (!isSelected) {
          return ["rgba(255, 189, 0, 0.4)", "rgba(125, 125, 125, 0.32)"];
        } else {
          return ["rgba(253, 187, 0, 0.62)", "rgba(170, 253, 214, 0.3)"];
        }
      } else {
        /*************** GREY ***************/
        if (!isSelected) {
          return ["rgba(125, 125, 125, 0.4)", "rgba(125, 125, 125, 0.32)"];
        } else {
          return ["rgba(170, 253, 214, 0.3)", "rgba(170, 253, 214, 0.3)"];
        }
      }
    } else {
      switch (statusCode) {
        case StatusCode.SW_INITIALIZING:
          if (!isSelected) {
            return ["rgba(125, 125, 125, 0.4)", "rgba(125, 125, 125, 0.32)"];
          } else {
            return ["rgba(170, 253, 214, 0.3)", "rgba(170, 253, 214, 0.3)"];
          }
        case StatusCode.PRIMING_CHANNELS:
          if (!isSelected) {
            return ["rgba(125, 125, 125, 0.4)", "rgba(125, 125, 125, 0.32)"];
          } else {
            return ["rgba(170, 253, 214, 0.3)", "rgba(170, 253, 214, 0.3)"];
          }
        case StatusCode.UL_INITIALIZING:
          if (!isSelected) {
            return ["rgba(125, 125, 125, 0.4)", "rgba(125, 125, 125, 0.32)"];
          } else {
            return ["rgba(170, 253, 214, 0.3)", "rgba(170, 253, 214, 0.3)"];
          }
        case StatusCode.IDLE:
          if (!isSelected) {
            return ["rgba(125, 125, 125, 0.4)", "rgba(125, 125, 125, 0.32)"];
          } else {
            return ["rgba(170, 253, 214, 0.3)", "rgba(170, 253, 214, 0.3)"];
          }
        case StatusCode.ERROR_SW:
          if (!isSelected) {
            return ["rgba(255, 61, 0, 0.4)", "rgba(125, 125, 125, 0.32)"];
          } else {
            return ["rgba(255, 61, 0, 0.62)", "rgba(170, 253, 214, 0.3)"];
          }
        case StatusCode.ERROR_UL:
          if (!isSelected) {
            return ["rgba(255, 61, 0, 0.4)", "rgba(125, 125, 125, 0.32)"];
          } else {
            return ["rgba(255, 61, 0, 0.62)", "rgba(170, 253, 214, 0.3)"];
          }
        case StatusCode.CLEARING_SERVO_ERROR:
          if (!isSelected) {
            return ["rgba(125, 125, 125, 0.4)", "rgba(125, 125, 125, 0.32)"];
          } else {
            return ["rgba(170, 253, 214, 0.3)", "rgba(170, 253, 214, 0.3)"];
          }
        case StatusCode.UNABLE_TO_CLEAR_ERROR:
          if (!isSelected) {
            return ["rgba(255, 61, 0, 0.4)", "rgba(125, 125, 125, 0.32)"];
          } else {
            return ["rgba(255, 61, 0, 0.62)", "rgba(170, 253, 214, 0.3)"];
          }
        case StatusCode.ERROR_CAMERA:
          if (!isSelected) {
            return ["rgba(255, 61, 0, 0.4)", "rgba(125, 125, 125, 0.32)"];
          } else {
            return ["rgba(255, 61, 0, 0.62)", "rgba(170, 253, 214, 0.3)"];
          }
        case StatusCode.NORMAL:
          if (!isSelected) {
            return ["rgba(125, 125, 125, 0.4)", "rgba(125, 125, 125, 0.32)"];
          } else {
            return ["rgba(170, 253, 214, 0.3)", "rgba(170, 253, 214, 0.3)"];
          }
        case StatusCode.LOADING:
          if (!isSelected) {
            return ["rgba(125, 125, 125, 0.4)", "rgba(125, 125, 125, 0.32)"];
          } else {
            return ["rgba(170, 253, 214, 0.3)", "rgba(170, 253, 214, 0.3)"];
          }
        case StatusCode.WAIT_ACK:
          if (!isSelected) {
            return ["rgba(255, 61, 0, 0.4)", "rgba(125, 125, 125, 0.32)"];
          } else {
            return ["rgba(255, 61, 0, 0.62)", "rgba(170, 253, 214, 0.3)"];
          }
        case StatusCode.SELF_FIX_PENDING:
          if (!isSelected) {
            return ["rgba(125, 125, 125, 0.4)", "rgba(125, 125, 125, 0.32)"];
          } else {
            return ["rgba(170, 253, 214, 0.3)", "rgba(170, 253, 214, 0.3)"];
          }
        case StatusCode.WAITING_FOR_BUFFER:
          if (!isSelected) {
            return ["rgba(255, 189, 0, 0.4)", "rgba(125, 125, 125, 0.32)"];
          } else {
            return ["rgba(253, 187, 0, 0.62)", "rgba(170, 253, 214, 0.3)"];
          }
        case StatusCode.WAITING_FOR_PASSIVE_LOAD:
          if (!isSelected) {
            return ["rgba(255, 189, 0, 0.4)", "rgba(125, 125, 125, 0.32)"];
          } else {
            return ["rgba(253, 187, 0, 0.62)", "rgba(170, 253, 214, 0.3)"];
          }
        case StatusCode.INIT_WAITING_FOR_BUFFER:
          if (!isSelected) {
            return ["rgba(255, 189, 0, 0.4)", "rgba(125, 125, 125, 0.32)"];
          } else {
            return ["rgba(253, 187, 0, 0.62)", "rgba(170, 253, 214, 0.3)"];
          }
        case StatusCode.INIT_WAITING_FOR_PASSIVE_LOAD:
          if (!isSelected) {
            return ["rgba(255, 189, 0, 0.4)", "rgba(125, 125, 125, 0.32)"];
          } else {
            return ["rgba(253, 187, 0, 0.62)", "rgba(170, 253, 214, 0.3)"];
          }
        default:
          if (!isSelected) {
            return ["rgba(125, 125, 125, 0.4)", "rgba(125, 125, 125, 0.32)"];
          } else {
            return ["rgba(170, 253, 214, 0.3)", "rgba(170, 253, 214, 0.3)"];
          }
      }
    }
  }

  function resolveStatusCodeOpacity() {
    // if slots not complete, return 'error' opacity anyways
    if (isNotComplete) return 50;

    switch (statusCode) {
      case StatusCode.SW_INITIALIZING:
        return 10;
      case StatusCode.PRIMING_CHANNELS:
        return 10;
      case StatusCode.UL_INITIALIZING:
        return 10;
      case StatusCode.IDLE:
        return 10;
      case StatusCode.ERROR_SW:
        return 50;
      case StatusCode.ERROR_UL:
        return 50;
      case StatusCode.CLEARING_SERVO_ERROR:
        return 10;
      case StatusCode.UNABLE_TO_CLEAR_ERROR:
        return 50;
      case StatusCode.ERROR_CAMERA:
        return 50;
      case StatusCode.NORMAL:
        return 10;
      case StatusCode.LOADING:
        return 10;
      case StatusCode.WAIT_ACK:
        return 50;
      case StatusCode.SELF_FIX_PENDING:
        return 10;
      case StatusCode.WAITING_FOR_BUFFER:
        return 50;
      case StatusCode.WAITING_FOR_PASSIVE_LOAD:
        return 50;
      case StatusCode.INIT_WAITING_FOR_BUFFER:
        return 50;
      case StatusCode.INIT_WAITING_FOR_PASSIVE_LOAD:
        return 50;
      default:
        return 10;
    }
  }

  function getOpacity() {
    // If under maintainence
    if (maintainenceFlag) {
      if (!isSelected) {
        return 50;
      }
      return 75;
    }

    // If cage is offline
    if (!isLoaded) {
      if (!isSelected) {
        return 10;
      }
      return 75;
    }

    // Full opacity if under 4 minutes (focused cages)
    if (isUnderFourMinutes && mode == "experiment") {
      return 100;
    }
    if (!isSelected) {
      return resolveStatusCodeOpacity();
    }
    return 75;
  }

  return (
    <>
      <div
        className={`subcontent-container ${
          isSelected ? "selected" : isUnderFourMinutes && mode == "experiment" ? "highlighted" : ""
        }`}
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
        {!isCageActionMode && (
          <>
            <div className="row-container" style={{ justifyContent: "left" }}>
              <Subinfo title={"SW"} content={<DisplayCustomEmoji emoji={servoEmoji(starwheelStatus)} />} />
              <Subinfo title={"UL"} content={<DisplayCustomEmoji emoji={servoEmoji(unloaderStatus)} />} />
            </div>
            <div className="row-container" style={{ justifyContent: "left" }}>
              <Subinfo title={"Load"} content={<DisplayCustomEmoji emoji={sensorEmoji(loadSensor)} />} />
              <Subinfo title={"Unload"} content={<DisplayCustomEmoji emoji={sensorEmoji(unloadSensor)} />} />
              <Subinfo title={"Buffer"} content={<DisplayCustomEmoji emoji={sensorEmoji(bufferSensor)} />} />
            </div>
          </>
        )}
        {isCageActionMode && (
          <>
            <div className="row-container" style={{ justifyContent: "left" }}>
              <div className="loading-bar-container">
                <div
                  className="loading-bar"
                  style={{ width: `${slotBarWidth}%`, backgroundColor: "rgba(50, 245, 39, 0.8)" }}
                >
                  <span className="loading-text">
                    {slots}/{maxSlots}
                  </span>
                </div>
              </div>
            </div>
            <div className="row-container" style={{ justifyContent: "left" }}>
              <Subinfo title={""} content={resolveStatusCodeOperatorAction()} />
            </div>
          </>
        )}
        <HorizontalLine />
      </div>
    </>
  );
}

export default Cage;
