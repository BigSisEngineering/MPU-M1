import React from "react";
import { useState, useEffect, useRef, useCallback } from "react";
import "../../Assets/Styles/styles.css";
import { useDict, Dicts } from "../../Middleware/get-api.js";
import { getColor, DEFAULT_MSG } from "../../Utils/Utils.js";

function MainMessage() {
  const [message, setMessage] = useState(DEFAULT_MSG);
  const [flash, setFlash] = useState(false);
  const [isToggled, setIsToggled] = useState(false);
  const [mode, setMode] = useState(DEFAULT_MSG);
  const intervalObject = useRef(null);
  const messageRef = useRef(null);
  const flashColor = useRef(null);

  const toggle = useCallback(() => {
    if (messageRef.current) {
      setIsToggled((prevIsToggled) => !prevIsToggled);
      if (!isToggled) {
        messageRef.current.classList.add("toggled");
        messageRef.current.style.background = flashColor.current;
      } else {
        messageRef.current.classList.remove("toggled");
        messageRef.current.style.background = "rgba(125, 125, 125, 0.32)";
      }
    }
  }, [isToggled, setIsToggled, flashColor]);

  /* ---------------------------------------------------------------------------------- */
  const dictActuationHandler = useDict(Dicts.actuation_handler);
  const dictSystem = useDict(Dicts.system);

  useEffect(() => {
    if (dictActuationHandler) {
      setMessage(dictActuationHandler["message"]);
    } else {
      setMessage(DEFAULT_MSG);
    }
  }, [dictActuationHandler]);

  useEffect(() => {
    if (dictSystem) {
      setMode(dictSystem["system_state"]);
    } else {
      setMode(DEFAULT_MSG);
    }
  }, [dictSystem]);
  /* ---------------------------------------------------------------------------------- */

  useEffect(() => {
    if (flash) {
      intervalObject.current = setInterval(() => {
        toggle();
      }, 1000);
    } else {
      if (intervalObject.current) {
        clearInterval(intervalObject.current);
      }
    }

    return () => {
      if (intervalObject.current) {
        clearInterval(intervalObject.current);
      }
    };
  }, [flash, toggle]);

  function startFlashing(color) {
    if (!flash) {
      flashColor.current = color;
      setFlash(true);
    }
  }

  function stopFlashing() {
    if (flash) {
      setFlash(false);
    }
  }

  function processMessage(inputString, modeState) {
    const slashIndex = inputString.indexOf("/");
    let messageType;
    let message;
    let color = null;
    let flash = false;

    try {
      messageType = inputString[slashIndex - 1];
      message = inputString.substring(slashIndex + 1);
    } catch (error) {
      messageType = DEFAULT_MSG;
      message = DEFAULT_MSG;
    }

    switch (messageType) {
      case "A": // actuation
        if (modeState.includes("IDLE")) {
          message = `Stopping soon... [${message}]`;
          color = getColor("YELLOW");
          flash = true;
        } else {
          color = getColor("GREEN");
        }
        break;
      case "P": // passive
        color = getColor("YELLOW");
        break;
      case "U": // user interaction required
        color = getColor("GREEN");
        flash = true;
        break;
      default:
        color = getColor("GREY");
    }

    if (flash) {
      startFlashing(color);
    } else {
      stopFlashing();
    }

    return { message: message, color: color };
  }

  const result = processMessage(message, mode);

  return (
    <div className="current-action-container">
      <div className="main-message" ref={messageRef}>
        {result.message}
      </div>
    </div>
  );
}

export default MainMessage;
