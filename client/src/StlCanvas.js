import React, { useEffect, useRef, useState } from "react";
import { Canvas, useLoader } from "@react-three/fiber";
import { PerspectiveCamera, TrackballControls } from "@react-three/drei";
import * as THREE from "three";
import { STLLoader } from "three/examples/jsm/loaders/STLLoader";
import "./StlCanvas.css";

const Model = ({ url, meshRef, onGeometryLoad }) => {
  console.log(`url = ${url}`);
  const geometry = useLoader(STLLoader, url);

  useEffect(() => {
    if (meshRef.current) onGeometryLoad(true);
  }, [meshRef, onGeometryLoad]);

  return (
    <mesh ref={meshRef} geometry={geometry}>
      <meshNormalMaterial />
    </mesh>
  );
};

const computeInitialControls = (meshRef, controlsRef) => {
  if (!meshRef.current || !controlsRef.current) return;

  const bbox = new THREE.Box3().setFromObject(meshRef.current);
  const center = bbox.getCenter(new THREE.Vector3());
  const camera = controlsRef.current.object;
  const size = bbox.getSize(new THREE.Vector3());
  const maxDim = Math.max(size.x, size.y, size.z);
  const fov = camera.fov * (Math.PI / 180);
  const radius = 0.5 * Math.abs((maxDim / 2) * Math.tan(fov * 2));
  const direction = new THREE.Vector3(0.61545745, -0.61545745, 0.49236596);
  const position = center.clone().addScaledVector(direction, radius);

  return {
    target: center,
    cameraPosition: position,
    cameraUp: new THREE.Vector3(0, 0, 1),
  };
};

const ControlsSetup = ({
  meshRef,
  controlsRef,
  isModelLoaded,
  onControlsSetup,
}) => {
  useEffect(() => {
    if (isModelLoaded) {
      const initialControls = computeInitialControls(meshRef, controlsRef);
      if (initialControls) {
        onControlsSetup(initialControls);

        controlsRef.current.target.copy(initialControls.target);
        controlsRef.current.object.position.copy(
          initialControls.cameraPosition
        );
        controlsRef.current.object.up.copy(initialControls.cameraUp);
        controlsRef.current.update();
      }
    }
  }, [meshRef, controlsRef, isModelLoaded, onControlsSetup]);

  return null;
};

const StlViewer = ({ dataUrl }) => {
  const meshRef = useRef();
  const controlsRef = useRef();
  const [isModelLoaded, setModelLoaded] = useState(false);
  const [initialControls, setInitialControls] = useState({
    target: new THREE.Vector3(),
    cameraPosition: new THREE.Vector3(),
    cameraUp: new THREE.Vector3(),
  });

  const handleResetControls = () => {
    if (controlsRef.current) {
      controlsRef.current.target.copy(initialControls.target);
      controlsRef.current.object.position.copy(initialControls.cameraPosition);
      controlsRef.current.object.up.copy(initialControls.cameraUp);
      controlsRef.current.update();
    }
  };

  return (
    <>
      <Canvas>
        <Model
          url={dataUrl}
          meshRef={meshRef}
          onGeometryLoad={setModelLoaded}
        />
        <PerspectiveCamera makeDefault={true} />
        <TrackballControls ref={controlsRef} />
        <ControlsSetup
          meshRef={meshRef}
          controlsRef={controlsRef}
          isModelLoaded={isModelLoaded}
          onControlsSetup={setInitialControls}
        />
      </Canvas>
      <button id="reset-button" onClick={handleResetControls}>
        Reset View
      </button>
    </>
  );
};

export default StlViewer;
