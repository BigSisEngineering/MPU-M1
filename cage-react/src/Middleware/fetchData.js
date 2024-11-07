// // src/Middleware/fetchData.js
// import { useEffect } from "react";

// // General fetch function
// async function fetchDataFromUrl(url, parser) {
//   try {
//     const response = await fetch(url);
//     if (!response.ok) {
//       throw new Error(`HTTP error! Status: ${response.status}`);
//     }
//     const data = await parser(response);
//     return data;
//   } catch (error) {
//     console.error("Error fetching data:", error);

//     throw error;
//   }
// }

// // Parser for Board Data
// async function parseBoardData(response) {
//   return response.json();
// }

// // Parser for Experiment Data
// async function parseExperimentData(response) {
//   let text = await response.text();
//   console.log(text);
//   return text;
// }

// // Helper function to parse the text data and format it for display
// function parseTextData(text) {
//   const patterns = {
//     potsUnloaded: /purging state - pots unloaded : (\d+)/i,
//     pauseDuration: /pause state for ([\d\.]+)s/i,
//     remainingTime: /remaining time : ([\d\.]+)s/i,
//   };

//   let formattedData = "";
//   let dataFound = {};

//   // Extract all data first
//   for (const key in patterns) {
//     const regex = patterns[key];
//     const match = text.match(regex);
//     if (match && match[1]) {
//       dataFound[key] = parseFloat(match[1]);
//     }
//   }

//   // Format data based on what's found
//   if ("potsUnloaded" in dataFound) {
//     formattedData = `Purging state - pots unloaded : ${dataFound["potsUnloaded"]}`;
//   } else if ("pauseDuration" in dataFound && "remainingTime" in dataFound) {
//     formattedData = `Pause State for ${dataFound["pauseDuration"]}s - Remaining Time: ${dataFound[
//       "remainingTime"
//     ].toFixed(2)}s`;
//   }

//   return formattedData;
// }

// // Custom hooks to fetch data
// async function useFetchData(setResult, setError, url, parser) {
//   useEffect(() => {
//     const fetchData = async () => {
//       try {
//         let data = await fetchDataFromUrl(url, parser);
//         setResult(data);
//       } catch (error) {
//         setError(error.message);
//       }
//     };

//     fetchData();
//     const interval = setInterval(fetchData, 500);

//     return () => clearInterval(interval);
//   }, [setResult, setError, url, parser]);
// }

// export { useFetchData, parseBoardData, parseExperimentData };

// useDict.js
import { useState, useEffect } from "react";

class Dicts {
  static boardData = 1;
  static experimentData = 2;
  static experimentSettings = 3;
}

async function fetchJSON(url) {
  try {
    const response = await fetch(url, {
      method: "GET",
    });

    if (!response.ok) {
      throw new Error("Network response was not ok");
    }

    return await response.json();
  } catch (error) {
    throw error;
  }
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
  const [dictboardData, setDictboardData] = useState(null);
  const [dictExperimentData, setDictExperimentData] = useState(null);
  const [dictExperimentSettings, setDictExperimentSettings] = useState(null);

  useEffect(() => {
    const urls = {
      [Dicts.boardData]: "/BoardData",
      [Dicts.experimentData]: "/ExperimentData",
      [Dicts.experimentSettings]: "/ExperimentSettings",
    };

    const url = urls[dictName];

    if (url) {
      const intervalId = setInterval(() => {
        fetchAndSetState(
          url,
          {
            [Dicts.boardData]: setDictboardData,
            [Dicts.experimentData]: setDictExperimentData,
            [Dicts.experimentSettings]: setDictExperimentSettings,
          }[dictName]
        );
      }, 2000);

      return () => clearInterval(intervalId);
    }
  }, [dictName]);

  switch (dictName) {
    case Dicts.boardData:
      return dictboardData;
    case Dicts.experimentData:
      return dictExperimentData;
    case Dicts.experimentSettings:
      return dictExperimentSettings;
    default:
      return null;
  }
}

export { useDict, Dicts };
