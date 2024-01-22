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

const cleanScene = (scene) => {
  scene.traverse((object) => {
    if (object.isMesh) {
      if (object.geometry) {
        // is this not working?
        object.geometry.dispose();
      }
      if (object.material) {
        if (object.material.isMaterial) {
          cleanMaterial(object.material);
        } else {
          // an array of materials
          for (const material of object.material) cleanMaterial(material);
        }
      }
    }
  });
  scene.clear();
};

const cleanMaterial = (material) => {
  material.dispose();
  // dispose textures if any
  for (const key of Object.keys(material)) {
    const value = material[key];
    if (value && typeof value === "object" && "minFilter" in value) {
      value.dispose();
    }
  }
};

const StlCanvas = ({ dataUrl }) => {
  const containerRef = useRef(null);
  const controlsRef = useRef(null);
  const initialViewRef = useRef(null);
  const sceneRef = useRef(null);

  useEffect(() => {
    if (!sceneRef.current) {
      sceneRef.current = new THREE.Scene();
    }
    const scene = sceneRef.current;
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
      controlsRef.current?.update();
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
      window.removeEventListener("resize", handleResize);
      controlsRef.current?.dispose();
      cleanScene(scene);
      //   renderer.info.reset(); // maybe unnecessary
      // dispose of initialViewRef?
      container.removeChild(renderer.domElement);
      renderer.dispose();
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
