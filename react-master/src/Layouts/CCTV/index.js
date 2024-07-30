import React from "react";
import "../../Assets/Styles/styles.css";
import { DisplayImage, Gap } from "../../Components/index.js";

function CCTV() {
  const link = "/image";

  return (
    <div className="subcontent-container" style={{ width: "60%", marginRight: "auto", marginLeft: "auto" }}>
      📸 CCTV
      <Gap />
      <DisplayImage link={link} />
    </div>
  );
}

export default CCTV;
