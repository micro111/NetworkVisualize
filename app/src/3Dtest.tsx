import React, { useEffect, useState, useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Sphere, Html, Line } from '@react-three/drei';
import { animated, useSpring } from '@react-spring/web';
import { Vector3, CatmullRomCurve3 } from 'three';

const earthRadius = 5;

const calculateSpherePoint = (lat, lon, radius) => {
  const phi = (90 - lat) * (Math.PI / 180);
  const theta = (lon + 180) * (Math.PI / 180);
  const x = -(radius * Math.sin(phi) * Math.cos(theta));
  const z = radius * Math.sin(phi) * Math.sin(theta);
  const y = radius * Math.cos(phi);
  return [x, y, z];
};

const Node = ({ position, info }) => {
  const [hovered, setHovered] = useState(false);
  const animationProps = useSpring({ opacity: hovered ? 1 : 0 });
  const AnimatedHtml = animated(Html);

  return (
    <mesh
      position={position}
      onPointerOver={() => setHovered(true)}
      onPointerOut={() => setHovered(false)}
    >
      <Sphere args={[0.1]}>
        <meshStandardMaterial color={'lightblue'} />
      </Sphere>
      <AnimatedHtml style={animationProps} scaleFactor={10}>
        <div style={{ color: 'white', background: 'rgba(0, 0, 0, 0.5)', padding: '10px', borderRadius: '5px', fontSize: '16px' }}>
          {info}
        </div>
      </AnimatedHtml>
    </mesh>
  );
};


const Connection = ({ start, end, info, color }) => {
    const [visible, setVisible] = useState(true);
    const [hovered, setHovered] = useState(false);
    const animationProps = useSpring({ opacity: hovered ? 1 : 0 });
    const AnimatedHtml = animated(Html);
  
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
  
    const points = curve.getPoints(50);
  
    useEffect(() => {
      const timer = setTimeout(() => {
        setVisible(false);
      }, 5000);
      return () => clearTimeout(timer);
    }, []);
  
    return visible ? (
      <>
        <Line
          points={points}
          color={color}
          lineWidth={1}
          onPointerOver={() => setHovered(true)}
          onPointerOut={() => setHovered(false)}
        />
        {hovered && (
          <AnimatedHtml style={animationProps} position={end} scaleFactor={10}>
            <div style={{ color: 'white', background: 'rgba(0, 0, 0, 0.5)', padding: '10px', borderRadius: '5px', fontSize: '16px' }}>
              <h3>{info}</h3>
              <ul>
                <li>Name: John Doe</li>
                <li>Date: 2023-10-13</li>
              </ul>
            </div>
          </AnimatedHtml>
        )}
      </>
    ) : null;
  };
const Earth = () => {
  const earthRef = useRef();
  useFrame(() => {
    if (earthRef.current) {
      earthRef.current.rotation.y += 0.005;
    }
  });

  return (
    <mesh ref={earthRef}>
      <Sphere args={[earthRadius]}>
        <meshStandardMaterial color={'blue'} />
      </Sphere>
    </mesh>
  );
};

const Graph3D = () => {
  const japanPosition = calculateSpherePoint(35.6895, 139.6917, earthRadius);
  const nodeData = [
    { lat: 40.7128, lon: -74.0060, info: 'USA', color: 'red' },
    { lat: 39.9042, lon: 116.4074, info: 'China', color: 'green' },
    { lat: 41.9028, lon: 12.4964, info: 'Italy', color: 'blue' },
  ];

  return (
    <Canvas style={{ background: 'black' }}>
      <ambientLight />
      <pointLight position={[10, 10, 10]} />
      <OrbitControls />
      <Earth />
      <Node position={japanPosition} info="Japan" />
      {nodeData.map((node, idx) => {
        const position = calculateSpherePoint(node.lat, node.lon, earthRadius);
        return (
          <React.Fragment key={idx}>
            <Node position={position} info={node.info} />
            <Connection start={japanPosition} end={position} info={node.info} color={node.color} />
          </React.Fragment>
        );
      })}
    </Canvas>
  );
};

export default Graph3D;