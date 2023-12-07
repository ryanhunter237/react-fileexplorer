import "./Breadcrumbs.css";

function getBreadcrumbs(path) {
  let components = path.split("/");
  let result = [["", "."]];
  if (path == ".") return result;
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
          <li
            key={index}
            className={`breadcrumb-item ${
              index === breadcrumbs.length - 1 ? "active" : ""
            }`}
          >
            {index !== breadcrumbs.length - 1 ? (
              <button
                type="button"
                className="breadcrumb-link"
                onClick={() => onPathChange(crumb[0])}
              >
                {crumb[1]}
              </button>
            ) : (
              <span className="breadcrumb-link" style={{ cursor: "default" }}>
                {crumb[1]}
              </span>
            )}
          </li>
        ))}
      </ol>
    </nav>
  );
};

export default Breadcrumbs;
