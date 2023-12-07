import React, { useEffect, useState } from "react";
import axios from "axios";

const DirectoryContents = ({ currentPath, onPathChange }) => {
  const [directoryInfo, setDirectoryInfo] = useState({ directories: [] });
  useEffect(() => {
    axios
      .get(`/api/directory-info/${currentPath}`)
      .then((response) => {
        setDirectoryInfo(response.data);
      })
      .catch((error) => console.error("Error fetching data:", error));
  }, [currentPath]);
  console.log(directoryInfo["directories"]);

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
          {directoryInfo["directories"].map((info, index) => (
            <tr key={index}>
              <td> {info["name"]} </td>
              <td></td>
              <td></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default DirectoryContents;
