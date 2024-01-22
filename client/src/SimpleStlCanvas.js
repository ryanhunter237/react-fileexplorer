import React, { useRef, useEffect } from "react";
import * as THREE from "three";
import { STLLoader } from "three/addons/loaders/STLLoader";

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

const cleanScene = (scene) => {
  scene.traverse((object) => {
    if (object.isMesh) {
      if (object.geometry) {
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

const SimpleStlCanvas = ({ dataUrl }) => {
  const containerRef = useRef(null);
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

    loadSTL(dataUrl)
      .then((mesh) => {
        scene.add(mesh);
        camera.position.x = -30;
      })
      .catch((error) => {
        console.error("Error loading STL file:", error);
      });

    const animate = () => {
      requestAnimationFrame(animate);
      renderer.render(scene, camera);
    };

    animate();

    return () => {
      cleanScene(scene);
      //   renderer.info.reset(); // maybe unnecessary
      // dispose of initialViewRef?
      container.removeChild(renderer.domElement);
      renderer.dispose();
    };
  }, [dataUrl]);

  return (
    <div
      ref={containerRef}
      style={{ width: "100%", height: "100%", position: "relative" }}
    ></div>
  );
};

export default SimpleStlCanvas;
