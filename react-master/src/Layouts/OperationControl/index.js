import React from "react";
import "../../Assets/Styles/styles.css";
import { httpPOST, exec, getColor } from "../../Utils/Utils.js";
import { Button, HorizontalLine, Gap, SubcontentTitle, InfoSameRow } from "../../Components/index.js";

function OperationControl({ m1aRunning, m1cRunning }) {
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
        <InfoSameRow
          title="1A"
          text={m1aRunning ? "RUNNING" : "STOPPED"}
          color={m1aRunning ? getColor("GREEN") : getColor("BLUE")}
        />
        <HorizontalLine />
        <div className="buttons-container">
          <Button
            name="Start"
            onclick={() => exec("START 1A", httpPOST, "/start_1a")}
            disable={m1aRunning ? true : false}
          />
          <Button
            name="Stop"
            onclick={() => exec("STOP 1A", httpPOST, "/stop_1a")}
            disable={m1aRunning ? false : true}
          />
          <Button
            name="+10 Pots"
            onclick={() => exec("+10 Pots", httpPOST, "/add_pots")}
            disable={m1aRunning ? false : true}
          />
          <Button
            name="Set Zero"
            onclick={() => exec("Set Zero", httpPOST, "/set_zero")}
            disable={m1aRunning ? false : true}
          />
        </div>
        <Gap />
        <InfoSameRow
          title="1C"
          text={m1cRunning ? "RUNNING" : "STOPPED"}
          color={m1cRunning ? getColor("GREEN") : getColor("BLUE")}
        />
        <HorizontalLine />
        <div className="buttons-container">
          <Button
            name="Start"
            onclick={() => exec("START 1C", httpPOST, "/start_1c")}
            disable={m1cRunning ? true : false}
          />
          <Button
            name="Stop"
            onclick={() => exec("STOP 1C", httpPOST, "/stop_1c")}
            disable={m1cRunning ? false : true}
          />
        </div>
        <Gap />
      </div>
    </>
  );
}
export default OperationControl;
