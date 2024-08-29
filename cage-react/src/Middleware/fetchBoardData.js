// src/Middleware/fetchBoardData.js
import { useEffect } from 'react';

const BoardData = async () => {
    const url = `http://linaro-alip/:8080/BoardData`;
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        console.log("Fetched Board Data:", data);
        return data;
    } catch (error) {
        console.error("Error fetching board data:", error);
        throw error;
    }
};

// Proper custom hook to fetch data every 5 seconds
const FetchBoardData = (setBoardData, setError) => {
    useEffect(() => {
        const fetchData = async () => {
            try {
                const data = await BoardData();
                setBoardData(data);
            } catch (error) {
                setError(error.message);
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 5000);

        return () => clearInterval(interval);
    }, [setBoardData, setError]);
};

export { BoardData, FetchBoardData };
