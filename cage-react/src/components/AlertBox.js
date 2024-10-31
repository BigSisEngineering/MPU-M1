import React from "react";

function AlertBox({ content }) {
  return (
    <div id="alert-box" className="custom-alert">
      {content}
    </div>
  );
}

export default AlertBox;

