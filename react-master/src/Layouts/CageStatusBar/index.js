import React from "react";
import "../../Assets/Styles/styles.css";
import { useDict, Dicts } from "../../Middleware/get-api.js";
import { Gap, HorizontalLine, SubcontentTitle } from "../../Components/index.js";

function CageLoadingBar({ title, cageExperimentDict }) {
  // Read dict
  let operationIndex = null;
  let slots = null;
  let maxSlots = null;
  let timeElapsed = null;
  let timeInterval = null;
  let sequenceNumber = null;
  let purgeFrequency = null;

  if (cageExperimentDict) {
    operationIndex = cageExperimentDict["operation_index"];
    slots = cageExperimentDict["slots"];
    maxSlots = cageExperimentDict["max_slots"];
    timeElapsed = cageExperimentDict["time_elapsed"];
    timeInterval = cageExperimentDict["sequence_duration"];
    sequenceNumber = cageExperimentDict["sequence_number"];
    purgeFrequency = cageExperimentDict["purge_frequency"] || 5; // if running on old code
  }

  function getOperationMode(operationIndex) {
    if (purgeFrequency) {
      return operationIndex === purgeFrequency - 1 ? "Purge" : "Ai";
    }
    return "n/a";
  }

  function getBarOpacity(operationIndex) {
    if (purgeFrequency) {
      return (0.1 + (operationIndex / (purgeFrequency - 1)) * 0.9).toFixed(2);
    }
    return 0;
  }

  // Text
  const slotBarWidth = maxSlots ? (slots / maxSlots) * 100 : 0;
  const timeBarWidth = timeInterval ? (timeElapsed / timeInterval) * 100 : 0;
  const currentMode = getOperationMode(operationIndex);
  const barOpacity = getBarOpacity(operationIndex);

  return (
    <>
      <div className="subcontent-info-same-row-container">
        <div className="character-container">{title}</div>
        <div className="subcontent-same_column-container">
          <Gap height={3} />
          {/*SLOTS*/}
          <div className="loading-bar-container">
            <div
              className="loading-bar"
              style={{ width: `${slotBarWidth}%`, backgroundColor: "rgba(50, 245, 39, 0.8)" }}
            >
              <span className="loading-text">
                {slots}/{maxSlots}
              </span>
            </div>
          </div>
          <Gap height={2} />
          {/*TIME*/}
          <div className="loading-bar-container">
            <div
              className="loading-bar"
              style={{ width: `${timeBarWidth}%`, backgroundColor: `rgba(245, 148, 39, ${barOpacity})` }}
            >
              <span className="loading-text">{`${currentMode}-(${sequenceNumber})`}</span>
            </div>
          </div>
          <Gap height={5} />
        </div>
      </div>
    </>
  );
}

function CageStatusBar() {
  /* =================================== Fetch Data =================================== */
  const dictExperiment = useDict(Dicts.experiment);
  const dictInfo = useDict(Dicts.info);
  const row = dictInfo ? dictInfo.row : 1;

  let c1ExperimentDict = null;
  let c2ExperimentDict = null;
  let c3ExperimentDict = null;
  let c4ExperimentDict = null;
  let c5ExperimentDict = null;
  let c6ExperimentDict = null;
  let c7ExperimentDict = null;
  let c8ExperimentDict = null;
  let c9ExperimentDict = null;
  let c10ExperimentDict = null;
  let c11ExperimentDict = null;
  let c12ExperimentDict = null;
  let c13ExperimentDict = null;
  let c14ExperimentDict = null;

  /* ---------------------------------------------------------------------------------- */
  if (dictExperiment) {
    c1ExperimentDict = dictExperiment[`cage${row - 1}x0001`];
    c2ExperimentDict = dictExperiment[`cage${row - 1}x0002`];
    c3ExperimentDict = dictExperiment[`cage${row - 1}x0003`];
    c4ExperimentDict = dictExperiment[`cage${row - 1}x0004`];
    c5ExperimentDict = dictExperiment[`cage${row - 1}x0005`];
    c6ExperimentDict = dictExperiment[`cage${row - 1}x0006`];
    c7ExperimentDict = dictExperiment[`cage${row - 1}x0007`];
    c8ExperimentDict = dictExperiment[`cage${row - 1}x0008`];
    c9ExperimentDict = dictExperiment[`cage${row - 1}x0009`];
    c10ExperimentDict = dictExperiment[`cage${row - 1}x0010`];
    c11ExperimentDict = dictExperiment[`cage${row - 1}x0011`];
    c12ExperimentDict = dictExperiment[`cage${row - 1}x0012`];
    c13ExperimentDict = dictExperiment[`cage${row - 1}x0013`];
    c14ExperimentDict = dictExperiment[`cage${row - 1}x0014`];
  }
  /* ---------------------------------------------------------------------------------- */

  return (
    <>
      <div
        className="subcontent-container"
        style={{
          fontSize: "16px",
          letterSpacing: "0.05em",
        }}
      >
        <SubcontentTitle text={"Experiment Mode Status"} />
        <HorizontalLine />
        <CageLoadingBar title="Cage1 " cageExperimentDict={c1ExperimentDict} />
        <CageLoadingBar title="Cage2 " cageExperimentDict={c2ExperimentDict} />
        <CageLoadingBar title="Cage3 " cageExperimentDict={c3ExperimentDict} />
        <CageLoadingBar title="Cage4 " cageExperimentDict={c4ExperimentDict} />
        <CageLoadingBar title="Cage5 " cageExperimentDict={c5ExperimentDict} />
        <CageLoadingBar title="Cage6 " cageExperimentDict={c6ExperimentDict} />
        <CageLoadingBar title="Cage7 " cageExperimentDict={c7ExperimentDict} />
        <CageLoadingBar title="Cage8 " cageExperimentDict={c8ExperimentDict} />
        <CageLoadingBar title="Cage9 " cageExperimentDict={c9ExperimentDict} />
        <CageLoadingBar title="Cage10" cageExperimentDict={c10ExperimentDict} />
        <CageLoadingBar title="Cage11" cageExperimentDict={c11ExperimentDict} />
        <CageLoadingBar title="Cage12" cageExperimentDict={c12ExperimentDict} />
        <CageLoadingBar title="Cage13" cageExperimentDict={c13ExperimentDict} />
        <CageLoadingBar title="Cage14" cageExperimentDict={c14ExperimentDict} />
      </div>
    </>
  );
}

export default CageStatusBar;
