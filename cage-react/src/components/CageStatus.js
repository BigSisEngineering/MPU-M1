import { useMemo } from 'react';

const CageStatus = (starWheelStatus, unloaderStatus, modeStatus) => {
  const starWheel = useMemo(() => {
    switch (starWheelStatus) {
      case 'overload':
        return 'red';  // CSS class for red
      case 'normal':
        return 'green';  // CSS class for green
      case 'idle':
      case 'not_init':
        return 'grey';  // CSS class for grey
      default:
        return 'black';  // Default color if status is unknown
    }
  }, [starWheelStatus]);

  const unloader = useMemo(() => {
    switch (unloaderStatus) {
      case 'overload':
        return 'red';  // CSS class for red
      case 'normal':
        return 'green';  // CSS class for green
      case 'idle':
      case 'not_init':
        return 'grey';  // CSS class for grey
      default:
        return 'black';  // Default color if status is unknown
    }
  }, [unloaderStatus]);

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
        return { color: 'black', text: 'OFFLINE' };  // Default state
    }
  }, [modeStatus]);

  return { starWheel, unloader, mode };
};

export default CageStatus;
