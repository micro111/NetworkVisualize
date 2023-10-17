import React, { useEffect, useState, useRef } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { OrbitControls, Sphere, Html, Line } from '@react-three/drei';
import { animated, useSpring } from '@react-spring/web';
import { Vector3, CatmullRomCurve3, TextureLoader } from 'three';
import InfoBox from './InfoBox';
import NodeInfoBox from './NodeInfoBox';  // 追加
import './3Dtest.css';

const earthRadius = 5;

const calculateSpherePoint = (lat, lon, radius) => {
  const phi = (90 - lat) * (Math.PI / 180);
  const theta = (lon + 180) * (Math.PI / 180);
  const x = -(radius * Math.sin(phi) * Math.cos(theta));
  const z = radius * Math.sin(phi) * Math.sin(theta);
  const y = radius * Math.cos(phi);
  return [x, y, z];
};

const Node = ({ position, info, onClick }) => {
  const [hovered, setHovered] = useState(false);
  const animationProps = useSpring({ opacity: hovered ? 1 : 0 });
  const AnimatedHtml = animated(Html);

  return (
    <mesh
      position={position}
      onPointerOver={() => setHovered(true)}
      onPointerOut={() => setHovered(false)}
      onClick={() => onClick(info)}
    >
      <Sphere args={[0.1]}>
        <meshStandardMaterial color={'lightblue'} />
      </Sphere>
      <AnimatedHtml style={animationProps} scaleFactor={10}>
        <div style={{ color: 'white', background: 'rgba(0, 0, 0, 0.5)', padding: '10px', borderRadius: '5px', fontSize: '16px' }}>
          {info.info}
        </div>
      </AnimatedHtml>
    </mesh>
  );
};

const Connection = ({ start, end, info, color, delay = 0 }) => {
  const [lineProgress, setLineProgress] = useState(0);
  const [points, setPoints] = useState([]);
  const [isDelayed, setIsDelayed] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsDelayed(false);
    }, delay);
    return () => clearTimeout(timer);
  }, [delay]);

  useEffect(() => {
    const midPoint = new Vector3(
      (start[0] + end[0]) / 2,
      (start[1] + end[1]) / 2,
      (start[2] + end[2]) / 2
    );
    const length = midPoint.length();
    const scalingFactor = 2;
    midPoint.normalize().multiplyScalar(length * scalingFactor);

    const curve = new CatmullRomCurve3([
      new Vector3(...start),
      midPoint,
      new Vector3(...end),
    ]);

    const fullPoints = curve.getPoints(50);
    const newPoints = fullPoints.slice(0, Math.floor(lineProgress * fullPoints.length));
    setPoints(newPoints);
  }, [lineProgress, start, end]);

  useFrame(() => {
    if (!isDelayed) {
      if (lineProgress < 1) {
        setLineProgress((prev) => Math.min(prev + 0.01, 1));
      } else {
        setLineProgress(0);
      }
    }
  });

  return (
    <>
      {points.length > 0 && (
        <Line
          points={points}
          color={color}
          lineWidth={0.7}
        />
      )}
    </>
  );
};

const Earth = () => {
  const earthRef = useRef(null);
  const [earthTexture, setEarthTexture] = useState(null);

  useEffect(() => {
    new TextureLoader().load('assets/earthspec1k.jpg', texture => {
      setEarthTexture(texture);
    });
  }, []);

  return (
    <mesh ref={earthRef} position={[0, 0, 0]}>
      <Sphere args={[earthRadius, 64, 64]}>
        {earthTexture && (
          <meshStandardMaterial map={earthTexture} rotation={0} />
        )}
      </Sphere>
    </mesh>
  );
};

const CameraController = () => {
  const { camera } = useThree();
  const controls = useRef();
  let angle = 0;

  useFrame(() => {
    if (controls.current && !controls.current.autoRotate) {
      angle += 0.005;
      const x = 20 * Math.sin(angle);
      const z = 20 * Math.cos(angle);
      camera.position.set(x, 5, z);
      camera.lookAt(0, 0, 0);
    }
  });

  return <OrbitControls ref={controls} autoRotate enablePan={false} />;
};

const Graph3D = () => {
  const [enableAutoRotate, setEnableAutoRotate] = useState(true);
  const [selectedNode, setSelectedNode] = useState(null);

  const handleOrbitControlsChange = () => {
    setEnableAutoRotate(false);
  };

  const handleNodeClick = (nodeInfo) => {
    setSelectedNode(nodeInfo);
  };

  const japanPosition = calculateSpherePoint(35.6895, 139.6917, earthRadius);
  const nodeData = [
    { lat: 40.7128, lon: -74.0060, info: 'USA', color: 'red', delay: 0 },
    { lat: 39.9042, lon: 116.4074, info: 'China', color: 'green', delay: 1000 },
    { lat: 41.9028, lon: 12.4964, info: 'Italy', color: 'blue', delay: 2000 },
  ];

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%' }}>
      <Canvas
        antialias={"true"}
        style={{ background: 'black' }}
        camera={{ position: [0, 0, 20], fov: 50 }}
      >
        <ambientLight />
        <pointLight position={[10, 10, 10]} />
        <OrbitControls
          enableRotate={enableAutoRotate}
          enableZoom={true}
          enablePan={false}
          enableDamping={true}
          dampingFactor={0.25}
          rotateSpeed={0.5}
          zoomSpeed={0.8}
          onChange={handleOrbitControlsChange}
        />
        <Earth />
        <Node position={japanPosition} info={{ lat: 35.6895, lon: 139.6917, info: 'Japan' }} onClick={handleNodeClick} />
        {nodeData.map((node, idx) => {
          const position = calculateSpherePoint(node.lat, node.lon, earthRadius);
          return (
            <React.Fragment key={idx}>
              <Node position={position} info={node} onClick={handleNodeClick} />
              <Connection start={japanPosition} end={position} info={node.info} color={node.color} delay={node.delay} />
            </React.Fragment>
          );
        })}
        <CameraController />
      </Canvas>
      <div className="InfoBox-wrapper">
        <InfoBox />
      </div>
      <div className="NodeInfoBox-wrapper">
        <NodeInfoBox selectedNode={selectedNode} />
      </div>
    </div>
  );
};

export default Graph3D;
