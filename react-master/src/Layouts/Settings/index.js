import React from "react";
import { useState, useEffect } from "react";
import "../../Assets/Styles/styles.css";
import { useDict, Dicts } from "../../Middleware/get-api.js";
import { DEFAULT_MSG } from "../../Utils/Utils.js";
import { Subinfo, HorizontalLine } from "../../Components/index.js";

function Settings() {
  const [S3_trayOffset, setS3_trayOffset] = useState(DEFAULT_MSG);
  const [S3_dockHeight, setS3_dockHeight] = useState(DEFAULT_MSG);
  const [P2_trayOffset, setP2_trayOffset] = useState(DEFAULT_MSG);
  const [P1_reciprocate, setP1_reciprocate] = useState(null);

  /* ---------------------------------------------------------------------------------- */
  const dictData = useDict(Dicts.settings);

  useEffect(() => {
    if (dictData) {
      setS3_trayOffset(`${dictData["S3_SHUTTLE_Z"]["tray_offset"]} mm`);
      setS3_dockHeight(`${dictData["S3_SHUTTLE_Z"]["dock_height"]} mm`);
      setP1_reciprocate(dictData["P1_PUSHER_X"]["reciprocate"]);
      setP2_trayOffset(`${dictData["P2_PUSHER_Z"]["tray_offset"]} mm`);
    } else {
      setS3_trayOffset(DEFAULT_MSG);
      setS3_dockHeight(DEFAULT_MSG);
      setP1_reciprocate(DEFAULT_MSG);
      setP2_trayOffset(DEFAULT_MSG);
    }
  }, [dictData]);

  /* ---------------------------------------------------------------------------------- */

  function getReciprocateEmoji(reciprocate) {
    switch (reciprocate) {
      case 0:
        return "✔️";
      case 1:
        return "❌";
      default:
        return DEFAULT_MSG;
    }
  }

  return (
    <>
      <div className="subcontent-container">
        🔧 Settings
        <HorizontalLine />
        <Subinfo title={"Shuttle-Z Tray Offset"} content={S3_trayOffset} />
        <Subinfo title={"Shuttle-Z Dock Height"} content={S3_dockHeight} />
        <Subinfo title={"Pusher-Z Tray Offset"} content={P2_trayOffset} />
        <Subinfo title={"Pusher-X Reciprocate"} content={getReciprocateEmoji(P1_reciprocate)} />
      </div>
    </>
  );
}

export default Settings;
