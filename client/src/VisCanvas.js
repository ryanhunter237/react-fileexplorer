const VisCanvas = ({ canvasInfo }) => {
  // 'image', 'pdf', 'stl'
  if (canvasInfo.fileType === "image") {
    return (
      <div id="vis-panel">
        <img src={canvasInfo.dataUrl} className="img-fluid" />
      </div>
    );
  }
  return <div id="vis-panel">{canvasInfo.dataUrl}</div>;
};

export default VisCanvas;
