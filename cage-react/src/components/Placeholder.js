// Updated function to return a controlled input component
export function getInput(type, inputType, value, setValue) {
    const placeholders = {
        position: 'Enter position',
        interval: 'Enter interval in seconds',
        default: 'Enter value'
    };
    const placeholder = placeholders[inputType] || placeholders.default;

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
