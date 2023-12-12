import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import axios from "axios";
import "./Button.css";
import "./Table.css";

function convertSize(size) {
  size = parseFloat(size);
  const suffixes = ["B", "KB", "MB", "GB"];
  let suffixIdx = 0;
  while (size >= 1024 && suffixIdx < 3) {
    size /= 1024;
    suffixIdx++;
  }
  return `${Math.round(size)} ${suffixes[suffixIdx]}`;
}

const FileRow = ({ fileInfoUrl, setCanvasInfo }) => {
  const [fileInfo, setFileInfo] = useState({
    relpath: "",
    name: "",
    st_size: "",
    file_type: "",
    thumbnail_url: "",
    file_data_url: "",
  });

  useEffect(() => {
    axios
      .get(fileInfoUrl)
      .then((response) => {
        setFileInfo(response.data);
      })
      .catch((error) =>
        console.error(`Error fetching file details from ${fileInfoUrl}:`, error)
      );
  }, [fileInfoUrl]);

  const handleImageClick = (dataUrl, fileType) => {
    setCanvasInfo({
      show: true,
      dataUrl: dataUrl,
      fileType: fileType,
    });
  };

  // Need to check when thumbnail_url is 'processing' or 'error'
  return (
    <tr>
      <td>
        <img src="/images/file.png" className="icon" alt="File Icon" />
        {fileInfo.name}
      </td>
      <td>{convertSize(fileInfo.st_size)}</td>
      <td>
        {fileInfo.thumbnail_url ? (
          <img
            src={fileInfo.thumbnail_url}
            alt="Thumbnail"
            onClick={() =>
              handleImageClick(fileInfo.file_data_url, fileInfo.file_type)
            }
            className="img-thumbnail img-preview"
          />
        ) : null}
      </td>
    </tr>
  );
};

const DirectoryRow = ({ name, relpath }) => {
  return (
    <tr>
      <td>
        <img src="/images/folder.png" className="icon" alt="Folder Icon" />
        <Link to={`/${relpath}`}>{name}</Link>
      </td>
      <td></td>
      <td></td>
    </tr>
  );
};

const DirectoryContents = ({ currentPath, setCanvasInfo }) => {
  const [directoryInfo, setDirectoryInfo] = useState({
    directories: [],
    files: [],
  });
  useEffect(() => {
    axios
      .get(`/api/directory-info/${currentPath}`)
      .then((response) => {
        setDirectoryInfo(response.data);
      })
      .catch((error) => console.error("Error fetching data:", error));
  }, [currentPath]);

  return (
    <div className="table-container">
      <table className="table table-bordered table-striped">
        <thead>
          <tr>
            <th style={{ width: "60%" }}>Name</th>
            <th style={{ width: "17%" }}>Size</th>
            <th style={{ width: "23%" }}>Thumbnail</th>
          </tr>
        </thead>
        <tbody>
          {directoryInfo["directories"].map((info) => (
            <DirectoryRow
              key={info.name}
              name={info.name}
              relpath={info.relpath}
            />
          ))}
          {directoryInfo["files"].map((info) => (
            <FileRow
              key={info.name}
              fileInfoUrl={info.link}
              setCanvasInfo={setCanvasInfo}
            />
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default DirectoryContents;
