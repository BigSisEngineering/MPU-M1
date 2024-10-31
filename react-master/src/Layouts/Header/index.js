import "../../Assets/Styles/styles.css";
import { HeaderButton } from "../../Components/index.js";

function Header({ module, unit, row, isDisplayOnly, setIsDisplayOnly }) {
  function generateName(module) {
    switch (module) {
      case 1:
        return "🥚 M1-Egg Detection";
      case 2:
        return "🪰 M2-Adult Sortation";
      case 3:
        return "⚤ M3-Sex Sortation";
      case 4:
        return "🛁 M4-Washer";
      case 5:
        return "🩻 M5-Male Sterilization";
      default:
        return "❓ MODULE NOT FOUND";
    }
  }
  return (
    <div className="header">
      <div className="header-container-module-name">
        <h2>{generateName(module)}</h2>
      </div>
      <div className="header-container-text">
        <h2>{unit}</h2>
      </div>
      <div className="header-container-text">
        <h2>Row: {row}</h2>
      </div>
      <div className="header-container-button">
        View mode:
        <HeaderButton name={isDisplayOnly ? "DISPLAY" : "OPERATION"} onclick={() => setIsDisplayOnly(!isDisplayOnly)} />
      </div>
    </div>
  );
}

export default Header;
