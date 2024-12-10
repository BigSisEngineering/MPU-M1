// Updated function to return a controlled input component
export function getInput(type, inputType, value, setValue, placeholder) {
  // const placeholders = {
  //     position: 'Enter position',
  //     pauseinterval: 'Enter interval in seconds',
  //     cycletime: 'Enter interval in seconds',
  //     valvedelay: 'Enter delay in ms',
  //     default: 'Enter value'
  // };
  // const placeholder = placeholders[inputType] || placeholders.default;

  return (
    <input
      type={type}
      placeholder={placeholder}
      className="input-box"
      value={value}
      onChange={(e) => setValue(e.target.value)}
    />
  );
}
