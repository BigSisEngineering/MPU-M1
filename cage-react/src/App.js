import React, { useEffect, useState } from "react";
import Header from "./components/Header";
import { FetchBoardData } from "./Middleware/fetchBoardData";
import useCageStatusStyles from "./Middleware/CageStatus";
import "./App.css"; // Ensure this path is correct


function App() {
  const [boardData, setBoardData] = useState(null);
  const [error, setError] = useState(null);

  FetchBoardData(setBoardData, setError);

  // Extract statuses from the fetched data
  const starWheelStatus = boardData ? boardData.star_wheel_status : '';
  const unloaderStatus = boardData ? boardData.unloader_status : '';
  const { starWheelStyle, unloaderStyle } = useCageStatusStyles(starWheelStatus, unloaderStatus);


  return (
    <div>
      <Header />
      <div style={{ display: "flex", width: "100%" }}>
        <div className="columns-container" style={{ width: "40%" }}>
          <div className="subcontent-container">
            <div className="subcontent-title">Production Status</div>
            <div className="subinfo-horizontal-line"></div>
            <div className="subcontent-info-same-row-container">
              ⓘ Status
              <div className="subcontent-info-box">PNP</div>
            </div>
            <div className="gap"></div>
            <div className="subcontent-title">Commands</div>
            <div className="subinfo-horizontal-line"></div>
            <div className="buttons-container">
              <button className="button">↪️</button>
              <button className="button">⤵️</button>
              <button className="button">↩️</button>
            </div>
            <div className="gap"></div>
            <div className="subcontent-title">Servos Init</div>
            <div className="subinfo-horizontal-line"></div>
            <div className="buttons-container">
              <button className="button">SW Init</button>
              <button className="button">UL Init</button>
              <button className="button">ALL Init</button>
              <button className="button">Clear Error</button>
            </div>
            <div className="gap"></div>
            <div className="subcontent-title">SW Alignment</div>
            <div className="subinfo-horizontal-line"></div>
            <div className="buttons-container">
              <button className="button">Save Zero</button>
              <button className="button">Save Offset</button>
              <button className="button">Move SW</button>
              <input type="number" placeholder="Pos" className="input-box" />
            </div>
            <div className="gap"></div>
            <div className="subcontent-title">Experiment Settings</div>
            <div className="subinfo-horizontal-line"></div>
            <div className="buttons-container">
              <button className="button">Confirm</button>
              <input type="number" placeholder="Interval" className="input-box" />
            </div>
            <div className="gap"></div>
          </div>
        </div>
        <div className="columns-container" style={{ width: "60%" }}>
          <div className="subcontent-container">
            <div className="video-feed-container"></div>
            <div className="subcontent-title">Servos & Sensors</div>
            <div className="subinfo-horizontal-line"></div>
            <div className="icon-container">
              <div className={`gear ${starWheelStyle}`}>
                <i className="fas fa-cog" aria-hidden="true"></i>
                <span>SW</span>
                36
              </div>
              <div className={`gear ${unloaderStyle}`}>
                <i className="fas fa-cog" aria-hidden="true"></i>
                <span>UL</span>
              </div>
              <div className="circle">
                <span>BUFFER</span>
              </div>
              <div className="circle">
                <span>LOAD</span>
              </div>
            </div>
            <div className="gap"></div>
            <div className="subcontent-title">Operation Control</div>
            <div className="subinfo-horizontal-line"></div>
            <div className="buttons-container">
              <button className="button">PNP</button>
              <button className="button">DUMMY</button>
              <button className="button">EXPERIMENT</button>
              <button className="button">STOP</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
