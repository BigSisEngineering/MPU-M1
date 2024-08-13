import React from "react";
import { useState, useEffect } from "react";
import "../../Assets/Styles/styles.css";
import { useDict, Dicts } from "../../Middleware/get-api.js";
import { getColor, DEFAULT_MSG, DEFAULT_BOOL } from "../../Utils/Utils.js";
import {
  Info,
  Gap,
  HorizontalLine,
  Subinfo,
  SubcontentTitle,
  DisplayImage,
  DisplayCustomEmoji,
  CustomEmoji,
} from "../../Components/index.js";

function CCTV() {
  return (
    <>
      <div className="subcontent-container" style={{ border: "5px solid #ccc" }}>
        <SubcontentTitle text="CCTV" />
        <HorizontalLine />
        <DisplayImage link={`/cctv`} />
        <Gap />
      </div>
    </>
  );
}

export default CCTV;
