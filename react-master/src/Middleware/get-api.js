import { useState, useEffect } from "react";
import { fetchJSON } from "../Utils/Utils.js";

class Dicts {
  static m1a = 1;
  static m1c = 2;
  static cages = 3;
  static system = 4;
}

// Global storage for state and intervals
const dictStates = {
  [Dicts.m1a]: null,
  [Dicts.m1c]: null,
  [Dicts.cages]: null,
  [Dicts.system]: null,
};

const intervalIds = {
  [Dicts.m1a]: null,
  [Dicts.m1c]: null,
  [Dicts.cages]: null,
  [Dicts.system]: null,
};

async function fetchAndSetState(url, dictName) {
  try {
    const result = await fetchJSON(url);
    dictStates[dictName] = result; // Update global state
  } catch (error) {
    dictStates[dictName] = null;
  }
}

function useDict(dictName) {
  const [state, setState] = useState(dictStates[dictName]);

  useEffect(() => {
    const urls = {
      [Dicts.m1a]: "/get_status/m1a",
      [Dicts.m1c]: "/get_status/m1c",
      [Dicts.cages]: "/get_status/cages",
      [Dicts.system]: "/get_status/system",
    };

    const fetchInterval = {
      [Dicts.m1a]: 2000,
      [Dicts.m1c]: 2000,
      [Dicts.cages]: 5000,
      [Dicts.system]: 2000,
    };

    const url = urls[dictName];

    if (url) {
      // If there's no interval running, start one
      if (!intervalIds[dictName]) {
        intervalIds[dictName] = setInterval(() => {
          fetchAndSetState(url, dictName);
        }, fetchInterval[dictName]);
      }

      // Update local state whenever the global state changes
      const updateState = () => setState(dictStates[dictName]);

      // Set the state initially and set up the update listener
      updateState();
      const intervalStateUpdate = setInterval(updateState, fetchInterval[dictName]);

      return () => clearInterval(intervalStateUpdate);
    }
  }, [dictName]);

  return state;
}

export { useDict, Dicts };
