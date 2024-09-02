import React from "react";
import hostname from './Hostname';  


function Header() {
  return (
    <div className="header">
      <div className="header-container-module-name">Module Name : {hostname}</div>
      {/* <div className="header-container-text">Status: Active</div> */}
    </div>
  );
}

export default Header;
