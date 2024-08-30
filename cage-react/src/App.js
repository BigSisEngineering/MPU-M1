import React, { useEffect, useState } from "react";
import Header from "./Components/Header";
import { FetchBoardData } from "./Middleware/fetchBoardData";
import CageStatus from "./Components/CageStatus";
import VideoFeed from "./Components/VideoFeed";
import Button from './Components/Button';
import * as PostActions from "./Actions/Post";
import "./App.css"; // Ensure this path is correct


function App() {
  const [boardData, setBoardData] = useState(null);
  const [error, setError] = useState(null);

  FetchBoardData(setBoardData, setError);

  // Extract statuses from the fetched data
  const starWheelStatus = boardData ? boardData.star_wheel_status : '';
  const unloaderStatus = boardData ? boardData.unloader_status : '';
  const modeStatus = boardData ? boardData.mode : '';
  const { starWheel, unloader, mode} = CageStatus(starWheelStatus, unloaderStatus, modeStatus);


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
              <div className="subcontent-info-box" style={{ backgroundColor: mode.color }}>{mode.text}</div>
            </div>
            <div className="gap"></div>
            <div className="subcontent-title">Commands</div>
            <div className="subinfo-horizontal-line"></div>
            <div className="buttons-container">
              <Button onClick={PostActions.MoveCCW} label="↪️"/>
              <Button onClick={PostActions.Unload} label="⤵️"/>
              <Button onClick={PostActions.MoveCW} label="↩️"/>
            </div>
            <div className="gap"></div>
            <div className="subcontent-title">Servos Init</div>
            <div className="subinfo-horizontal-line"></div>
            <div className="buttons-container">
              <Button onClick={PostActions.SWInit} label="SW Init"/>
              <Button onClick={PostActions.ULInit} label="UL Init"/>
              <Button onClick={PostActions.ALLInit} label="ALL Init"/>
              <Button onClick={PostActions.ClearError} label="Clear Error"/>
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
            <VideoFeed />
            <div className="subcontent-title">Servos & Sensors</div>
            <div className="subinfo-horizontal-line"></div>
            <div className="icon-container">
              <div className={`gear ${starWheel}`}>
                <i className="fas fa-cog" aria-hidden="true"></i>
                <span>SW</span>
              </div>
              <div className={`gear ${unloader}`}>
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
              <Button onClick={PostActions.PNP} label="PNP"/>
              <Button onClick={PostActions.Dummy} label="DUMMY"/>
              <Button onClick={PostActions.Experiment} label="EXPERIMENT"/>
              <button className="button">STOP</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
