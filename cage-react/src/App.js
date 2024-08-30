import React, { useEffect, useState } from "react";
import { FetchBoardData } from "./Middleware/fetchBoardData";
import Header from "./Components/Header";
import CageStatus from "./Components/CageStatus";
import VideoFeed from "./Components/VideoFeed";
import Button from './Components/Button';
import { getInput } from './Components/Placeholder';

import * as PostActions from "./Actions/Post";
import "./App.css";

function App() {
  const [boardData, setBoardData] = useState(null);
  const [error, setError] = useState(null);
  const [position, setPosition] = useState('');
  const [interval, setInterval] = useState('');

  FetchBoardData(setBoardData, setError);

  // Extract statuses from the fetched data
  const starWheelStatus = boardData ? boardData.star_wheel_status : '';
  const unloaderStatus = boardData ? boardData.unloader_status : '';
  const modeStatus = boardData ? boardData.mode : '';
  const { starWheel, unloader, mode } = CageStatus(starWheelStatus, unloaderStatus, modeStatus);

  const isIdle = mode.text === 'IDLE';
  const isNormal = starWheelStatus === 'normal' && unloaderStatus === 'normal';

  const handleMoveSW = () => {
    PostActions.MoveSW(position); // Use the current position state as parameter
  };

  const handleSetInterval = () => {
    PostActions.SetInterval(interval); // Use the current interval state as parameter
  };

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
              <Button onClick={PostActions.MoveCCW} label="↪️" disabled={!isIdle}/>
              <Button onClick={PostActions.Unload} label="⤵️" disabled={!isIdle}/>
              <Button onClick={PostActions.MoveCW} label="↩️" disabled={!isIdle}/>
            </div>
            <div className="gap"></div>
            <div className="subcontent-title">Servos Init</div>
            <div className="subinfo-horizontal-line"></div>
            <div className="buttons-container">
              <Button onClick={PostActions.SWInit} label="SW Init" disabled={!isIdle}/>
              <Button onClick={PostActions.ULInit} label="UL Init" disabled={!isIdle}/>
              <Button onClick={PostActions.ALLInit} label="ALL Init" disabled={!isIdle}/>
            </div>
            <div className="gap"></div>
            <div className="subcontent-title">SW Alignment</div>
            <div className="subinfo-horizontal-line"></div>
            <div className="buttons-container">
              <Button onClick={PostActions.SaveZero} label="Save Zero" disabled={!isIdle}/>
              <Button onClick={PostActions.SaveOffset} label="Save Offset" disabled={!isIdle}/>
              <Button onClick={handleMoveSW} label="Move SW" disabled={!isIdle}/>
              {getInput('number', 'position', position, setPosition)}
            </div>
            <div className="gap"></div>
            <div className="subcontent-title">Experiment Settings</div>
            <div className="subinfo-horizontal-line"></div>
            <div className="buttons-container">
              <Button onClick={handleSetInterval} label="Set Interval" />
              {getInput('number', 'interval', interval, setInterval)}
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
              <Button onClick={PostActions.PNP} label="PNP" disabled={!isIdle || !isNormal}/>
              <Button onClick={PostActions.Dummy} label="DUMMY" disabled={!isIdle || !isNormal}/>
              <Button onClick={PostActions.Experiment} label="EXPERIMENT" disabled={!isIdle || !isNormal}/>
              <button className="button" disabled={isIdle}>STOP</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
