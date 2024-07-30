import React from "react";
import { useState, useEffect } from "react";
import "../../Assets/Styles/styles.css";
import { useDict, Dicts } from "../../Middleware/get-api.js";
import { getColor, httpPOST, exec, DEFAULT_MSG } from "../../Utils/Utils.js";
import { Info, Button, HorizontalLine, DebugContent, TextInput } from "../../Components/index.js";

function ActuatorStatus() {
  const numRows = 2;
  const width = `${100 / numRows}%`;

  const [m1, setM1] = useState(DEFAULT_MSG);
  const [s1, setS1] = useState(DEFAULT_MSG);
  const [s2, setS2] = useState(DEFAULT_MSG);
  const [s3, setS3] = useState(DEFAULT_MSG);
  const [s4, setS4] = useState(DEFAULT_MSG);
  const [s5, setS5] = useState(DEFAULT_MSG);
  const [s6, setS6] = useState(DEFAULT_MSG);
  const [p1, setP1] = useState(DEFAULT_MSG);
  const [p2, setP2] = useState(DEFAULT_MSG);

  const [shuttleZlevel, setShuttleZlevel] = useState(63);

  const handleShuttleZlevel = (event) => {
    setShuttleZlevel(event.target.value);
  };

  const [pusherZlevel, setPusherZlevel] = useState(63);

  const handlePusherZlevel = (event) => {
    setPusherZlevel(event.target.value);
  };

  /* ---------------------------------------------------------------------------------- */
  const dictData = useDict(Dicts.actuators);

  useEffect(() => {
    if (dictData) {
      setM1(dictData["M1_CALLIBRATION_BAR"]["status"] || DEFAULT_MSG);
      setS1(dictData["S1_SHUTTLE_X"]["status"] || DEFAULT_MSG);
      setS2(dictData["S2_SHUTTLE_Y"]["status"] || DEFAULT_MSG);
      setS3(dictData["S3_SHUTTLE_Z"]["status"] || DEFAULT_MSG);
      setS4(dictData["S4_SHUTTLE_GATE"]["status"] || DEFAULT_MSG);
      setS5(dictData["S5_LOADER_ARM"]["status"] || DEFAULT_MSG);
      setS6(dictData["S6_LOCK_PIN"]["status"] || DEFAULT_MSG);
      setP1(dictData["P1_PUSHER_X"]["status"] || DEFAULT_MSG);
      setP2(dictData["P2_PUSHER_Z"]["status"] || DEFAULT_MSG);
    } else {
      setM1(DEFAULT_MSG);
      setS1(DEFAULT_MSG);
      setS2(DEFAULT_MSG);
      setS3(DEFAULT_MSG);
      setS4(DEFAULT_MSG);
      setS5(DEFAULT_MSG);
      setS6(DEFAULT_MSG);
      setP1(DEFAULT_MSG);
      setP2(DEFAULT_MSG);
    }
  }, [dictData]);
  /* ---------------------------------------------------------------------------------- */

  function getStatusText(status) {
    switch (status) {
      case "start":
        return "RUNNING";
      case "complete":
        return "IDLE";
      case "null":
        return "IDLE";
      case "fault":
        return "FAULT";
      default:
        return DEFAULT_MSG;
    }
  }

  function getStatusColor(status) {
    switch (status) {
      case "start":
        return getColor("GREEN");
      case "complete":
        return getColor("YELLOW");
      case "null":
        return getColor("YELLOW");
      case "fault":
        return getColor("RED");
      default:
        return getColor("GREY");
    }
  }

  /* ================================= Debug elements ================================= */
  const shuttleZ_1 = (
    <Button
      name="HOME"
      onclick={() => exec("Shuttle-Z Home", httpPOST, "/move_actuator/S3_SHUTTLE_Z/ACT_S3__init__UNLOAD_POS/null")}
    />
  );

  const shuttleZ_2 = (
    <Button
      name="GOTO DOCK"
      onclick={() => exec("Shuttle-Z Goto Dock", httpPOST, "/move_actuator/S3_SHUTTLE_Z/ACT_S3__move__UNLOAD_POS/null")}
    />
  );

  const shuttleZ_3 = (
    <Button
      name="GOTO TRAY"
      onclick={() =>
        exec(
          `Shuttle-Z Goto Level ${shuttleZlevel}`,
          httpPOST,
          `/move_actuator/S3_SHUTTLE_Z/ACT_S3__move__LOAD_LEVEL_POS/${shuttleZlevel}`
        )
      }
    />
  );

  const shuttleZ_levelTextBox = (
    <TextInput value={shuttleZlevel} onChange={handleShuttleZlevel} placeholder={shuttleZlevel} />
  );

  const shuttleY_1 = (
    <Button
      name="HOME"
      onclick={() => exec("Shuttle-Y Home", httpPOST, "/move_actuator/S2_SHUTTLE_Y/ACT_S2__init__LOAD_POS/null")}
    />
  );
  const shuttleY_2 = (
    <Button
      name="ENGAGE TRAY"
      onclick={() => exec("Shuttle-Y Goto Tray", httpPOST, "/move_actuator/S2_SHUTTLE_Y/ACT_S2__move__LOAD_POS/null")}
    />
  );
  const shuttleY_3 = (
    <Button
      name="DISENGAGE TRAY"
      onclick={() => exec("Shuttle-Y Goto Dock", httpPOST, "/move_actuator/S2_SHUTTLE_Y/ACT_S2__move__UNLOAD_POS/null")}
    />
  );

  const shuttleX_1 = (
    <Button
      name="HOME"
      onclick={() => exec("Shuttle-X Home", httpPOST, "/move_actuator/S1_SHUTTLE_X/ACT_S1__init__UNLOAD_POS/null")}
    />
  );
  const shuttleX_2 = (
    <Button
      name="ENGAGE TRAY"
      onclick={() => exec("Shuttle-X Goto Tray", httpPOST, "/move_actuator/S1_SHUTTLE_X/ACT_S1__move__LOAD_POS/null")}
    />
  );
  const shuttleX_3 = (
    <Button
      name="DISENGAGE TRAY"
      onclick={() => exec("Shuttle-X Goto Dock", httpPOST, "/move_actuator/S1_SHUTTLE_X/ACT_S1__move__UNLOAD_POS/null")}
    />
  );

  const shuttleGate_1 = (
    <Button
      name="HOME"
      onclick={() =>
        exec("Shuttle-Gate Home", httpPOST, "/move_actuator/S4_SHUTTLE_GATE/ACT_S4__init__UNLOAD_POS/null")
      }
    />
  );
  const shuttleGate_2 = (
    <Button
      name="OPEN TRAY-SIDE"
      onclick={() =>
        exec("Shuttle-Gate Open Tray Side", httpPOST, "/move_actuator/S4_SHUTTLE_GATE/ACT_S4__move__LOAD_POS/null")
      }
    />
  );
  const shuttleGate_3 = (
    <Button
      name="OPEN DOCK-SIDE"
      onclick={() =>
        exec("Shuttle-Gate Open Dock Side", httpPOST, "/move_actuator/S4_SHUTTLE_GATE/ACT_S4__move__UNLOAD_POS/null")
      }
    />
  );

  const shuttleArm_1 = (
    <Button
      name="HOME"
      onclick={() => exec("Shuttle-Arm Home", httpPOST, "/move_actuator/S5_LOADER_ARM/ACT_S5__init__LOAD_POS/null")}
    />
  );
  const shuttleArm_2 = (
    <Button
      name="PUSH"
      onclick={() => exec("Shuttle-Arm Push", httpPOST, "/move_actuator/S5_LOADER_ARM/ACT_S5__move__UNLOAD_POS/null")}
    />
  );
  const shuttleArm_3 = (
    <Button
      name="RETRACT"
      onclick={() => exec("Shuttle-Arm Retract", httpPOST, "/move_actuator/S5_LOADER_ARM/ACT_S5__move__LOAD_POS/null")}
    />
  );

  const shuttleLockPin_1 = (
    <Button
      name="HOME"
      onclick={() => exec("Shuttle-LockPin Home", httpPOST, "/move_actuator/S6_LOCK_PIN/ACT_S6__init__UNLOCK/null")}
    />
  );
  const shuttleLockPin_2 = (
    <Button
      name="LOCK"
      onclick={() => exec("Shuttle-LockPin Lock", httpPOST, "/move_actuator/S6_LOCK_PIN/ACT_S6__move__LOCK/null")}
    />
  );
  const shuttleLockPin_3 = (
    <Button
      name="UNLOCK"
      onclick={() => exec("Shuttle-LockPin Unlock", httpPOST, "/move_actuator/S6_LOCK_PIN/ACT_S6__move__UNLOCK/null")}
    />
  );

  /* ---------------------------------------------------------------------------------- */
  const callibrationBar_1 = (
    <Button
      name="HOME"
      onclick={() => exec("Callibration Bar Home", httpPOST, "/move_actuator/M1_CALLIBRATION_BAR/ACT_M1__init/null")}
    />
  );
  const callibrationBar_2 = (
    <Button
      name="CALLIBRATE TROLLEY"
      onclick={() =>
        exec(
          "Callibration Bar Callibrate",
          httpPOST,
          "/move_actuator/M1_CALLIBRATION_BAR/ACT_M1__move__CALLIBRATE_OFFSET/null"
        )
      }
    />
  );

  const pusherZ_1 = (
    <Button
      name="HOME"
      onclick={() => exec("Pusher-Z Home", httpPOST, "/move_actuator/P2_PUSHER_Z/ACT_P2__init__TOP_LIMIT/null")}
    />
  );

  const pusherZ_2 = (
    <Button
      name="UP A BIT"
      onclick={() => exec("Pusher-Z Goto Dock", httpPOST, "/move_actuator/P2_PUSHER_Z/ACT_P2__move__UP_ABIT/null")}
    />
  );

  const pusherZ_3 = (
    <Button
      name="DOWN A BIT"
      onclick={() => exec("Pusher-Z Goto Dock", httpPOST, "/move_actuator/P2_PUSHER_Z/ACT_P2__move__DOWN_ABIT/null")}
    />
  );

  const pusherZ_4 = (
    <Button
      name="GOTO TRAY"
      onclick={() =>
        exec(
          `Pusher-Z Goto Level ${pusherZlevel}`,
          httpPOST,
          `/move_actuator/P2_PUSHER_Z/ACT_P2__move__TO_LEVEL/${pusherZlevel}`
        )
      }
    />
  );

  const pusherZ_levelTextBox = (
    <TextInput value={pusherZlevel} onChange={handlePusherZlevel} placeholder={pusherZlevel} />
  );

  const pusherX_1 = (
    <Button
      name="HOME"
      onclick={() => exec("Pusher-X Home", httpPOST, "/move_actuator/P1_PUSHER_X/ACT_P1__init__UNLOAD_POS_2/null")}
    />
  );

  const pusherX_2 = (
    <Button
      name="LEAVE TRAY"
      onclick={() =>
        exec("Pusher-X Leave Tray", httpPOST, "/move_actuator/P1_PUSHER_X/ACT_P1__move__UNLOAD_POS_2/null")
      }
    />
  );

  const pusherX_3 = (
    <Button
      name="MIDPOINT"
      onclick={() => exec("Pusher-X Midpoint", httpPOST, "/move_actuator/P1_PUSHER_X/ACT_P1__move__LOAD_POS_1/null")}
    />
  );

  const pusherX_4 = (
    <Button
      name="PUSH CAPSULES"
      onclick={() => exec("Pusher-X Push", httpPOST, "/move_actuator/P1_PUSHER_X/ACT_P1__move__LOAD_POS_2/null")}
    />
  );

  return (
    <div className="row-container">
      <div className="nested-columns-container" style={{ width }}>
        <div className="subcontent-container">
          Shuttle
          <HorizontalLine />
          ▶ X
          <Info text={getStatusText(s1)} color={getStatusColor(s1)} />
          <DebugContent elements={[shuttleX_1, shuttleX_2, shuttleX_3]} />
          ▶ Y
          <Info text={getStatusText(s2)} color={getStatusColor(s2)} />
          <DebugContent elements={[shuttleY_1, shuttleY_2, shuttleY_3]} />
          ▶ Z
          <Info text={getStatusText(s3)} color={getStatusColor(s3)} />
          <DebugContent elements={[shuttleZ_1, shuttleZ_2, shuttleZ_3, shuttleZ_levelTextBox]} />
          ▶ Gate
          <Info text={getStatusText(s4)} color={getStatusColor(s4)} />
          <DebugContent elements={[shuttleGate_1, shuttleGate_2, shuttleGate_3]} />
          ▶ Arm
          <Info text={getStatusText(s5)} color={getStatusColor(s5)} />
          <DebugContent elements={[shuttleArm_1, shuttleArm_2, shuttleArm_3]} />
          ▶ Lock Pin
          <Info text={getStatusText(s6)} color={getStatusColor(s6)} />
          <DebugContent elements={[shuttleLockPin_1, shuttleLockPin_2, shuttleLockPin_3]} />
        </div>
      </div>
      <div className="nested-columns-container" style={{ width }}>
        <div className="subcontent-container">
          Others
          <HorizontalLine />
          ▶ Callibration Bar
          <Info text={getStatusText(m1)} color={getStatusColor(m1)} />
          <DebugContent elements={[callibrationBar_1, callibrationBar_2]} />
          ▶ Pusher-Z
          <Info text={getStatusText(p1)} color={getStatusColor(p1)} />
          <DebugContent elements={[pusherZ_1, pusherZ_2, pusherZ_3, pusherZ_4, pusherZ_levelTextBox]} />
          ▶ Pusher-X
          <Info text={getStatusText(p2)} color={getStatusColor(p2)} />
          <DebugContent elements={[pusherX_1, pusherX_2, pusherX_3, pusherX_4]} />
        </div>
      </div>
    </div>
  );
}
export default ActuatorStatus;
