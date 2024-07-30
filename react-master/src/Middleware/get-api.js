// useDict.js
import { useState, useEffect } from "react";
import { fetchJSON } from "../Utils/Utils.js";

class Dicts {
  static system = 1;
  static actuators = 2;
  static outputs = 3;
  static inputs = 4;
  static actuation_handler = 5;
  static settings = 6;
}

async function fetchAndSetState(url, setState) {
  try {
    const result = await fetchJSON(url);
    setState(result);
  } catch (error) {
    setState(null);
  }
}

function useDict(dictName) {
  const [dictSettings, setDictSettings] = useState(null);
  const [dictActuators, setDictActuators] = useState(null);
  const [dictInputs, setDictInputs] = useState(null);
  const [dictOutputs, setDictOutputs] = useState(null);
  const [dictActuationHandler, setDictActuationHandler] = useState(null);
  const [dictSystem, setDictSystem] = useState(null);

  useEffect(() => {
    const urls = {
      [Dicts.system]: "/get_status/system",
      [Dicts.actuators]: "/get_status/actuators",
      [Dicts.outputs]: "/get_status/outputs",
      [Dicts.inputs]: "/get_status/inputs",
      [Dicts.actuation_handler]: "/get_status/actuation_handler",
      [Dicts.settings]: "/get_status/settings",
    };

    const url = urls[dictName];

    if (url) {
      const intervalId = setInterval(() => {
        fetchAndSetState(
          url,
          {
            [Dicts.system]: setDictSystem,
            [Dicts.actuators]: setDictActuators,
            [Dicts.outputs]: setDictOutputs,
            [Dicts.inputs]: setDictInputs,
            [Dicts.actuation_handler]: setDictActuationHandler,
            [Dicts.settings]: setDictSettings,
          }[dictName]
        );
      }, 2000);

      return () => clearInterval(intervalId);
    }
  }, [dictName]);

  switch (dictName) {
    case Dicts.system:
      return dictSystem;
    case Dicts.actuators:
      return dictActuators;
    case Dicts.outputs:
      return dictOutputs;
    case Dicts.inputs:
      return dictInputs;
    case Dicts.actuation_handler:
      return dictActuationHandler;
    case Dicts.settings:
      return dictSettings;
    default:
      return null;
  }
}

export { useDict, Dicts };
