import { Fragment } from "react";
import { Link } from "react-router-dom";
import "./Breadcrumbs.css";

function getBreadcrumbs(path) {
  let components = path.split("/");
  let result = [{ relpath: "", name: "home" }];
  let currentPath = "";

  for (let i = 0; i < components.length; i++) {
    if (components[i]) {
      currentPath += (currentPath ? "/" : "") + components[i];
      result.push({ relpath: currentPath, name: components[i] });
    }
  }

  return result;
}

const Breadcrumbs = ({ currentPath }) => {
  const breadcrumbs = getBreadcrumbs(currentPath);
  return (
    <nav className="breadcrumbs header">
      {breadcrumbs.map((crumb, index) => (
        <Fragment key={index}>
          <Link to={`/${crumb["relpath"]}`} className="breadcrumb-item">
            {crumb["name"]}
          </Link>
          {index < breadcrumbs.length - 1 && (
            <span className="path-separator">/</span>
          )}
        </Fragment>
      ))}
    </nav>
  );
};

export default Breadcrumbs;
