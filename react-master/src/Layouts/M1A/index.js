import React from "react";
import { useState, useEffect } from "react";
import "../../Assets/Styles/styles.css";
import { useDict, Dicts } from "../../Middleware/get-api.js";
import { getColor, DEFAULT_MSG, httpPOST, exec } from "../../Utils/Utils.js";
import { Gap, HorizontalLine, Button, SubcontentTitle, InfoSameRow } from "../../Components/index.js";

function M1A() {
  const [a1StatusDict, setA1StatusDict] = useState(null);
  const [a2StatusDict, setA2StatusDict] = useState(null);
  const [a3StatusDict, setA3StatusDict] = useState(null);

  /* ---------------------------------------------------------------------------------- */
  // data update
  const dictData = useDict(Dicts.m1a);

  useEffect(() => {
    if (dictData) {
      setA1StatusDict(dictData["a1"]);
      setA2StatusDict(dictData["a2"]);
      setA3StatusDict(dictData["a3"]);
    } else {
      setA1StatusDict(null);
      setA2StatusDict(null);
      setA3StatusDict(null);
    }
  }, [dictData]);

  /* ---------------------------------------------------------------------------------- */

  function getA1StatusText() {
    if (a1StatusDict && a1StatusDict["connected"] === "True") {
      if (a1StatusDict["running"] === "True") {
        if (a1StatusDict["buff_out"] === "True") {
          return "RUNNING";
        }
        return "WAITING FOR POTS";
      }
      return "IDLE";
    }
    return DEFAULT_MSG;
  }

  function getA1StatusColor() {
    if (a1StatusDict && a1StatusDict["connected"] === "True") {
      if (a1StatusDict["running"] === "True") {
        if (a1StatusDict["buff_out"] === "True") {
          return getColor("GREEN");
        }
        return getColor("YELLOW");
      }
      return getColor("BLUE");
    }
    return getColor("DEFAULT");
  }

  function getA2StatusText() {
    if (a2StatusDict && a2StatusDict["connected"] === "True") {
      if (a2StatusDict["running"] === "True") {
        if (a2StatusDict["dispenser_homed"] === "True") {
          if (a2StatusDict["sw_error"] === "False") {
            if (a2StatusDict["sw_homed"] === "True") {
              if (a2StatusDict["buff_in"] === "False") {
                if (a2StatusDict["buff_out"] === "True") {
                  return "RUNNING";
                }
                return "POT DISPENSER BELT FULL";
              }
              return "WAITING FOR POTS";
            }
            return "SW NOT HOMED";
          }
          return "SW ERROR";
        }
        return "NOZZLE NOT HOMED";
      }
      return "IDLE";
    }
    return DEFAULT_MSG;
  }

  function getA2StatusColor() {
    if (a2StatusDict && a2StatusDict["connected"] === "True") {
      if (a2StatusDict["running"] === "True") {
        if (a2StatusDict["dispenser_homed"] === "True") {
          if (a2StatusDict["sw_error"] === "False") {
            if (a2StatusDict["sw_homed"] === "True") {
              if (a2StatusDict["buff_in"] === "False") {
                if (a2StatusDict["buff_out"] === "True") {
                  return getColor("GREEN");
                }
                return getColor("YELLOW");
              }
              return getColor("YELLOW");
            }
            return getColor("RED");
          }
          return getColor("RED");
        }
        return getColor("RED");
      }
      return getColor("BLUE");
    }
    return getColor("DEFAULT");
  }

  function getA3StatusText() {
    if (a3StatusDict && a3StatusDict["connected"] === "True") {
      if (a3StatusDict["running"] === "True") {
        if (a3StatusDict["sw_error"] === "False") {
          if (a3StatusDict["sw_homed"] === "True") {
            if (a3StatusDict["buff_in"] === "False") {
              return "RUNNING";
            }
            return "WAITING FOR POTS";
          }
          return "SW NOT HOMED";
        }
        return "SW ERROR";
      }
      return "IDLE";
    }
    return DEFAULT_MSG;
  }

  function getA3StatusColor() {
    if (a3StatusDict && a3StatusDict["connected"] === "True") {
      if (a3StatusDict["running"] === "True") {
        if (a3StatusDict["sw_error"] === "False") {
          if (a3StatusDict["sw_homed"] === "True") {
            if (a3StatusDict["buff_in"] === "False") {
              return getColor("GREEN");
            }
            return getColor("YELLOW");
          }
          return getColor("RED");
        }
        return getColor("RED");
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
        <SubcontentTitle text={"Pot Sorter"} />
        <HorizontalLine />
        <InfoSameRow title="ⓘ Status" text={getA1StatusText()} color={getA1StatusColor()} />
        <Gap height="20" />
        <SubcontentTitle text={"Diet Dispenser"} />
        <HorizontalLine />
        📷 Live Feed
        {/* <Gap />
        <DisplayImage link={"https://cdn.theorg.com/4fcdc583-1643-4367-9dce-e92104596f1d_thumb.jpg"} width={100} />
        <Gap /> */}
        <InfoSameRow title="ⓘ Status" text={getA2StatusText()} color={getA2StatusColor()} />
        <Gap />
        <div className="buttons-container">
          <Button name="Raise Nozzle" onclick={() => exec("Raise Nozzle", httpPOST, "/raise_nozzle")} />
          <Button name="Lower Nozzle" onclick={() => exec("Lower Nozzle", httpPOST, "/lower_nozzle")} />
          <Button name="Home SW" onclick={() => exec("Home Diet Dispenser Starwheel", httpPOST, "/home_a2_sw")} />
        </div>
        <Gap height="20" />
        <SubcontentTitle text={"Pot Dispenser"} />
        <HorizontalLine />
        <InfoSameRow title="ⓘ Status" text={getA3StatusText()} color={getA3StatusColor()} />
        <Gap />
        <div className="buttons-container">
          <Button name="Home SW" onclick={() => exec("Home Pot Dispenser Starwheel", httpPOST, "/home_a3_sw")} />
        </div>
      </div>
    </>
  );
}

export default M1A;
