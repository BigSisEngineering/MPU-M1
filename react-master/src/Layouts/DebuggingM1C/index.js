import React from "react";
import { useState, useEffect } from "react";
import "../../Assets/Styles/styles.css";
import { useDict, Dicts } from "../../Middleware/get-api.js";
import { getColor, DEFAULT_MSG } from "../../Utils/Utils.js";
import m1cSensors from "../../Assets/Media/m1c_sensors.png";
import {
  Gap,
  HorizontalLine,
  SubcontentTitle,
  DisplayCustomEmoji,
  CustomEmoji,
  Subinfo,
  DisplayImage,
} from "../../Components/index.js";

class C1StatusCode {
  static IDLE = 0;
  static OFFLINE = 1;
  static SORTING = 2;
  static SORTING_TIMEOUT = 3;
  static WAITING_BUF_OUT = 4;
  static WAITING_BUF_OUT_TIMEOUT = 5;
  static STOPPING = 6;
  static STARTING = 7;
}

class C2StatusCode {
  static IDLE = 0;
  static OFFLINE = 1;
  static CAPPING = 2;
  static WAITING_FOR_CHIMNEY = 3;
  static WAITING_FOR_CHIMNEY_TIMEOUT = 4;
  static WAITING_FOR_POT = 5;
  static STOPPING = 6;
  static STARTING = 7;
}

function DebuggingM1C() {
  let c1StatusDict = null;
  let c2StatusDict = null;
  let c1StatusCode = null;
  let c2StatusCode = null;

  /* =================================== data update ================================== */
  const dictData = useDict(Dicts.m1c);
  const dictInfo = useDict(Dicts.info);
  const row = dictInfo ? dictInfo["row"] : null;

  if (dictData) {
    c1StatusDict = dictData["c1"];
    c2StatusDict = dictData["c2"];
    c1StatusCode = dictData["c1"]["status_code"];
    c2StatusCode = dictData["c2"]["status_code"];
  }

  const getC1StatusText = () => {
    switch (c1StatusCode) {
      case C1StatusCode.IDLE:
        return "Chimney Sorter is in IDLE mode.";
      case C1StatusCode.OFFLINE:
        return "Duet is offline.";
      case C1StatusCode.SORTING:
        return "Sorting chimneys.";
      case C1StatusCode.SORTING_TIMEOUT:
        return "Sorting chimneys. It's been more than 30 seconds since a chimney is detected by the output buffer.";
      case C1StatusCode.WAITING_BUF_OUT:
        return "Waiting for the chimneys at the output buffer to clear.";
      case C1StatusCode.WAITING_BUF_OUT_TIMEOUT:
        return "System has been waiting for the chimneys at the output buffer to clear for more than 30 seconds.";
      case C1StatusCode.STARTING:
        return "Chimney Sorter is starting.";
      case C1StatusCode.STOPPING:
        return "Chimney Sorter is stopping.";
      default:
        return DEFAULT_MSG;
    }
  };

  const getC2StatusText = () => {
    switch (c2StatusCode) {
      case C2StatusCode.IDLE:
        return "Chimney Placer is in IDLE mode.";
      case C2StatusCode.OFFLINE:
        return "Duet is offline.";
      case C2StatusCode.CAPPING:
        return "Capping.";
      case C2StatusCode.WAITING_FOR_CHIMNEY:
        return "Waiting for chimneys to arrive.";
      case C2StatusCode.WAITING_FOR_CHIMNEY_TIMEOUT:
        return "System has been waiting for chimneys to arrive for more than 30 seconds.";
      case C2StatusCode.WAITING_FOR_POT:
        return "Waiting for pots to arrive.";
      case C2StatusCode.STARTING:
        return "Chimney Placer is starting.";
      case C2StatusCode.STOPPING:
        return "Chimney Placer is stoppping.";
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
        <DisplayImage link={m1cSensors} width={80} height={35} opacity={0.7} />
        <Gap height="15" />
        <SubcontentTitle text={"Chimney Sorter"} link={`http://10.207.1${row}.14`} />
        <HorizontalLine />
        <div className="row-container" style={{ padding: "0px 20px" }}>
          <Subinfo
            title="⦾ OUTPUT BUFFER"
            content={
              <DisplayCustomEmoji
                emoji={c1StatusDict ? getEmoji(c1StatusDict["buff_out"]) : CustomEmoji.black_circle}
              />
            }
            widthPercentage={90}
          />
        </div>
        <div className="row-container" style={{ padding: "0px 20px" }}>
          <Subinfo
            title="⦾ CHANNEL 1 BUFFER"
            content={
              <DisplayCustomEmoji
                emoji={c1StatusDict ? getEmoji(c1StatusDict["chn1_sensor"]) : CustomEmoji.black_circle}
              />
            }
            widthPercentage={90}
          />
        </div>
        <div className="row-container" style={{ padding: "0px 20px" }}>
          <Subinfo
            title="⦾ CHANNEL 2 BUFFER"
            content={
              <DisplayCustomEmoji
                emoji={c1StatusDict ? getEmoji(c1StatusDict["chn2_sensor"]) : CustomEmoji.black_circle}
              />
            }
            widthPercentage={90}
          />
        </div>
        <div className="row-container" style={{ padding: "0px 20px" }}>
          <Subinfo
            title="⦾ CHANNEL 3 BUFFER"
            content={
              <DisplayCustomEmoji
                emoji={c1StatusDict ? getEmoji(c1StatusDict["chn3_sensor"]) : CustomEmoji.black_circle}
              />
            }
            widthPercentage={90}
          />
        </div>
        <div className="row-container" style={{ padding: "0px 20px" }}>
          <Subinfo title="ⓢ STATUS" content={getC1StatusText()} widthPercentage={90} />
        </div>

        <Gap height="15" />
        <SubcontentTitle text={"Chimney Capper"} link={`http://10.207.1${row}.15`} />
        <HorizontalLine />
        <div className="row-container" style={{ padding: "0px 20px" }}>
          <Subinfo
            title="⦾ POT SENSOR"
            content={
              <DisplayCustomEmoji
                emoji={c2StatusDict ? getEmoji(c2StatusDict["pot_sensor"]) : CustomEmoji.black_circle}
              />
            }
            widthPercentage={90}
          />
        </div>
        <div className="row-container" style={{ padding: "0px 20px" }}>
          <Subinfo
            title="⦾ CHIMNEY SENSOR"
            content={
              <DisplayCustomEmoji
                emoji={c2StatusDict ? getEmoji(c2StatusDict["chimney_sensor"]) : CustomEmoji.black_circle}
              />
            }
            widthPercentage={90}
          />
        </div>
        <div className="row-container" style={{ padding: "0px 20px" }}>
          <Subinfo title="ⓢ STATUS" content={getC2StatusText()} widthPercentage={90} />
        </div>
      </div>
    </>
  );
}

export default DebuggingM1C;
