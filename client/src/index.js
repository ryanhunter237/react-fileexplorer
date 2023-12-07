import React from "react";
import ReactDOM from "react-dom/client";
import FileExplorer from "./FileExplorer";
import reportWebVitals from "./reportWebVitals";
import "bootstrap/dist/css/bootstrap.min.css";

const root = ReactDOM.createRoot(document.getElementById("root"));
const currentPath = "key-way-vice-solidworks-1/Key Way Vice Solidworks/Drawing";
root.render(
  <React.StrictMode>
    <FileExplorer />
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();