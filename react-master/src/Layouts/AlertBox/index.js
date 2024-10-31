import React from "react";
import "../../Assets/Styles/styles.css";

function AlertBox({ content }) {
  return (
    <div id="alert-box" className="custom-alert">
      {content}
    </div>
  );
}

export default AlertBox;
