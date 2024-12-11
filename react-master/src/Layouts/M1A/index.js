import React from "react";
import "../../Assets/Styles/styles.css";
import { useDict, Dicts } from "../../Middleware/get-api.js";
import { getColor, DEFAULT_MSG, httpPOST, exec } from "../../Utils/Utils.js";
import { Gap, HorizontalLine, Button, SubcontentTitle, Info } from "../../Components/index.js";

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

function M1A({ displayButtons = true }) {
  let a1StatusDict = null;
  let a2StatusDict = null;
  let a3StatusDict = null;

  let a1StatusCode = null;
  let a2StatusCode = null;
  let a3StatusCode = null;

  /* =================================== data update ================================== */
  const dictData = useDict(Dicts.m1a);
  const dictInfo = useDict(Dicts.info);
  const row = dictInfo ? dictInfo.row : 1;

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
        return "IDLE";
      case A1StatusCode.OFFLINE:
        return "🚨 OFFLINE";
      case A1StatusCode.FILLING:
        return "SORTING";
      case A1StatusCode.FILLING_TIMEOUT:
        return "REFILL POTS!";
      case A1StatusCode.FULL:
        return "WAITING FOR POTS TO CLEAR";
      case A1StatusCode.FULL_TIMEOUT:
        if (a2StatusCode === A2StatusCode.WAITING_BUF_IN || a2StatusCode === A2StatusCode.WAITING_BUF_IN_TIMEOUT)
          return "POT SORTER ALIGNED? CHANNELIZER JAMMED?";
        else return "WAITING FOR POTS TO CLEAR";
      case A1StatusCode.STOPPING:
        return "STOPPING";
      case A1StatusCode.STARTING:
        return "STARTING";
      default:
        return DEFAULT_MSG;
    }
  };

  const getA1StatusColor = () => {
    switch (a1StatusCode) {
      case A1StatusCode.IDLE:
        return getColor();
      case A1StatusCode.OFFLINE:
        return getColor("RED");
      case A1StatusCode.FILLING:
        return getColor("GREEN");
      case A1StatusCode.FILLING_TIMEOUT:
        return getColor("RED");
      case A1StatusCode.FULL:
        return getColor("YELLOW");
      case A1StatusCode.FULL_TIMEOUT:
        if (a2StatusCode === A2StatusCode.WAITING_BUF_IN || a2StatusCode === A2StatusCode.WAITING_BUF_IN_TIMEOUT)
          return getColor("RED");
        else return getColor("YELLOW");
      case A1StatusCode.STOPPING:
        return getColor("YELLOW");
      case A1StatusCode.STARTING:
        return getColor("YELLOW");
      default:
        return getColor();
    }
  };

  const getA2StatusText = () => {
    switch (a2StatusCode) {
      case A2StatusCode.IDLE:
        return "IDLE";
      case A2StatusCode.OFFLINE:
        return "🚨 OFFLINE";
      case A2StatusCode.DISPENSING:
        return "DISPENSING";
      case A2StatusCode.WAITING_BUF_IN:
        return "WAITING FOR POTS TO ENTER";
      case A2StatusCode.WAITING_BUF_IN_TIMEOUT:
        if (a1StatusCode === A1StatusCode.FULL_TIMEOUT) return "CHANNELIZER JAMMED?";
        return "WAITING FOR POTS TO ENTER";
      case A2StatusCode.WAITING_BUF_OUT:
        return "WAITING FOR POTS TO CLEAR";
      case A2StatusCode.STOPPING:
        return "STOPPING";
      case A2StatusCode.STARTING:
        return "STARTING";
      case A2StatusCode.SW_ERROR:
        return "SW ERROR";
      case A2StatusCode.SW_NOT_HOMED:
        return "SW NOT HOMED";
      case A2StatusCode.DISPENSER_NOT_HOMED:
        return "DISPENSER NOT HOMED";
      case A2StatusCode.SW_HOMING:
        return "SW HOMING";
      default:
        return DEFAULT_MSG;
    }
  };

  const getA2StatusColor = () => {
    switch (a2StatusCode) {
      case A2StatusCode.IDLE:
        return getColor();
      case A2StatusCode.OFFLINE:
        return getColor("RED");
      case A2StatusCode.DISPENSING:
        return getColor("GREEN");
      case A2StatusCode.WAITING_BUF_IN:
        return getColor("YELLOW");
      case A2StatusCode.WAITING_BUF_IN_TIMEOUT:
        if (a1StatusCode === A1StatusCode.FULL_TIMEOUT) return getColor("RED");
        return getColor("YELLOW");
      case A2StatusCode.WAITING_BUF_OUT:
        return getColor("YELLOW");
      case A2StatusCode.STOPPING:
        return getColor("YELLOW");
      case A2StatusCode.STARTING:
        return getColor("YELLOW");
      case A2StatusCode.SW_ERROR:
        return getColor("RED");
      case A2StatusCode.SW_NOT_HOMED:
        return getColor("RED");
      case A2StatusCode.DISPENSER_NOT_HOMED:
        return getColor("RED");
      case A2StatusCode.SW_HOMING:
        return getColor("YELLOW");
      default:
        return DEFAULT_MSG;
    }
  };

  const getA3StatusText = () => {
    switch (a3StatusCode) {
      case A3StatusCode.IDLE:
        return "IDLE";
      case A3StatusCode.OFFLINE:
        return "🚨 OFFLINE";
      case A3StatusCode.DISPENSING:
        return "SENDING POTS";
      case A3StatusCode.COMPUTING:
        return "GATHERING INFORMATION";
      case A3StatusCode.WAITING_BUF_IN:
        return "WAITING FOR POTS TO CLEAR";
      case A3StatusCode.STOPPING:
        return "STOPPING";
      case A3StatusCode.STARTING:
        return "STARTING";
      case A3StatusCode.SW_ERROR:
        return "SW ERROR";
      case A3StatusCode.SW_NOT_HOMED:
        return "SW NOT HOMED";
      case A3StatusCode.SW_HOMING:
        return "SW HOMING";
      default:
        return DEFAULT_MSG;
    }
  };

  const getA3StatusColor = () => {
    switch (a3StatusCode) {
      case A3StatusCode.IDLE:
        return getColor();
      case A3StatusCode.OFFLINE:
        return getColor("RED");
      case A3StatusCode.DISPENSING:
        return getColor("GREEN");
      case A3StatusCode.COMPUTING:
        return getColor("YELLOW");
      case A3StatusCode.WAITING_BUF_IN:
        return getColor("YELLOW");
      case A3StatusCode.STOPPING:
        return getColor("YELLOW");
      case A3StatusCode.STARTING:
        return getColor("YELLOW");
      case A3StatusCode.SW_ERROR:
        return getColor("RED");
      case A3StatusCode.SW_NOT_HOMED:
        return getColor("RED");
      case A3StatusCode.SW_HOMING:
        return getColor("YELLOW");
      default:
        return getColor();
    }
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
        <SubcontentTitle text={"Diet Tank"} link={`http://10.207.1${row}.10`} />
        <Info title="ⓘ Status" text={"UNDER DEVELOPMENT"} color={getColor()} />
        <Gap height="15" />
        <SubcontentTitle text={"Pot Sorter"} link={`http://10.207.1${row}.11`} />
        <Info title="ⓘ Status" text={getA1StatusText()} color={getA1StatusColor()} />
        <Gap height="15" />
        <SubcontentTitle text={"Diet Dispenser"} link={`http://10.207.1${row}.12`} />
        {/* <Gap />
        <DisplayImage link={"https://cdn.theorg.com/4fcdc583-1643-4367-9dce-e92104596f1d_thumb.jpg"} width={100} />
        <Gap /> */}
        <Info title="ⓘ Status" text={getA2StatusText()} color={getA2StatusColor()} />
        <Gap height="3" />
        {displayButtons && (
          <div className="buttons-container">
            <Button
              name="Raise Nozzle"
              onclick={() => exec("Raise Nozzle", httpPOST, "/raise_nozzle")}
              disable={a1StatusCode === A1StatusCode.OFFLINE}
            />
            <Button
              name="Lower Nozzle"
              onclick={() => exec("Lower Nozzle", httpPOST, "/lower_nozzle")}
              disable={a1StatusCode === A1StatusCode.OFFLINE}
            />
            <Button
              name="Home SW"
              onclick={() => exec("Home Diet Dispenser Starwheel", httpPOST, "/home_a2_sw")}
              disable={a1StatusCode === A1StatusCode.OFFLINE}
            />
          </div>
        )}
        <Gap height="15" />
        <SubcontentTitle text={"Pot Dispenser"} link={`http://10.207.1${row}.13`} />
        <Info title="ⓘ Status" text={getA3StatusText()} color={getA3StatusColor()} />
        <Gap height="3" />
        {displayButtons && (
          <div className="buttons-container">
            <Button
              name="Home SW"
              onclick={() => exec("Home Pot Dispenser Starwheel", httpPOST, "/home_a3_sw")}
              disable={a3StatusCode === A3StatusCode.OFFLINE}
            />
          </div>
        )}
      </div>
    </>
  );
}

export default M1A;
