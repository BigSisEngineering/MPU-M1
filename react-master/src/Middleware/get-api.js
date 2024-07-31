// useDict.js
import { useState, useEffect } from "react";
import { fetchJSON } from "../Utils/Utils.js";

class Dicts {
  static m1a = 1;
  static m1c = 2;
  static cages = 3;
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
  const [dict1A, setDict1A] = useState(null);
  const [dict1C, setDict1C] = useState(null);
  const [dictCages, setDictCages] = useState(null);

  useEffect(() => {
    const urls = {
      [Dicts.m1a]: "/get_status/m1a",
      [Dicts.m1c]: "/get_status/m1c",
      [Dicts.cages]: "/get_status/cages",
    };

    const url = urls[dictName];

    if (url) {
      const intervalId = setInterval(() => {
        fetchAndSetState(
          url,
          {
            [Dicts.m1a]: setDict1A,
            [Dicts.m1c]: setDict1C,
            [Dicts.cages]: setDictCages,
          }[dictName]
        );
      }, 2000);

      return () => clearInterval(intervalId);
    }
  }, [dictName]);

  switch (dictName) {
    case Dicts.m1a:
      return dict1A;
    case Dicts.m1c:
      return dict1C;
    case Dicts.cages:
      return dictCages;
    default:
      return null;
  }
}

export { useDict, Dicts };
