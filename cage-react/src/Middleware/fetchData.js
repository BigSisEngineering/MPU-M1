// src/Middleware/fetchData.js
import { useEffect } from 'react';

// General fetch function
async function fetchDataFromUrl(url, parser) {
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await parser(response);
        return data;
    } catch (error) {
        console.error("Error fetching data:", error);
        
        throw error;
    }
}

// Parser for Board Data
async function parseBoardData(response) {
    return response.json();
}

// Parser for Experiment Data
async function parseExperimentData(response) {
    const text = await response.text();
    return parseTextData(text);
}


// Helper function to parse the text data and format it for display
function parseTextData(text) {
    const patterns = {
        potsUnloaded: /purging state - pots unloaded : (\d+)/i,
        pauseDuration: /pause state for ([\d\.]+)s/i,
        remainingTime: /remaining time : ([\d\.]+)s/i,
    };

    let formattedData = "";
    let dataFound = {};

    // Extract all data first
    for (const key in patterns) {
        const regex = patterns[key];
        const match = text.match(regex);
        if (match && match[1]) {
            dataFound[key] = parseFloat(match[1]);
        }
    }

    // Format data based on what's found
    if ('potsUnloaded' in dataFound) {
        formattedData = `Purging state - pots unloaded : ${dataFound['potsUnloaded']}`;
    } else if ('pauseDuration' in dataFound && 'remainingTime' in dataFound) {
        formattedData = `Pause State for ${dataFound['pauseDuration']}s - Remaining Time: ${dataFound['remainingTime'].toFixed(2)}s`;
    }

    return formattedData;
}



// Custom hooks to fetch data
const useFetchData = (setResult, setError, url, parser) => {
    useEffect(() => {
        const fetchData = async () => {
            try {
                const data = await fetchDataFromUrl(url, parser);
                setResult(data);
            } catch (error) {
                setError(error.message);
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 5000);

        return () => clearInterval(interval);
    }, [setResult, setError, url, parser]);
};

export { useFetchData, parseBoardData, parseExperimentData };
