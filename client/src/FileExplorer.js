import React from "react";
import { BrowserRouter, Route, Routes, useParams } from "react-router-dom";
import Breadcrumbs from "./Breadcrumbs";
import DirectoryContents from "./DirectoryContents";
import "./FileExplorer.css";

const FileExplorer = () => {
  return (
    <BrowserRouter>
      <div className="container-fluid pt-3 pb-3">
        <Routes>
          <Route path="/*" element={<FileExplorerContent />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
};

const FileExplorerContent = () => {
  const { "*": currentPath = "" } = useParams();
  return (
    <>
      <div className="row">
        <div className="col">
          <Breadcrumbs currentPath={currentPath} />
        </div>
      </div>
      <div className="row flex-grow-1">
        <div className="col-md-5">
          <DirectoryContents currentPath={currentPath} />
        </div>
        <div className="col-md-7">
          <div id="vis-panel" className="d-none">
            <div id="vis-display"></div>
          </div>
        </div>
      </div>
    </>
  );
};

export default FileExplorer;
