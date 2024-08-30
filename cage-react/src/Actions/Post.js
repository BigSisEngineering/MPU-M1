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
      console.log('Response:', data);
      return data;
    } else {
      const text = await response.text();
      console.log('Text response:', text);
      return text;
    }
  } catch (error) {
    console.error('Error:', error);
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
// export const ClearError = () => sendPostRequest('/CLEAR_ERROR');
// export const Confirm = () => sendPostRequest('/CONFIRM');
// export const Stop = () => sendPostRequest('/STOP');
