import React from "react";
import { useState, useEffect } from "react";
import "../../Assets/Styles/styles.css";
import { useDict, Dicts } from "../../Middleware/get-api.js";
import { getColor, DEFAULT_MSG } from "../../Utils/Utils.js";
import { Gap, HorizontalLine, SubcontentTitle, InfoSameRow } from "../../Components/index.js";

function M1C() {
  const [c1StatusDict, setC1StatusDict] = useState(null);
  const [c2StatusDict, setC2StatusDict] = useState(null);

  /* ---------------------------------------------------------------------------------- */
  // data update
  const dictData = useDict(Dicts.m1c);

  useEffect(() => {
    if (dictData) {
      setC1StatusDict(dictData["c1"]);
      setC2StatusDict(dictData["c2"]);
    } else {
      setC1StatusDict(null);
      setC2StatusDict(null);
    }
  }, [dictData]);

  /* ---------------------------------------------------------------------------------- */
  function getC1StatusText() {
    if (c1StatusDict && c1StatusDict["connected"] === "True") {
      if (c1StatusDict["running"] === "True") {
        if (c1StatusDict["buff_out"] === "True") {
          return "RUNNING";
        }
        return "BELT FULL";
      }
      return "IDLE";
    }
    return DEFAULT_MSG;
  }

  function getC1StatusColor() {
    if (c1StatusDict && c1StatusDict["connected"] === "True") {
      if (c1StatusDict["running"] === "True") {
        if (c1StatusDict["buff_out"] === "True") {
          return getColor("GREEN");
        }
        return getColor("YELLOW");
      }
      return getColor("BLUE");
    }
    return getColor("DEFAULT");
  }

  function getC2StatusText() {
    if (c1StatusDict && c2StatusDict["connected"] === "True") {
      if (c2StatusDict["running"] === "True") {
        if (c2StatusDict["chimney_sensor"] === "True") {
          if (c2StatusDict["pot_sensor"] === "True") {
            return "RUNNING";
          }
          return "WAITING FOR POTS";
        }
        return "WAITING FOR CHIMNEYS";
      }
      return "IDLE";
    }
    return DEFAULT_MSG;
  }

  function getC2StatusColor() {
    if (c1StatusDict && c2StatusDict["connected"] === "True") {
      if (c2StatusDict["running"] === "True") {
        if (c2StatusDict["chimney_sensor"] === "True") {
          if (c2StatusDict["pot_sensor"] === "True") {
            return getColor("GREEN");
          }
          return getColor("YELLOW");
        }
        return getColor("YELLOW");
      }
      return getColor("BLUE");
    }
    return getColor("DEFAULT");
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
        <InfoSameRow title="ⓘ Status" text={getC1StatusText()} color={getC1StatusColor()} />
        <Gap height="20" />
        <SubcontentTitle text={"Chimney Capper"} />
        <HorizontalLine />
        <InfoSameRow title="ⓘ Status" text={getC2StatusText()} color={getC2StatusColor()} />
      </div>
    </>
  );
}

export default M1C;
