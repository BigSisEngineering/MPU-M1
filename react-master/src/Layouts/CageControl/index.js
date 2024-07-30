import React from "react";
import "../../Assets/Styles/styles.css";
import { httpPOST, exec } from "../../Utils/Utils.js";
import { Button, HorizontalLine, Gap, SubcontentTitle } from "../../Components/index.js";

function CageControl(selectAll, clearAll) {
  return (
    <>
      {" "}
      <div
        className="subcontent-container"
        style={{
          backgroundColor: "rgba(175, 161, 122, 0.4)",
          border: "3px solid rgba(255, 255, 206, 0.7)",
          fontWeight: "bold",
          fontSize: "16px",
          letterSpacing: "0.05em",
          width: "50%",
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
          <Button name="Start PNP" onclick={() => exec("START", httpPOST, "/cmd_start")} />
          <Button name="Stop PNP" onclick={() => exec("STOP", httpPOST, "/cmd_stop")} />
          <Button name="Start Dummy" onclick={() => exec("STOP", httpPOST, "/cmd_stop")} />
          <Button name="Stop Dummy" onclick={() => exec("STOP", httpPOST, "/cmd_stop")} />
          <Button name="Servo Init" onclick={() => exec("STOP", httpPOST, "/cmd_stop")} />
        </div>
        (*Note: Affects selected cages only)
      </div>
    </>
  );
}
export default CageControl;
