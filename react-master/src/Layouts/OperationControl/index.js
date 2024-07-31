import React from "react";
import "../../Assets/Styles/styles.css";
import { httpPOST, exec } from "../../Utils/Utils.js";
import { Button, HorizontalLine, Gap, SubcontentTitle } from "../../Components/index.js";

function OperationControl() {
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
        }}
      >
        {" "}
        <SubcontentTitle text={"⚙ OPERATION CONTROL"} />
        <HorizontalLine />
        <Gap />
        1A
        <HorizontalLine />
        <div className="buttons-container">
          <Button name="Start" onclick={() => exec("START", httpPOST, "/start_1a")} />
          <Button name="Stop" onclick={() => exec("STOP", httpPOST, "/stop_1a")} />
          <Button name="Add 10 Pots" onclick={() => exec("STOP", httpPOST, "/add_pots")} />
        </div>
        <Gap />
        1C
        <HorizontalLine />
        <div className="buttons-container">
          <Button name="Start" onclick={() => exec("START", httpPOST, "/start_1c")} />
          <Button name="Stop" onclick={() => exec("STOP", httpPOST, "/stop_1c")} />
        </div>
        <Gap />
      </div>
    </>
  );
}
export default OperationControl;
