import React from "react";
import { useState } from "react";
import "../../Assets/Styles/styles.css";
import { httpPOST, exec } from "../../Utils/Utils.js";
import { Button, HorizontalLine, Gap, SubcontentTitle, TextInput } from "../../Components/index.js";

class CageActions {
  static sw_init = "STAR_WHEEL_INIT";
  static ul_init = "UNLOADER_INIT";
  static servo_init = "ALL_SERVOS_INIT";
  static sw_clear_error = "CLEAR_STAR_WHEEL_ERROR";
  static ul_clear_error = "CLEAR_UNLOADER_ERROR";
  static dummy_start = "ENABLE_DUMMY";
  static dummy_stop = "DISABLE_DUMMY";
  static pnp_start = "ENABLE_PNP";
  static pnp_stop = "DISABLE_PNP";
  static sw_move_fwd = "MOVE_CW";
  static sw_move_bwd = "MOVE_CCW";
  static experiment_start = "ENABLE_EXPERIMENT";
  static experiment_stop = "DISABLE_EXPERIMENT";
  static experiment_set_pause_interval = "SET_PAUSE_INTERVAL";
}

function CageControl({ selectAll, clearAll, isSelectedArray, isCageActionMode, setIsCageActionMode }) {
  function getSelectedCages() {
    let selectedCages = "";

    isSelectedArray.forEach((isSelected, index) => {
      if (isSelected) {
        if (selectedCages === "") {
          selectedCages = `Cage ${index + 1}`;
        } else {
          selectedCages = selectedCages + `, ${index + 1}`;
        }
      }
    });

    if (selectedCages === "") {
      return "nothing";
    } else {
      return selectedCages;
    }
  }

  function createPOSTBody(action, data = {}) {
    const dict = { action: action, bool_list: isSelectedArray };
    const result = { ...dict, ...data };
    return result;
  }

  const [pauseInterval, setPauseInterval] = useState(null);

  const handlePauseInterval = (event) => {
    setPauseInterval(event.target.value);
  };

  async function execFunction(func, ...args) {
    await func(...args);
    clearAll();
  }

  return (
    <>
      {" "}
      <div
        className="subcontent-container"
        style={{
          backgroundColor: "rgba(138, 240, 154, 0.2)",
          border: "3px solid rgba(255, 255, 206, 0.7)",
          fontWeight: "bold",
          fontSize: "16px",
          letterSpacing: "0.05em",
          width: "100%",
        }}
      >
        {" "}
        <SubcontentTitle text={"⚙ CAGE CONTROL"} />
        <Gap />
        Utility
        <HorizontalLine />
        <div className="buttons-container">
          <Button name="Select All" onclick={selectAll} />
          <Button name="Clear All" onclick={clearAll} />
          <Button
            name={isCageActionMode ? "Sensor View" : "Action View"}
            onclick={() => setIsCageActionMode(!isCageActionMode)}
          />
        </div>
        <Gap />
        Operation
        <HorizontalLine />
        <div className="buttons-container">
          <Button
            name="Start PNP"
            onclick={() =>
              execFunction(
                exec,
                `Start PNP on ${getSelectedCages()}`,
                httpPOST,
                "/operate_cage",
                createPOSTBody(CageActions.pnp_start)
              )
            }
          />
          <Button
            name="Stop PNP"
            onclick={() =>
              execFunction(
                exec,
                `Stop PNP on ${getSelectedCages()}`,
                httpPOST,
                "/operate_cage",
                createPOSTBody(CageActions.pnp_stop)
              )
            }
          />
          <Button
            name="Start Dummy"
            onclick={() =>
              execFunction(
                exec,
                `Start DUMMY on ${getSelectedCages()}`,
                httpPOST,
                "/operate_cage",
                createPOSTBody(CageActions.dummy_start)
              )
            }
          />
          <Button
            name="Stop Dummy"
            onclick={() =>
              execFunction(
                exec,
                `Stop DUMMY on ${getSelectedCages()}`,
                httpPOST,
                "/operate_cage",
                createPOSTBody(CageActions.dummy_stop)
              )
            }
          />
          <Button
            name="Servo Init"
            onclick={() =>
              execFunction(
                exec,
                `Servo Init on ${getSelectedCages()}`,
                httpPOST,
                "/operate_cage",
                createPOSTBody(CageActions.servo_init)
              )
            }
          />
        </div>
        <Gap />
        Experiment Mode
        <HorizontalLine />
        <div className="buttons-container">
          <Button
            name="Start Experiment"
            onclick={() =>
              execFunction(
                exec,
                `Start EXPERIMENT on ${getSelectedCages()}`,
                httpPOST,
                "/operate_cage",
                createPOSTBody(CageActions.experiment_start)
              )
            }
          />
          <Button
            name="Stop Experiment"
            onclick={() =>
              execFunction(
                exec,
                `Stop EXPERIMENT on ${getSelectedCages()}`,
                httpPOST,
                "/operate_cage",
                createPOSTBody(CageActions.experiment_stop)
              )
            }
          />
          <Button
            name="Set Pause Interval"
            onclick={() =>
              execFunction(
                exec,
                `Set PAUSE INTERVAL on ${getSelectedCages()}`,
                httpPOST,
                "/operate_cage",
                createPOSTBody(CageActions.experiment_set_pause_interval, { interval: pauseInterval })
              )
            }
          />
          <TextInput value={pauseInterval} onChange={handlePauseInterval} placeholder={"seconds"} />
        </div>
        <Gap />
        Maintainence
        <HorizontalLine />
        <div className="buttons-container">
          <Button
            name="Set Flag"
            onclick={() =>
              execFunction(exec, `Set Maintainence flag on ${getSelectedCages()}`, httpPOST, "/set_maintainence_flag", {
                bool_list: isSelectedArray,
                bool_val: true,
              })
            }
          />
          <Button
            name="Clear Flag"
            onclick={() =>
              execFunction(exec, `Set Maintainence flag on ${getSelectedCages()}`, httpPOST, "/set_maintainence_flag", {
                bool_list: isSelectedArray,
                bool_val: false,
              })
            }
          />
        </div>
        (*Note: Affects selected cages only)
      </div>
    </>
  );
}
export default CageControl;
