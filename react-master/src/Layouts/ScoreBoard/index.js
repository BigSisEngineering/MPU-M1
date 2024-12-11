import React from "react";
import "../../Assets/Styles/styles.css";
import { useDict, Dicts } from "../../Middleware/get-api.js";
import { Gap, HorizontalLine, Subinfo } from "../../Components/index.js";

function ScoreBoard() {
  const dictScore = useDict(Dicts.cageScore);

  let isCompletedExist = false;
  let completedNum = null;
  let completedScore = null;
  let completedSlots = null;

  let isMinExist = false;
  let minNum = null;
  let minScore = null;
  let minSlots = null;

  let isMaxExist = false;
  let maxNum = null;
  let maxScore = null;
  let maxSlots = null;

  let isBestExist = false;
  let bestNum = null;
  let bestScore = null;
  let bestSlots = null;

  if (dictScore) {
    completedNum = dictScore["completed_num"];
    completedScore = dictScore["completed_score"];
    completedSlots = dictScore["completed_slots"];
    isCompletedExist = completedNum ? true : false;

    minNum = dictScore["min_num"];
    minScore = dictScore["min_score"];
    minSlots = dictScore["min_slots"];
    isMinExist = minNum ? true : false;

    maxNum = dictScore["max_num"];
    maxScore = dictScore["max_score"];
    maxSlots = dictScore["max_slots"];
    isMaxExist = maxNum ? true : false;

    bestNum = dictScore["best_num"];
    bestScore = dictScore["best_score"];
    bestSlots = dictScore["best_slots"];
    isBestExist = bestNum ? true : false;
  }

  return (
    <>
      <div
        className="subcontent-container"
        style={{
          border: "5px solid #ccc",
          fontWeight: "bold",
          fontSize: "22px",
          backgroundColor: "rgba(255, 194, 0, 0.35)",
          overflow: "hidden",
        }}
      >
        <div
          className="subcontent-title"
          style={{
            fontStyle: "italic",
            fontSize: "24px",
            alignItems: "center",
            whiteSpace: "nowrap",
            overflow: "hidden",
          }}
        >
          - DAILY SCORE BOARD -
        </div>
        <HorizontalLine />
        <Gap />
        <div
          className="subcontent-info-box"
          style={{
            fontSize: "18px",
            marginLeft: "0px",
            background: "rgba(42, 196, 185, 0.8)",
            whiteSpace: "nowrap",
            overflow: "hidden",
          }}
        >
          BEST
        </div>
        <HorizontalLine />
        {isBestExist && (
          <div className="row-container" style={{ justifyContent: "left", alignItems: "center" }}>
            <Subinfo
              title={`#${bestNum}`}
              content={`Score: ${bestScore}% (${bestSlots}/${14 * 80})`}
              fontSize={18}
              gap={20}
            />
          </div>
        )}
        {!isBestExist && (
          <div className="row-container" style={{ justifyContent: "left" }}>
            <Subinfo title={"No data"} fontSize={18} />
          </div>
        )}
        <Gap height={15} />
        <div
          className="subcontent-info-box"
          style={{
            fontSize: "18px",
            marginLeft: "0px",
            background: "rgba(42, 196, 185, 0.8)",
            whiteSpace: "nowrap",
            overflow: "hidden",
          }}
        >
          LAST COMPLETED
        </div>
        <HorizontalLine />
        {isCompletedExist && (
          <div className="row-container" style={{ justifyContent: "left" }}>
            <Subinfo
              title={`#${completedNum}`}
              content={`Score: ${completedScore}% (${completedSlots}/${14 * 80})`}
              fontSize={18}
              gap={20}
            />
          </div>
        )}
        {!isCompletedExist && (
          <div className="row-container" style={{ justifyContent: "left" }}>
            <Subinfo title={"No data"} fontSize={18} />
          </div>
        )}
        <Gap height={15} />
        <div
          className="subcontent-info-box"
          style={{
            fontSize: "18px",
            marginLeft: "0px",
            background: "rgba(42, 196, 185, 0.8)",
            whiteSpace: "nowrap",
            overflow: "hidden",
          }}
        >
          ONGOING
        </div>
        <HorizontalLine />
        {isMinExist && (
          <div className="row-container" style={{ justifyContent: "left" }}>
            <Subinfo
              title={`#${minNum}`}
              content={`Score: ${minScore}% (${minSlots}/${14 * 80})`}
              fontSize={18}
              gap={20}
            />
          </div>
        )}
        {!isMinExist && (
          <div className="row-container" style={{ justifyContent: "left" }}>
            <Subinfo title={"No data"} fontSize={18} />
          </div>
        )}
        {isMaxExist && (
          <div className="row-container" style={{ justifyContent: "left" }}>
            <Subinfo
              title={`#${maxNum}`}
              content={`Score: ${maxScore}% (${maxSlots}/${14 * 80})`}
              fontSize={18}
              gap={20}
            />
          </div>
        )}
        <Gap />
      </div>
    </>
  );
}

export default ScoreBoard;
