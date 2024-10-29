import React from "react";
import { useState, useEffect } from "react";
import "../../Assets/Styles/styles.css";
import { useDict, Dicts } from "../../Middleware/get-api.js";
import { getColor, DEFAULT_MSG } from "../../Utils/Utils.js";
import { Gap, HorizontalLine, SubcontentTitle, InfoSameRow } from "../../Components/index.js";

function CageLoadingBar({ title, cageExperimentDict }) {
  function getOperationMode(operationIndex) {
    switch (operationIndex) {
      case 0:
        return "Ai";
      case 1:
        return "Ai";
      case 2:
        return "Ai";
      case 3:
        return "Ai";
      case 4:
        return "Purge";
      default:
        return "n/a";
    }
  }

  function getBarOpacity(operationIndex) {
    switch (operationIndex) {
      case 0:
        return 0.2;
      case 1:
        return 0.4;
      case 2:
        return 0.6;
      case 3:
        return 0.8;
      case 4:
        return 1;
      default:
        return 0;
    }
  }

  // Read dict
  let operationIndex = null;
  let slots = null;
  let maxSlots = null;
  let timeElapsed = null;
  let timeInterval = null;

  if (cageExperimentDict) {
    operationIndex = cageExperimentDict["operation_index"];
    slots = cageExperimentDict["slots"];
    maxSlots = cageExperimentDict["max_slots"];
    timeElapsed = cageExperimentDict["time_elapsed"];
    timeInterval = cageExperimentDict["time_interval"];
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
              <span className="loading-text">{currentMode}</span>
            </div>
          </div>
          <Gap height={5} />
        </div>
      </div>
    </>
  );
}

function CageStatusBar({ row, dictExperiment }) {
  const [c1ExperimentDict, setC1ExperimentDict] = useState(null);
  const [c2ExperimentDict, setC2ExperimentDict] = useState(null);
  const [c3ExperimentDict, setC3ExperimentDict] = useState(null);
  const [c4ExperimentDict, setC4ExperimentDict] = useState(null);
  const [c5ExperimentDict, setC5ExperimentDict] = useState(null);
  const [c6ExperimentDict, setC6ExperimentDict] = useState(null);
  const [c7ExperimentDict, setC7ExperimentDict] = useState(null);
  const [c8ExperimentDict, setC8ExperimentDict] = useState(null);
  const [c9ExperimentDict, setC9ExperimentDict] = useState(null);
  const [c10ExperimentDict, setC10ExperimentDict] = useState(null);
  const [c11ExperimentDict, setC11ExperimentDict] = useState(null);
  const [c12ExperimentDict, setC12ExperimentDict] = useState(null);
  const [c13ExperimentDict, setC13ExperimentDict] = useState(null);
  const [c14ExperimentDict, setC14ExperimentDict] = useState(null);

  /* ---------------------------------------------------------------------------------- */
  useEffect(() => {
    if (dictExperiment) {
      try {
        setC1ExperimentDict(dictExperiment[`cage${row - 1}x0001`] || null);
        setC2ExperimentDict(dictExperiment[`cage${row - 1}x0002`] || null);
        setC3ExperimentDict(dictExperiment[`cage${row - 1}x0003`] || null);
        setC4ExperimentDict(dictExperiment[`cage${row - 1}x0004`] || null);
        setC5ExperimentDict(dictExperiment[`cage${row - 1}x0005`] || null);
        setC6ExperimentDict(dictExperiment[`cage${row - 1}x0006`] || null);
        setC7ExperimentDict(dictExperiment[`cage${row - 1}x0007`] || null);
        setC8ExperimentDict(dictExperiment[`cage${row - 1}x0008`] || null);
        setC9ExperimentDict(dictExperiment[`cage${row - 1}x0009`] || null);
        setC10ExperimentDict(dictExperiment[`cage${row - 1}x0010`] || null);
        setC11ExperimentDict(dictExperiment[`cage${row - 1}x0011`] || null);
        setC12ExperimentDict(dictExperiment[`cage${row - 1}x0012`] || null);
        setC13ExperimentDict(dictExperiment[`cage${row - 1}x0013`] || null);
        setC14ExperimentDict(dictExperiment[`cage${row - 1}x0014`] || null);
      } catch {
        setC1ExperimentDict(null);
        setC2ExperimentDict(null);
        setC3ExperimentDict(null);
        setC4ExperimentDict(null);
        setC5ExperimentDict(null);
        setC6ExperimentDict(null);
        setC7ExperimentDict(null);
        setC8ExperimentDict(null);
        setC9ExperimentDict(null);
        setC10ExperimentDict(null);
        setC11ExperimentDict(null);
        setC12ExperimentDict(null);
        setC13ExperimentDict(null);
        setC14ExperimentDict(null);
      }
    } else {
      setC1ExperimentDict(null);
      setC2ExperimentDict(null);
      setC3ExperimentDict(null);
      setC4ExperimentDict(null);
      setC5ExperimentDict(null);
      setC6ExperimentDict(null);
      setC7ExperimentDict(null);
      setC8ExperimentDict(null);
      setC9ExperimentDict(null);
      setC10ExperimentDict(null);
      setC11ExperimentDict(null);
      setC12ExperimentDict(null);
      setC13ExperimentDict(null);
      setC14ExperimentDict(null);
    }
  }, [row, dictExperiment]);

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
