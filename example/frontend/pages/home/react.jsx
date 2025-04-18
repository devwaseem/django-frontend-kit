import React, { useState } from "react";
import { createRoot } from 'react-dom/client';

export default function App() {
  const [index, setIndex] = useState(0);

  const handleClick = () => {
    setIndex(index + 1);
  };

  return (
    <div className="p-6 bg-gray-50 border border-gray-200 rounded-lg flex flex-col gap-4">
      <div>This is rendered using React</div>
      <div>Current values: {index}</div>
      <button
        type="button"
        onClick={handleClick}
        className="px-2 py-1 bg-black rounded-lg text-white cursor-pointer"
      >
        Increment
      </button>
    </div>
  );
}

const root = createRoot(document.getElementById('react-app'));
root.render(<App />);

if (import.meta.hot) {
    import.meta.hot.accept();
}
