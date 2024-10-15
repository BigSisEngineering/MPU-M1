import { useMemo } from 'react';

const CageStatus = (starWheelStatus, unloaderStatus, modeStatus, sensorsValues) => {
  // Parse the sensor values from a string format "(value1, value2, value3, value4)"
  const values = sensorsValues.replace(/[()]/g, '').split(', ').map(Number);

  // Access the specific sensor values for LOAD and BUFFER
  const loadSensorValue = values[0]; // first value for LOAD
  const bufferSensorValue = values[2]; // third value for BUFFER
  // console.log("loadSensorValue:", loadSensorValue);
  // console.log("bufferSensorValue:", bufferSensorValue);

  // Determine the color for the LOAD circle
  const load = useMemo(() => {
    return loadSensorValue > 90 ? 'green' : 'grey'; // If LOAD value > 90, color is green; otherwise, grey
  }, [loadSensorValue]);

  // Determine the color for the BUFFER circle
  const buffer = useMemo(() => {
    return bufferSensorValue > 90 ? 'green' : 'grey'; // If BUFFER value > 90, color is green; otherwise, grey
  }, [bufferSensorValue]);

  // Determine the status color and text for the star wheel
  const starWheel = useMemo(() => {
    switch (starWheelStatus) {
      case 'overload':
        return 'red';  // Overloaded condition
      case 'normal':
        return 'green';  // Normal operating condition
      case 'idle':
      case 'not_init':
        return 'grey';  // Idle or not initialized
      default:
        return 'black';  // Unknown or default condition
    }
  }, [starWheelStatus]);

  // Determine the status color and text for the unloader
  const unloader = useMemo(() => {
    switch (unloaderStatus) {
      case 'overload':
        return 'red';  // Overloaded condition
      case 'normal':
        return 'green';  // Normal operating condition
      case 'idle':
      case 'not_init':
        return 'grey';  // Idle or not initialized
      default:
        return 'black';  // Unknown or default condition
    }
  }, [unloaderStatus]);

  // Determine the mode display properties
  const mode = useMemo(() => {
    switch (modeStatus) {
      case 'pnp':
        return { color: 'green', text: 'PNP' };
      case 'dummy':
        return { color: 'blue', text: 'DUMMY' };
      case 'experiment':
        return { color: 'orange', text: 'EXPERIMENT' };
      case 'idle':
        return { color: 'grey', text: 'IDLE' };
      default:
        return { color: 'black', text: 'OFFLINE' };  // Default or unknown mode
    }
  }, [modeStatus]);

  // Return all computed statuses
  return { starWheel, unloader, mode, load, buffer };
};

export default CageStatus;
