import React, { useEffect, useState } from "react";
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

const FileRow = ({ fileInfoUrl }) => {
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

  // Need to check when thumbnail_url is 'processing' or 'error'
  return (
    <tr>
      <td>
        <img src="/images/file.png" class="icon" alt="File Icon" />
        {fileInfo.name}
      </td>
      <td>{convertSize(fileInfo.st_size)}</td>
      <td>
        {fileInfo.thumbnail_url ? (
          <img src={fileInfo.thumbnail_url} alt="Thumbnail" />
        ) : null}
      </td>
    </tr>
  );
};

const DirectoryRow = ({ name, relpath, onPathChange }) => {
  return (
    <tr>
      <td>
        <img src="/images/folder.png" class="icon" alt="Folder Icon" />
        <button
          type="button"
          className="directory-button"
          onClick={() => onPathChange(relpath)}
        >
          {name}
        </button>
      </td>
      <td></td>
      <td></td>
    </tr>
  );
};

const DirectoryContents = ({ currentPath, onPathChange }) => {
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
              onPathChange={onPathChange}
            />
          ))}
          {directoryInfo["files"].map((info) => (
            <FileRow key={info.name} fileInfoUrl={info.link} />
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default DirectoryContents;
