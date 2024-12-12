import React from "react";
import "../../Assets/Styles/styles.css";
import { useDict, Dicts } from "../../Middleware/get-api.js";
import Cage from "../Cage/index.js";
import CCTV from "../CCTV/index.js";
import ScoreBoard from "../ScoreBoard/index.js";
import { Gap } from "../../Components/index.js";

function Cages({ isSelected, toggleSelected, isCageActionMode }) {
  const dictInfo = useDict(Dicts.info);
  const row = dictInfo ? dictInfo["row"] : null;

  return (
    <>
      <Gap height={50} />
      <div className="row-container" style={{ justifyContent: "center" }}>
        {Array.from({ length: 5 }, (_, i) => (
          <div className="columns-container" style={{ width: "14%" }}>
            <Cage
              key={i}
              row={row}
              number={i + 1}
              isSelected={isSelected[i]}
              toggleSelected={toggleSelected(i)}
              isCageActionMode={isCageActionMode}
            />
          </div>
        ))}
      </div>
      <div className="row-container" style={{ justifyContent: "center", padding: "0px 0px" }}>
        {Array.from({ length: 5 }, (_, i) => (
          <div className="columns-container" style={{ width: "14%" }}>
            <Cage
              key={i + 5}
              row={row}
              number={i + 6}
              isSelected={isSelected[i + 5]}
              toggleSelected={toggleSelected(i + 5)}
              isCageActionMode={isCageActionMode}
            />
          </div>
        ))}
      </div>
      <div className="row-container" style={{ justifyContent: "center", padding: "0px 0px" }}>
        {Array.from({ length: 4 }, (_, i) => (
          <div className="columns-container" style={{ width: "14%" }}>
            <Cage
              key={i + 10}
              row={row}
              number={i + 11}
              isSelected={isSelected[i + 10]}
              toggleSelected={toggleSelected(i + 10)}
              isCageActionMode={isCageActionMode}
            />
          </div>
        ))}

        {isCageActionMode && (
          <div className="columns-container" style={{ width: "14%" }}>
            <ScoreBoard />
          </div>
        )}
        {!isCageActionMode && (
          <div className="columns-container" style={{ width: "14%" }}>
            <CCTV />
          </div>
        )}
      </div>
    </>
  );
}

export default Cages;
