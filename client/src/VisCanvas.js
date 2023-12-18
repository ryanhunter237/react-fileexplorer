import StlCanvas from "./StlCanvas";
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
  let content;

  if (canvasInfo.fileType === "image") {
    content = <ImgCanvas dataUrl={canvasInfo.dataUrl} />;
  } else if (canvasInfo.fileType === "pdf") {
    content = <PdfCanvas dataUrl={canvasInfo.dataUrl} />;
  } else if (canvasInfo.fileType === "stl") {
    content = <StlCanvas dataUrl={canvasInfo.dataUrl} />;
  } else {
    content = canvasInfo.dataUrl;
  }

  return <div id="vis-panel">{content}</div>;
};

export default VisCanvas;
