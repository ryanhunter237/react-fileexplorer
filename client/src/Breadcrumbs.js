import "./Button.css";

function getBreadcrumbs(path) {
  let components = path.split("/");
  let result = [["", "home"]];
  let currentPath = "";

  for (let i = 0; i < components.length; i++) {
    if (components[i]) {
      currentPath += (currentPath ? "/" : "") + components[i];
      result.push([currentPath, components[i]]);
    }
  }

  return result;
}

const Breadcrumbs = ({ currentPath, onPathChange }) => {
  const breadcrumbs = getBreadcrumbs(currentPath);
  return (
    <nav aria-label="breadcrumb">
      <ol className="breadcrumb">
        {breadcrumbs.map((crumb, index) => (
          <li key={index} className="breadcrumb-item">
            <button
              type="button"
              className="directory-button"
              onClick={() => onPathChange(crumb[0])}
            >
              {crumb[1]}
            </button>
          </li>
        ))}
      </ol>
    </nav>
  );
};

export default Breadcrumbs;
