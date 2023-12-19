import React, { useState, useEffect } from "react";
import {
  BrowserRouter,
  Route,
  Routes,
  useParams,
  useLocation,
} from "react-router-dom";
import Breadcrumbs from "./Breadcrumbs";
import DirectoryContents from "./DirectoryContents";
import VisCanvas from "./VisCanvas";
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

function useRouteChange(callback) {
  const location = useLocation();
  useEffect(() => {
    callback();
  }, [location]);
}

const FileExplorerContent = () => {
  const { "*": currentPath = "" } = useParams();
  const [canvasInfo, setCanvasInfo] = useState({
    show: false,
    dataUrl: null,
    fileType: null,
  });
  useRouteChange(() => {
    setCanvasInfo({
      show: false,
      dataUrl: null,
      fileType: null,
    });
  });
  return (
    <>
      <div className="row">
        <div className="col">
          <Breadcrumbs currentPath={currentPath} />
        </div>
      </div>
      <div className="row flex-grow-1">
        <div className="col-md-5">
          <DirectoryContents
            currentPath={currentPath}
            setCanvasInfo={setCanvasInfo}
          />
        </div>
        <div className="col-md-7">
          {/* <div id="vis-panel">{canvasInfo.dataUrl}</div> */}
          {canvasInfo.show && <VisCanvas canvasInfo={canvasInfo} />}
        </div>
      </div>
    </>
  );
};

export default FileExplorer;
