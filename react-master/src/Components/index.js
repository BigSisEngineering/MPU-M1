import React, { useState } from "react";
import "../Assets/Styles/styles.css";
import { openLink } from "../Utils/Utils.js";
import sw_red from "../Assets/Media/SW_RED.png";
import sw_green from "../Assets/Media/SW_GREEN.png";
import ul_red from "../Assets/Media/UL_RED.png";
import ul_green from "../Assets/Media/UL_GREEN.png";
import ul_sensor_green from "../Assets/Media/ULSensor_GREEN.png";
import ul_sensor_red from "../Assets/Media/ULSensor_RED.png";
import l_sensor_green from "../Assets/Media/LSensor_GREEN.png";
import l_sensor_red from "../Assets/Media/LSensor_RED.png";
import buf_sensor_green from "../Assets/Media/BUFSensor_GREEN.png";
import buf_sensor_red from "../Assets/Media/BUFSensor_RED.png";
import fallback from "../Assets/Media/404-or-page-f6738564cf.jpg";

class CustomEmoji {
  static sw_red = sw_red;
  static sw_green = sw_green;
  static ul_red = ul_red;
  static ul_green = ul_green;
  static ul_sensor_green = ul_sensor_green;
  static ul_sensor_red = ul_sensor_red;
  static l_sensor_green = l_sensor_green;
  static l_sensor_red = l_sensor_red;
  static buf_sensor_green = buf_sensor_green;
  static buf_sensor_red = buf_sensor_red;
}

function DisplayImage({ link, width = 100 }) {
  const [imgSrc, setImgSrc] = useState(link);
  return (
    <div className="video-feed-container" style={{ width: `${width}%`, margin: "auto" }}>
      <img src={imgSrc} alt="not found" onError={() => setImgSrc(fallback)} />
    </div>
  );
}

function DisplayCustomEmoji({ emoji }) {
  return <img src={emoji} alt={`emoji: ${emoji}`} style={{ width: "40px", height: "40px", padding: "0px 0px" }} />;
}

function Info({ text, color }) {
  return (
    <div className="subcontent-info-container" style={{ background: color }}>
      {text}
    </div>
  );
}

function InfoSameRow({ title, text, color }) {
  return (
    <div className="subcontent-info-same-row-container">
      {title}
      <div className="subcontent-info-box" style={{ background: color }}>
        {text}
      </div>
    </div>
  );
}

function Subinfo({ title, content }) {
  return (
    <div className="subcontent-subinfo-container">
      {title}
      <div className="display-box">{content}</div>
    </div>
  );
}

function Button({ name, onclick, disable = false }) {
  return (
    <button
      className="button"
      disabled={disable}
      onClick={() => {
        onclick();
      }}
    >
      {name}
    </button>
  );
}

function Gap({ height = null }) {
  if (height === null) {
    return <div className="gap"></div>;
  }
  return <div className="gap" style={{ height: `${height}px` }}></div>;
}

function HorizontalLine() {
  return <div className="subinfo-horizontal-line"></div>;
}

function SubcontentTitle({ text, link = null }) {
  if (link === null) {
    return <div className="subcontent-title">{text}</div>;
  } else {
    return (
      <div className="subcontent-title" onClick={() => openLink(link)} style={{ cursor: "pointer" }}>
        {text}
      </div>
    );
  }
}

function DebugContent({ elements }) {
  return (
    <div className="debug-container hidden">
      <div className="subcontent-row-container">{React.Children.toArray(elements)}</div>
      <HorizontalLine />
    </div>
  );
}

function TextInput({ value, onChange, placeholder = "" }) {
  return <input className="input-box" type="text" value={value} onChange={onChange} placeholder={placeholder} />;
}

export {
  DisplayImage,
  Info,
  Subinfo,
  Button,
  Gap,
  HorizontalLine,
  DebugContent,
  TextInput,
  SubcontentTitle,
  InfoSameRow,
  DisplayCustomEmoji,
  CustomEmoji,
};
