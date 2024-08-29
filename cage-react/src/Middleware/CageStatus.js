import { useMemo } from 'react';

const useCageStatusStyles = (starWheelStatus, unloaderStatus) => {
  const starWheelStyle = useMemo(() => {
    switch (starWheelStatus) {
      case 'overload':
        return 'red';  // CSS class for red
      case 'normal':
        return 'green';  // CSS class for green
      case 'idle':
      case 'not_init':
        return 'grey';  // CSS class for grey
      default:
        return 'grey';  // Default color if status is unknown
    }
  }, [starWheelStatus]);

  const unloaderStyle = useMemo(() => {
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

  return { starWheelStyle, unloaderStyle };
};

export default useCageStatusStyles;
