import React, { useState, useEffect } from "react";
import "../Assets/Styles/styles.css";
import { openLink } from "../Utils/Utils.js";
import green_circle from "../Assets/Media/green-circle.png";
import red_circle from "../Assets/Media/red-circle.png";
import grey_circle from "../Assets/Media/grey-circle.png";
import black_circle from "../Assets/Media/black-circle.png";
import red_hollow_circle from "../Assets/Media/red-hollow-circle.png";
import green_rectangle from "../Assets/Media/green-rectangle.png";
import red_rectangle from "../Assets/Media/red-rectangle.png";
import grey_rectangle from "../Assets/Media/grey-rectangle.png";
import black_rectangle from "../Assets/Media/black-rectangle.png";
import fallback from "../Assets/Media/404-or-page-f6738564cf.jpg";

class CustomEmoji {
  static green_circle = green_circle;
  static red_circle = red_circle;
  static grey_circle = grey_circle;
  static black_circle = black_circle;
  static red_hollow_circle = red_hollow_circle;
  static green_rectangle = green_rectangle;
  static red_rectangle = red_rectangle;
  static grey_rectangle = grey_rectangle;
  static black_rectangle = black_rectangle;
}

function DisplayImage({ link, width = 100 }) {
  const [imgSrc, setImgSrc] = useState(link);

  useEffect(() => {
    const interval = setInterval(() => {
      // Trigger a refresh by updating imgSrc
      setImgSrc(`${link}?t=${new Date().getTime()}`);
      console.log("refresh");
    }, 10000);

    return () => clearInterval(interval);
  }, [link]);

  return (
    <div className="video-feed-container" style={{ width: `${width}%`, margin: "auto" }}>
      <img src={imgSrc} alt="not found" onError={() => setImgSrc(fallback)} />
    </div>
  );
}

function DisplayCustomEmoji({ emoji }) {
  return <img src={emoji} alt={`emoji: ${emoji}`} style={{ width: "20px", height: "20px", padding: "0px 0px" }} />;
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
      <div className="gap" style={{ width: `${5}px` }}></div>
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
