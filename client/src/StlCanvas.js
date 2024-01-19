import React, { useRef, useEffect } from "react";
import * as THREE from "three";
import { TrackballControls } from "three/addons/controls/TrackballControls";
import { STLLoader } from "three/addons/loaders/STLLoader";
import "./StlCanvas.css";

const loadSTL = (url) => {
  return new Promise((resolve, reject) => {
    const loader = new STLLoader();
    loader.load(
      url,
      (geometry) => {
        const material = new THREE.MeshNormalMaterial();
        const mesh = new THREE.Mesh(geometry, material);
        resolve(mesh);
      },
      undefined,
      (error) => {
        reject(error);
      }
    );
  });
};

const computePositions = (camera, mesh) => {
  const bbox = new THREE.Box3().setFromObject(mesh);
  const center = bbox.getCenter(new THREE.Vector3());
  const size = bbox.getSize(new THREE.Vector3());
  const maxDim = Math.max(size.x, size.y, size.z);
  const fov = camera.fov * (Math.PI / 180);
  const radius = 3.5 * Math.abs((maxDim / 2) * Math.tan(fov * 2));
  const direction = new THREE.Vector3(0.61545745, -0.61545745, 0.49236596);
  const position = center.clone().addScaledVector(direction, radius);

  return {
    target: center,
    cameraPosition: position,
    cameraUp: new THREE.Vector3(0, 0, 1),
  };
};

const StlCanvas = ({ dataUrl }) => {
  const containerRef = useRef(null);
  const controlsRef = useRef(null);
  const initialViewRef = useRef(null);
  const scene = new THREE.Scene();

  useEffect(() => {
    const container = containerRef.current;
    const width = container.clientWidth;
    const height = container.clientHeight;

    const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer();
    renderer.setSize(width, height);
    // make the domElement have absolute position to avoid layout thrashing
    renderer.domElement.style.position = "absolute";
    container.appendChild(renderer.domElement);
    controlsRef.current = new TrackballControls(camera, renderer.domElement);

    loadSTL(dataUrl)
      .then((mesh) => {
        scene.add(mesh);
        const bbox = new THREE.Box3().setFromObject(mesh);
        const helper = new THREE.Box3Helper(bbox, 0xff0000);
        scene.add(helper);
        const positions = computePositions(camera, mesh);

        initialViewRef.current = {
          target: positions.target.clone(),
          cameraPosition: positions.cameraPosition.clone(),
          cameraUp: positions.cameraUp.clone(),
        };

        if (controlsRef.current) {
          controlsRef.current.target.copy(positions.target);
        }
        camera.position.copy(positions.cameraPosition);
        camera.up.copy(positions.cameraUp);
        controlsRef.current?.update();
      })
      .catch((error) => {
        console.error("Error loading STL file:", error);
      });

    const animate = () => {
      requestAnimationFrame(animate);
      if (controlsRef.current) {
        controlsRef.current.update();
      }
      renderer.render(scene, camera);
    };

    animate();

    const handleResize = () => {
      const width = container.clientWidth;
      const height = container.clientHeight;
      renderer.setSize(width, height);
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      controlsRef.current?.handleResize();
    };

    window.addEventListener("resize", handleResize);

    return () => {
      container.removeChild(renderer.domElement);
      window.removeEventListener("resize", handleResize);
    };
  }, [dataUrl]);

  const resetView = () => {
    if (controlsRef.current) {
      controlsRef.current.target.copy(initialViewRef.current.target);
      controlsRef.current.object.position.copy(
        initialViewRef.current.cameraPosition
      );
      controlsRef.current.object.up.copy(initialViewRef.current.cameraUp);
      controlsRef.current.update();
    }
  };

  return (
    <div
      ref={containerRef}
      style={{ width: "100%", height: "100%", position: "relative" }}
    >
      <button className="reset-button" onClick={resetView}>
        Reset View
      </button>
    </div>
  );
};

export default StlCanvas;
