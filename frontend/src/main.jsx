import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";

window.addEventListener('unhandledrejection', (event) => {
  event.preventDefault();
  console.error('Unhandled promise rejection:', event.reason);
});

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);