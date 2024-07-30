import React from "react";
import { useState, useEffect } from "react";
import "../../Assets/Styles/styles.css";
import { useDict, Dicts } from "../../Middleware/get-api.js";
import { DEFAULT_MSG } from "../../Utils/Utils.js";
import { Subinfo, HorizontalLine } from "../../Components/index.js";

function ControlPanel() {
  const [temperature, setTemperature] = useState(DEFAULT_MSG);
  const [humidity, setHumidity] = useState(DEFAULT_MSG);
  const [fan, setFan] = useState(DEFAULT_MSG);

  /* ---------------------------------------------------------------------------------- */
  const dictInputs = useDict(Dicts.inputs);
  const dictOutputs = useDict(Dicts.outputs);

  useEffect(() => {
    if (dictInputs) {
      setTemperature(`${dictInputs["temp_sensor_controlpanel"]["temperature"]} °C`);
      setHumidity(`${dictInputs["temp_sensor_controlpanel"]["humidity"]} %`);
    } else {
      setTemperature(DEFAULT_MSG);
      setHumidity(DEFAULT_MSG);
    }
  }, [dictInputs]);
  useEffect(() => {
    if (dictOutputs) {
      setFan(dictOutputs["fan_controlpanel"]["status"]);
    } else {
      setFan(DEFAULT_MSG);
    }
  }, [dictOutputs]);
  /* ---------------------------------------------------------------------------------- */

  return (
    <>
      <div className="subcontent-container">
        🌡 Control Panel
        <HorizontalLine />
        <Subinfo title={"Temperature"} content={temperature} />
        <Subinfo title={"Humidity"} content={humidity} />
        <Subinfo title={"Fan"} content={fan} />
      </div>
    </>
  );
}
export default ControlPanel;
