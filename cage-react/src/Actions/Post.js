const sendPostRequest = async (endpoint) => {
  const url = `http://tantest:8080${endpoint}`;
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({})
    });

    if (response.ok && response.headers.get('Content-Type')?.includes('application/json')) {
      const data = await response.json();
      console.log(data);
      return data;
    } else {
      const text = await response.text();
      console.log(text);
      return text;
    }
  } catch (error) {
    console.error('Error:', error);
    return null;
  }
};


const sendPostRequestWithParam = async (endpoint, param) => {
  const url = `http://tantest:8080${endpoint}/${param}`;
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({})
    });

    if (response.ok && response.headers.get('Content-Type')?.includes('application/json')) {
      const data = await response.json();
      console.log(data);
      return data;
    } else {
      const text = await response.text();
      console.log(text);
      return text;
    }
  } catch (error) {
    console.error('Error with param:', error);
    return null;
  }
};



export const MoveCCW = () => sendPostRequest('/MOVE_CCW');
export const MoveCW = () => sendPostRequest('/MOVE_CW');
export const Unload = () => sendPostRequest('/UNLOAD');
export const SWInit = () => sendPostRequest('/STAR_WHEEL_INIT');
export const ULInit = () => sendPostRequest('/UNLOADER_INIT');
export const ALLInit = () => sendPostRequest('/ALL_SERVOS_INIT');
export const PNP = () => sendPostRequest('/ENABLE_PNP');
export const Dummy = () => sendPostRequest('/ENABLE_DUMMY');
export const Experiment = () => sendPostRequest('/ENABLE_EXPERIMENT');
export const SaveZero = () => sendPostRequest('/SAVE_STAR_WHEEL_ZERO');
export const SaveOffset = () => sendPostRequest('/SAVE_STAR_WHEEL_OFFSET');


export const MoveSW = (param) => sendPostRequestWithParam('/MOVE_STAR_WHEEL', param);
export const SetInterval = (param) => sendPostRequestWithParam('/SET_PAUSE_INTERVAL', param);

