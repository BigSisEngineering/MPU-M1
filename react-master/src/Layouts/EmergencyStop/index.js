import React from "react";
import "../../Assets/Styles/styles.css";
import { httpPOST, exec } from "../../Utils/Utils.js";

function EmergencyStop() {
  return (
    <div className="buttons-container">
      <button className="emergency-button" onClick={() => exec("EMERGENCY STOP", httpPOST, "/emergency_stop")}></button>
    </div>
  );
}

export default EmergencyStop;
