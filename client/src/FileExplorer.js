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
      <Routes>
        <Route path="/*" element={<FileExplorerContent />} />
      </Routes>
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
    <div className="grid-container">
      <Breadcrumbs currentPath={currentPath} />
      <DirectoryContents
        currentPath={currentPath}
        setCanvasInfo={setCanvasInfo}
      />
      {canvasInfo.show && (
        <VisCanvas key={canvasInfo.dataUrl} canvasInfo={canvasInfo} />
      )}
    </div>
  );
};

export default FileExplorer;
