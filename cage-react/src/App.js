import React, { useEffect, useState } from "react";
// import { FetchBoardData } from "./Middleware/FetchBoardData";
// import { FetchExperimentData } from "./Middleware/ExperimentData"; // Import the custom hook
// import { useFetchData, parseBoardData, parseExperimentData } from "./Middleware/fetchData"; // !marco ori
import { useDict, Dicts } from "./Middleware/fetchData";
import Header from "./Components/Header";
import CageStatus from "./Components/CageStatus";
import { VideoFeed } from "./Components/VideoFeed";
// import VideoFeed from "./Components/VideoFeed";
import Button from "./Components/Button";
import { getInput } from "./Components/Placeholder";
import hostname from "./Components/Hostname";

import * as PostActions from "./Actions/Post";
import "./App.css";

class StatusCode {
  static SW_INITIALIZING = "0";
  static PRIMING_CHANNELS = "1";
  static UL_INITIALIZING = "2";
  static IDLE = "3";
  static ERROR_SW = "4";
  static ERROR_UL = "5";
  static CLEARING_SERVO_ERROR = "6";
  static UNABLE_TO_CLEAR_ERROR = "7";
  static ERROR_CAMERA = "8";
  static NORMAL = "9";
  static LOADING = "10";
  static WAIT_ACK = "11";
  static SELF_FIX_PENDING = "12";
  static WAITING_FOR_BUFFER = "13";
  static WAITING_FOR_PASSIVE_LOAD = "14";
  static INIT_WAITING_FOR_BUFFER = "15";
  static INIT_WAITING_FOR_PASSIVE_LOAD = "16";
  static WARNING_UNLOADER = "17";
}

function App() {
  // const [boardData, setBoardData] = useState(null);
  // const [experimentData, setExperimentData] = useState(null);
  // const [error, setError] = useState(null);
  const [position, setPosition] = useState("");
  const [pauseinterval, setInterval] = useState("");
  const [purgefrequency, setFrequency] = useState("");
  const [cycletime, setCycleTime] = useState("");
  const [valvedelay, setDelay] = useState("");

  function resolveStatusCode(status_code) {
    switch (status_code) {
      case StatusCode.SW_INITIALIZING:
        return "initializing starwheel";
      case StatusCode.PRIMING_CHANNELS:
        return "priming channels";
      case StatusCode.UL_INITIALIZING:
        return "initializing unloader";
      case StatusCode.IDLE:
        return "doing nothing";
      case StatusCode.ERROR_SW:
        return "starwheel error";
      case StatusCode.ERROR_UL:
        return "unloader error";
      case StatusCode.CLEARING_SERVO_ERROR:
        return "clearing servo error";
      case StatusCode.UNABLE_TO_CLEAR_ERROR:
        return "unable to clear servo error";
      case StatusCode.ERROR_CAMERA:
        return "camera fault";
      case StatusCode.NORMAL:
        return "normal";
      case StatusCode.LOADING:
        return "system loading";
      case StatusCode.WAIT_ACK:
        return "too many errors, ack fault";
      case StatusCode.SELF_FIX_PENDING:
        return "error detected, attempting self fix";
      case StatusCode.WAITING_FOR_BUFFER:
        return "waiting for buffer to be filled";
      case StatusCode.WAITING_FOR_PASSIVE_LOAD:
        return "waiting for pot to enter starwheel";
      case StatusCode.INIT_WAITING_FOR_BUFFER:
        return "waiting for buffer to proceed with starwheel init";
      case StatusCode.INIT_WAITING_FOR_PASSIVE_LOAD:
        return "waiting for pot to enter starwheel to proceed with starwheel init";
      case StatusCode.WARNING_UNLOADER:
        return "check unload sensor if working or unloader";
      default:
        return "unknown status";
    }
  }

  useEffect(() => {
    document.title = ` 🥚 ${hostname}`;
  }, [hostname]);

  // FetchBoardData(setBoardData, setError);
  // FetchExperimentData(setExperimentData, setError);
  // Use generalized fetch data hook
  // useFetchData(setBoardData, setError, "http://cege0x0000:8080/BoardData", parseBoardData);
  // useFetchData(setExperimentData, setError, "http://cege0x0000:8080/ExperimentData", parseExperimentData);

  // useFetchData(setBoardData, setError, `/BoardData`, parseBoardData);
  // useFetchData(setExperimentData, setError, `/ExperimentData`, parseExperimentData);

  const boardData = useDict(Dicts.boardData);
  const experimentData = useDict(Dicts.experimentData);
  const experimentSettings = useDict(Dicts.experimentSettings);

  // Extract statuses from the fetched data
  const starWheelStatus = boardData ? boardData.star_wheel_status : "";
  const unloaderStatus = boardData ? boardData.unloader_status : "";
  // const modeStatus = boardData ? boardData.mode : "";
  const sensorsValues = boardData ? boardData.sensors_values : "(0, 0, 0, 0)";
  const systemStatus = boardData ? resolveStatusCode(boardData.status_code) : resolveStatusCode("99");

  const get_pause_interval = experimentSettings ? experimentSettings.experiment_pause_interval : "";
  const get_purge_frequency = experimentSettings ? experimentSettings.experiment_purge_frequency : "";
  const get_cycle_time = experimentSettings ? experimentSettings.cycle_time : "";
  const get_valve_delay = experimentSettings ? experimentSettings.valve_delay : "";

  // console.log("pause_interval:", pause_interval);

  const { starWheel, unloader, mode, load, buffer } = CageStatus(
    boardData?.star_wheel_status,
    boardData?.unloader_status,
    boardData?.mode,
    sensorsValues
  );

  // const { starWheel, unloader, mode } = CageStatus(starWheelStatus, unloaderStatus, modeStatus);

  const isIdle = mode.text === "IDLE";
  const isNormal = starWheelStatus === "normal" && unloaderStatus === "normal";

  const handleMoveSW = () => {
    PostActions.MoveSW(position);
  };

  const handleSaveOffset = () => {
    PostActions.SaveOffset(position);
  };

  const handleSetInterval = () => {
    PostActions.SetInterval(pauseinterval);
  };

  const handleSetPurgeFrequency = () => {
    PostActions.SetFrequency(purgefrequency);
  };

  const handleSetCycleTime = () => {
    PostActions.SetCycleTime(cycletime);
  };

  const handleSetValveDelay = () => {
    PostActions.SetValveDelay(valvedelay);
  };

  const handleStop = () => {
    PostActions.Stop(mode.text);
  };

  return (
    <div>
      <Header />
      <div style={{ display: "flex", width: "100%" }}>
        <div className="columns-container" style={{ width: "40%" }}>
          <div className="subcontent-container">
            <div className="subcontent-title">Production Status</div>
            <div className="subinfo-horizontal-line"></div>
            <div className="subcontent-info-same-row-container">
              ⓘ Mode
              <div className="subcontent-info-box" style={{ backgroundColor: mode.color }}>
                {mode.text}
              </div>
            </div>
            <div className="subcontent-info-same-row-container">
              ⓘ Status
              <div className="subcontent-info-box">{systemStatus}</div>
            </div>
            <div className="gap"></div>
            <div className="subcontent-title">Commands</div>
            <div className="subinfo-horizontal-line"></div>
            <div className="buttons-container">
              <Button onClick={PostActions.MoveCCW} label="↪️" disabled={!isIdle} />
              <Button onClick={PostActions.Unload} label="⤵️" disabled={!isIdle} />
              <Button onClick={PostActions.MoveCW} label="↩️" disabled={!isIdle} />
            </div>
            <div className="gap"></div>
            <div className="subcontent-title">Servos Init</div>
            <div className="subinfo-horizontal-line"></div>
            <div className="buttons-container">
              <Button onClick={PostActions.SWInit} label="SW Init" disabled={!isIdle} />
              <Button onClick={PostActions.ULInit} label="UL Init" disabled={!isIdle} />
              <Button onClick={PostActions.ALLInit} label="ALL Init" disabled={!isIdle} />
              <Button onClick={PostActions.ClearError} label="Clear Error" />
            </div>
            <div className="gap"></div>
            <div className="subcontent-title">SW Alignment</div>
            <div className="subinfo-horizontal-line"></div>
            <div className="buttons-container">
              <Button onClick={PostActions.SaveZero} label="Save Zero" disabled={!isIdle} />
              <Button onClick={handleSaveOffset} label="Save Offset" disabled={!isIdle} />
              <Button onClick={handleMoveSW} label="Move SW" disabled={!isIdle} />
              {getInput("number", "position", position, setPosition)}
            </div>
            <div className="gap"></div>
            <div className="subcontent-title">Experiment Settings</div>
            <div className="subinfo-horizontal-line"></div>
            <div className="buttons-container">
              <Button onClick={handleSetInterval} label="Set Interval" />
              <div className="subcontent-info-text">{get_pause_interval}</div>
              {getInput("number", "interval", pauseinterval, setInterval, "Unit: seconds")}
            </div>
            {/* <div className="buttons-container">
              <Button onClick={handleSetPurgeFrequency} label="Set Purge freq" />
              <div className="subcontent-info-text">{get_purge_frequency}</div>
              {getInput("number", "interval", purgefrequency, setFrequency, "Enter number")}
            </div> */}
            <div className="buttons-container">
              <Button onClick={handleSetCycleTime} label="Set Cycle Time" />
              <div className="subcontent-info-text">{get_cycle_time}</div>
              {getInput("number", "cycletime", cycletime, setCycleTime, "Unit: seconds")}
            </div>
            <div className="buttons-container">
              <Button onClick={handleSetValveDelay} label="Set Valve delay" />
              <div className="subcontent-info-text">{get_valve_delay}</div>
              {getInput("number", "valvedelay", valvedelay, setDelay, "Unit: milliseconds")}
            </div>
            <div className="gap"></div>
            {mode.text === "EXPERIMENT" && experimentData && (
              <div className="subcontent-info-same-row-container">
                ⓘ Experiment State:
                <div className="subcontent-info-box" style={{ backgroundColor: mode.color }}>
                  {experimentData}
                </div>
              </div>
            )}
          </div>
          {/* <div className="subcontent-container">
            <VideoFeedAlignment />
          </div> */}
        </div>
        <div className="columns-container" style={{ width: "60%" }}>
          <div className="subcontent-container">
            <VideoFeed />
            <div className="subcontent-title">Servos & Sensors</div>
            <div className="subinfo-horizontal-line"></div>
            <div className="icon-container">
              <div className={`gear ${starWheel}`}>
                <i className="fas fa-cog" aria-hidden="true"></i>
                <span>SW</span>
              </div>
              <div className={`gear ${unloader}`}>
                <i className="fas fa-cog" aria-hidden="true"></i>
                <span>UL</span>
              </div>
              <div className={`circle ${load}`}>LOAD</div>
              <div className={`circle ${buffer}`}>BUFFER</div>
            </div>
            <div className="gap"></div>
            <div className="subcontent-title">Operation Control</div>
            <div className="subinfo-horizontal-line"></div>
            <div className="buttons-container">
              <Button onClick={PostActions.PNP} label="PNP" disabled={!isIdle || !isNormal} />
              <Button onClick={PostActions.Dummy} label="DUMMY" disabled={!isIdle || !isNormal} />
              <Button onClick={PostActions.Experiment} label="EXPERIMENT" disabled={!isIdle || !isNormal} />
              <Button onClick={handleStop} label="STOP" disabled={isIdle} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
