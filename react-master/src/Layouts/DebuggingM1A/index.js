import React from "react";
import "../../Assets/Styles/styles.css";
import { useDict, Dicts } from "../../Middleware/get-api.js";
import { DEFAULT_MSG } from "../../Utils/Utils.js";
import m1aSensors from "../../Assets/Media/m1a_sensors.png";
import {
  Gap,
  HorizontalLine,
  SubcontentTitle,
  DisplayCustomEmoji,
  CustomEmoji,
  Subinfo,
  Info,
  DisplayImage,
} from "../../Components/index.js";

class A1StatusCode {
  static IDLE = 0;
  static OFFLINE = 1;
  static FILLING = 2;
  static FILLING_TIMEOUT = 3; // empty for too long
  static FULL = 4;
  static FULL_TIMEOUT = 5; // full for too long
  static STOPPING = 6;
  static STARTING = 7;
}

class A2StatusCode {
  static IDLE = 0;
  static OFFLINE = 1;
  static DISPENSING = 2;
  static WAITING_BUF_IN = 3;
  static WAITING_BUF_IN_TIMEOUT = 4; // wait buff in for too long
  static WAITING_BUF_OUT = 5;
  static STOPPING = 6;
  static STARTING = 7;
  static SW_ERROR = 8;
  static SW_NOT_HOMED = 9;
  static DISPENSER_NOT_HOMED = 10;
  static SW_HOMING = 11;
}

class A3StatusCode {
  static IDLE = 0;
  static OFFLINE = 1;
  static DISPENSING = 2;
  static COMPUTING = 3;
  static WAITING_BUF_IN = 4;
  static STOPPING = 5;
  static STARTING = 6;
  static SW_ERROR = 7;
  static SW_NOT_HOMED = 8;
  static SW_HOMING = 9;
}

function DebuggingM1A() {
  let a1StatusDict = null;
  let a2StatusDict = null;
  let a3StatusDict = null;

  let a1StatusCode = null;
  let a2StatusCode = null;
  let a3StatusCode = null;

  /* =================================== data update ================================== */
  const dictData = useDict(Dicts.m1a);
  const dictInfo = useDict(Dicts.info);
  const row = dictInfo ? dictInfo["row"] : null;

  if (dictData) {
    a1StatusDict = dictData["a1"];
    a2StatusDict = dictData["a2"];
    a3StatusDict = dictData["a3"];
    a1StatusCode = dictData["a1"]["status_code"];
    a2StatusCode = dictData["a2"]["status_code"];
    a3StatusCode = dictData["a3"]["status_code"];
  }

  const getA1StatusText = () => {
    switch (a1StatusCode) {
      case A1StatusCode.IDLE:
        return "Pot Sorter is in IDLE mode.";
      case A1StatusCode.OFFLINE:
        return "DUET is offline.";
      case A1StatusCode.FILLING:
        return "Transfer belt should be moving.";
      case A1StatusCode.FILLING_TIMEOUT:
        return "Transfer belt should be moving. It's been more than 30 seconds since a pot passed through the output buffer.";
      case A1StatusCode.FULL:
        return "Pots are filled up to the buffer.";
      case A1StatusCode.FULL_TIMEOUT:
        return "Pots are filled up to the buffer for more than 30 seconds.";
      case A1StatusCode.STOPPING:
        return "Pot Sorter is stopping.";
      case A1StatusCode.STARTING:
        return "Pot Sorter is starting.";
      default:
        return DEFAULT_MSG;
    }
  };

  const getA2StatusText = () => {
    switch (a2StatusCode) {
      case A2StatusCode.IDLE:
        return "Diet Dispenser is in IDLE mode.";
      case A2StatusCode.OFFLINE:
        return "DUET is offline.";
      case A2StatusCode.DISPENSING:
        return "Diet dispenser is dispensing.";
      case A2StatusCode.WAITING_BUF_IN:
        return "Waiting for pots to get past the channelizer.";
      case A2StatusCode.WAITING_BUF_IN_TIMEOUT:
        return "System has been waiting for pots to get past the channelizer for more than 30 seconds. ";
      case A2StatusCode.WAITING_BUF_OUT:
        return "Waiting for pots to cleared from the output.";
      case A2StatusCode.STOPPING:
        return "Diet Dispenser is stopping.";
      case A2StatusCode.STARTING:
        return "Diet Dispenser is starting.";
      case A2StatusCode.SW_ERROR:
        return "Starwheel Error detected.";
      case A2StatusCode.SW_NOT_HOMED:
        return "Starwheel is not homed.";
      case A2StatusCode.DISPENSER_NOT_HOMED:
        return "Nozzle axis is raised.";
      case A2StatusCode.SW_HOMING:
        return "Starwheel is homing. (It takes 50s in total, even after it's visibly homed)";
      default:
        return DEFAULT_MSG;
    }
  };

  const getA3StatusText = () => {
    switch (a3StatusCode) {
      case A3StatusCode.IDLE:
        return "Pot Dispenser is in IDLE mode.";
      case A3StatusCode.OFFLINE:
        return "DUET is offline.";
      case A3StatusCode.DISPENSING:
        return "Pots are being sent.";
      case A3StatusCode.COMPUTING:
        return "System is fetching data from the cages.";
      case A3StatusCode.WAITING_BUF_IN:
        return "Waiting for pots to fill up to the buffer.";
      case A3StatusCode.STOPPING:
        return "Pot Dispenser is stopping.";
      case A3StatusCode.STARTING:
        return "Pot Dispenser is starting.";
      case A3StatusCode.SW_ERROR:
        return "Starwheel Error detected.";
      case A3StatusCode.SW_NOT_HOMED:
        return "Starwheel not homed.";
      case A3StatusCode.SW_HOMING:
        return "Starwheel is homing. (It takes 50s in total, even after it's visibly homed)";
      default:
        return DEFAULT_MSG;
    }
  };

  const getEmoji = (bool) => {
    return bool ? CustomEmoji.green_circle : CustomEmoji.red_circle;
  };

  return (
    <>
      <div
        className="subcontent-container"
        style={{
          fontSize: "16px",
          letterSpacing: "0.05em",
        }}
      >
        <SubcontentTitle text={"Sensor Map"} />
        <HorizontalLine />
        <Gap height="3" />
        <DisplayImage link={m1aSensors} width={80} height={35} opacity={0.7} />
        <Gap height="15" />
        <SubcontentTitle text={"Diet Tank"} link={`http://10.207.1${row}.10`} />
        <HorizontalLine />
        <Gap height="15" />
        <SubcontentTitle text={"Pot Sorter"} link={`http://10.207.1${row}.11`} />
        <HorizontalLine />
        <div className="row-container" style={{ padding: "0px 20px" }}>
          <Subinfo
            title="⦾ OUTPUT BUFFER"
            content={
              <DisplayCustomEmoji
                emoji={a1StatusDict ? getEmoji(a1StatusDict["buff_out"]) : CustomEmoji.black_circle}
              />
            }
            widthPercentage={90}
          />
        </div>
        <div className="row-container" style={{ padding: "0px 20px" }}>
          <Subinfo title="ⓢ STATUS" content={getA1StatusText()} widthPercentage={90} />
        </div>

        <Gap height="15" />
        <SubcontentTitle text={"Diet Dispenser"} link={`http://10.207.1${row}.12`} />
        <HorizontalLine />
        <div className="row-container" style={{ padding: "0px 20px" }}>
          <Subinfo
            title="⦾ INPUT BUFFER"
            content={
              <DisplayCustomEmoji emoji={a2StatusDict ? getEmoji(a2StatusDict["buff_in"]) : CustomEmoji.black_circle} />
            }
            widthPercentage={90}
          />
        </div>
        <div className="row-container" style={{ padding: "0px 20px" }}>
          <Subinfo
            title="⦾ OUTPUT BUFFER"
            content={
              <DisplayCustomEmoji
                emoji={a2StatusDict ? getEmoji(a2StatusDict["buff_out"]) : CustomEmoji.black_circle}
              />
            }
            widthPercentage={90}
          />
        </div>
        <div className="row-container" style={{ padding: "0px 20px" }}>
          <Subinfo
            title="⦾ POT SENSOR"
            content={
              <DisplayCustomEmoji
                emoji={a2StatusDict ? getEmoji(a2StatusDict["pot_sensor"]) : CustomEmoji.black_circle}
              />
            }
            widthPercentage={90}
          />
        </div>
        <div className="row-container" style={{ padding: "0px 20px" }}>
          <Subinfo title="ⓢ STATUS" content={getA2StatusText()} widthPercentage={90} />
        </div>

        <Gap height="15" />
        <SubcontentTitle text={"Pot Dispenser"} link={`http://10.207.1${row}.13`} />
        <HorizontalLine />
        <div className="row-container" style={{ padding: "0px 20px" }}>
          <Subinfo
            title="⦾ INPUT BUFFER"
            content={
              <DisplayCustomEmoji emoji={a3StatusDict ? getEmoji(a3StatusDict["buff_in"]) : CustomEmoji.black_circle} />
            }
            widthPercentage={90}
          />
        </div>
        <div className="row-container" style={{ padding: "0px 20px" }}>
          <Subinfo
            title="⦾ POT SENSOR"
            content={
              <DisplayCustomEmoji
                emoji={a3StatusDict ? getEmoji(a3StatusDict["pot_sensor"]) : CustomEmoji.black_circle}
              />
            }
            widthPercentage={90}
          />
        </div>
        <div className="row-container" style={{ padding: "0px 20px" }}>
          <Subinfo title="ⓢ STATUS" content={getA3StatusText()} widthPercentage={90} />
        </div>
      </div>
    </>
  );
}

export default DebuggingM1A;
