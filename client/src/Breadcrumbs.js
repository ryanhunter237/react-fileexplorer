import { Link } from "react-router-dom";
import "./Button.css";

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
    <nav aria-label="breadcrumb">
      <ol className="breadcrumb">
        {breadcrumbs.map((crumb, index) => (
          <li key={index} className="breadcrumb-item">
            <Link to={`/${crumb["relpath"]}`}>{crumb["name"]}</Link>
          </li>
        ))}
      </ol>
    </nav>
  );
};

export default Breadcrumbs;
