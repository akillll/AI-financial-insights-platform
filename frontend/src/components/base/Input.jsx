import React from "react";

const Input = React.forwardRef((props, ref) => {
  return (
    <input
      ref={ref}
      className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-green-500 outline-none"
      {...props}
    />
  );
});

export default Input;