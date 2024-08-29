import React from "react";
import Header from "./components/Header";
import "./App.css"; // Ensure this path is correct

function App() {
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
              <input
                type="number"
                placeholder="Interval"
                className="input-box"
              />
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
              <div className="gear">
                <i className="fas fa-cog"></i>

                <span>SW</span>
              </div>
              <div className="gear">
                <i className="fas fa-cog"></i>
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
