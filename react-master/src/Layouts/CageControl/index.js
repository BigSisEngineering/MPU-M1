import React from "react";
import "../../Assets/Styles/styles.css";
import { httpPOST, exec } from "../../Utils/Utils.js";
import { Button, HorizontalLine, Gap, SubcontentTitle } from "../../Components/index.js";

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
}

function CageControl({ selectAll, clearAll, isSelectedArray }) {
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

  function createPOSTBody(action) {
    const dict = { action: action, bool_list: isSelectedArray };
    console.log(dict);
    return dict;
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
        Quick Select
        <HorizontalLine />
        <div className="buttons-container">
          <Button name="Select All" onclick={selectAll} />
          <Button name="Clear All" onclick={clearAll} />
        </div>
        <Gap />
        Operation
        <HorizontalLine />
        <div className="buttons-container">
          <Button
            name="Start PNP"
            onclick={() =>
              exec(
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
              exec(`Stop PNP on ${getSelectedCages()}`, httpPOST, "/operate_cage", createPOSTBody(CageActions.pnp_stop))
            }
          />
          <Button
            name="Start Dummy"
            onclick={() =>
              exec(
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
              exec(
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
              exec(
                `Servo Init on ${getSelectedCages()}`,
                httpPOST,
                "/operate_cage",
                createPOSTBody(CageActions.servo_init)
              )
            }
          />
        </div>
        (*Note: Affects selected cages only)
      </div>
    </>
  );
}
export default CageControl;
