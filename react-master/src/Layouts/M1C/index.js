import React from "react";
import { useState, useEffect } from "react";
import "../../Assets/Styles/styles.css";
import { useDict, Dicts } from "../../Middleware/get-api.js";
import { getColor, DEFAULT_MSG } from "../../Utils/Utils.js";
import { Gap, SubcontentTitle, Info } from "../../Components/index.js";

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

function M1C() {
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
        return "IDLE";
      case C1StatusCode.OFFLINE:
        return "🚨 OFFLINE";
      case C1StatusCode.SORTING:
        return "SORTING";
      case C1StatusCode.SORTING_TIMEOUT:
        return "REFILL CHIMNEY! (JAMMED STARWHEEL / CHANNEL?)";
      case C1StatusCode.WAITING_BUF_OUT:
        return "WAITING FOR CHIMNEYS TO CLEAR";
      case C1StatusCode.WAITING_BUF_OUT_TIMEOUT:
        if (c2StatusCode === C2StatusCode.WAITING_FOR_CHIMNEY_TIMEOUT)
          return "CHIMNEY NOT CLEARING! (CHANNELIZER STUCK? FLIPPED CHIMNEY?)";
        return "WAITING FOR CHIMNEYS TO CLEAR";
      case C1StatusCode.STARTING:
        return "STARTING";
      case C1StatusCode.STOPPING:
        return "STOPPING";
      default:
        return DEFAULT_MSG;
    }
  };

  const getC1StatusColor = () => {
    switch (c1StatusCode) {
      case C1StatusCode.IDLE:
        return getColor();
      case C1StatusCode.OFFLINE:
        return getColor("RED");
      case C1StatusCode.SORTING:
        return getColor("GREEN");
      case C1StatusCode.SORTING_TIMEOUT:
        return getColor("RED");
      case C1StatusCode.WAITING_BUF_OUT:
        return getColor("YELLOW");
      case C1StatusCode.WAITING_BUF_OUT_TIMEOUT:
        if (c2StatusCode === C2StatusCode.WAITING_FOR_CHIMNEY_TIMEOUT) return getColor("RED");
        return getColor("YELLOW");
      case C1StatusCode.STARTING:
        return getColor("YELLOW");
      case C1StatusCode.STOPPING:
        return getColor("YELLOW");
      default:
        return getColor();
    }
  };

  const getC2StatusText = () => {
    switch (c2StatusCode) {
      case C2StatusCode.IDLE:
        return "IDLE";
      case C2StatusCode.OFFLINE:
        return "🚨 OFFLINE";
      case C2StatusCode.CAPPING:
        return "CAPPING";
      case C2StatusCode.WAITING_FOR_CHIMNEY:
        return "WAITING FOR CHIMNEY";
      case C2StatusCode.WAITING_FOR_CHIMNEY_TIMEOUT:
        if (c1StatusCode === C1StatusCode.WAITING_BUF_OUT_TIMEOUT)
          return "NO CHIMNEY! (CHANNELIZER STUCK? FLIPPED CHIMNEY?)";
        return "WAITING FOR CHIMNEY";
      case C2StatusCode.WAITING_FOR_POT:
        return "WAITING FOR POTS";
      case C2StatusCode.STARTING:
        return "STARTING";
      case C2StatusCode.STOPPING:
        return "STOPPING";
      default:
        return DEFAULT_MSG;
    }
  };

  const getC2StatusColor = () => {
    switch (c2StatusCode) {
      case C2StatusCode.IDLE:
        return getColor();
      case C2StatusCode.OFFLINE:
        return getColor("RED");
      case C2StatusCode.CAPPING:
        return getColor("GREEN");
      case C2StatusCode.WAITING_FOR_CHIMNEY:
        return getColor("YELLOW");
      case C2StatusCode.WAITING_FOR_CHIMNEY_TIMEOUT:
        if (c1StatusCode === C1StatusCode.WAITING_BUF_OUT_TIMEOUT) return getColor("RED");
        return getColor("YELLOW");
      case C2StatusCode.WAITING_FOR_POT:
        return getColor("YELLOW");
      case C2StatusCode.STARTING:
        return getColor("YELLOW");
      case C2StatusCode.STOPPING:
        return getColor("YELLOW");
      default:
        return DEFAULT_MSG;
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
        <SubcontentTitle text={"Chimney Sorter"} link={`http://10.207.1${row}.14`} />
        <Info title="ⓘ Status" text={getC1StatusText()} color={getC1StatusColor()} />
        <Gap height="15" />
        <SubcontentTitle text={"Chimney Capper"} link={`http://10.207.1${row}.15`} />
        <Info title="ⓘ Status" text={getC2StatusText()} color={getC2StatusColor()} />
      </div>
    </>
  );
}

export default M1C;
