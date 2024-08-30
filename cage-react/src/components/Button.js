// src/Components/Button.js
import React from 'react';

const Button = ({ onClick, label, disabled }) => {
  return (
    <button className="button" onClick={onClick} disabled={disabled}>
      {label}
    </button>
  );
};

export default Button;

