import "./VisCanvas.css";

const ImgCanvas = ({ dataUrl }) => {
  return <img src={dataUrl} className="img-fluid" />;
};

const PdfCanvas = ({ dataUrl }) => {
  return (
    <embed
      src={`${dataUrl}#toolbar=0&navpanes=0&scrollbar=0`}
      type="application/pdf"
      className="pdf-canvas"
    />
  );
};

const VisCanvas = ({ canvasInfo }) => {
  // 'image', 'pdf', 'stl'
  if (canvasInfo.fileType === "image") {
    return (
      <div id="vis-panel">
        <ImgCanvas dataUrl={canvasInfo.dataUrl} />
      </div>
    );
  } else if (canvasInfo.fileType === "pdf") {
    return (
      <div id="vis-panel">
        <PdfCanvas dataUrl={canvasInfo.dataUrl} />
      </div>
    );
  } else {
    return <div id="vis-panel">{canvasInfo.dataUrl}</div>;
  }
};

export default VisCanvas;
