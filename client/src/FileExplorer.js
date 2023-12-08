import React, { useState } from "react";
import Breadcrumbs from "./Breadcrumbs";
import DirectoryContents from "./DirectoryContents";
import "./FileExplorer.css";

const FileExplorer = () => {
  const [currentPath, setCurrentPath] = useState("");
  return (
    <div className="container-fluid pt-3 pb-3">
      <div className="row">
        <div className="col">
          <Breadcrumbs
            currentPath={currentPath}
            onPathChange={setCurrentPath}
          />
        </div>
      </div>
      <div className="row flex-grow-1">
        <div className="col-md-5">
          <DirectoryContents
            currentPath={currentPath}
            onPathChange={setCurrentPath}
          />
        </div>
        <div className="col-md-7">
          <div id="vis-panel" className="d-none">
            <div id="vis-display"></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FileExplorer;
