import React, { useEffect, useState, useRef } from 'react';
import { io, Socket } from "socket.io-client";
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { OrbitControls, Sphere, Html, Line } from '@react-three/drei';
import { animated, useSpring } from '@react-spring/web';
import { Vector3, CatmullRomCurve3, TextureLoader } from 'three';
import InfoBox from './InfoBox';
import NodeInfoBox from './NodeInfoBox';  // 追加
import './3Dtest.css';

const earthRadius = 5;

interface NodeProps {
  position: [number, number, number];
  info: any; // この型は具体的なオブジェクトの形状に合わせてください
  onClick: (info: any) => void; // この型も具体的なオブジェクトの形状に合わせてください
}

interface ConnectionProps {
  start: [number, number, number];
  end: [number, number, number];
  info: any;  // この行を追加
  color: string;
  delay?: number;
  onAnimationComplete?: () => void;  // この行を追加
}
const calculateSpherePoint = (lat:number, lon:number, radius:number) => {
  const phi = (90 - lat) * (Math.PI / 180);
  const theta = (lon + 180) * (Math.PI / 180);
  const x = -(radius * Math.sin(phi) * Math.cos(theta));
  const z = radius * Math.sin(phi) * Math.sin(theta);
  const y = radius * Math.cos(phi);
  return [x, y, z] as [number, number, number];
};

const Node: React.FC<NodeProps> = ({ position, info, onClick }) => {
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
      <AnimatedHtml style={animationProps}>
        <div style={{ color: 'white', background: 'rgba(0, 0, 0, 0.5)', padding: '10px', borderRadius: '5px', fontSize: '16px' }}>
          {info.info}
        </div>
      </AnimatedHtml>
    </mesh>
  );
};

const Connection: React.FC<ConnectionProps & { onAnimationComplete: () => void }> = ({ start, end, color, delay = 0, onAnimationComplete }) => {
  const [lineProgress, setLineProgress] = useState(0);
  const [points, setPoints] = useState<Vector3[]>([]);
  const [isDelayed, setIsDelayed] = useState(true);
  const [opacity, setOpacity] = useState(1); // 追加

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsDelayed(false);
    }, delay);
    return () => clearTimeout(timer);
  }, [delay]);

  const [offset, setOffset] = useState<number|null>(null);

  useEffect(() => {
    if (offset === null) {
      setOffset(Math.random() * 0.5 - 0.25); // -0.5から0.5の範囲でランダムな値を生成
    }
  }, [offset]);

  useFrame(() => {
    if (!isDelayed) {
      if (lineProgress < 1) {
        setLineProgress((prev) => Math.min(prev + 0.01, 1));
      } else {
        setOpacity(prev => Math.max(prev - 0.05, 0));  // フェードアウト
        if (opacity <= 0) {
          onAnimationComplete();
          setLineProgress(0);
          setOpacity(1); // 透明度をリセット
        }
      }
    }
  });

  useEffect(() => {
    if (offset !== null) {
      const midPoint = new Vector3(
        (start[0] + end[0]) / 2 + offset,
        (start[1] + end[1]) / 2 + offset,
        (start[2] + end[2]) / 2 + offset
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
      }
  }, [lineProgress, start, end]);
  
  useFrame(() => {
    if (!isDelayed) {
      if (lineProgress < 1) {
        setLineProgress((prev) => Math.min(prev + 0.01, 1));
      } else {
        onAnimationComplete();
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
          lineWidth={2}
          transparent  // 透明度を適用するためにはこのプロパティが必要です
          opacity={opacity}  // 透明度
        />
      )}
    </>
  );
};

const Earth = () => {
  const earthRef = useRef(null);
  const [earthTexture, setEarthTexture] = useState<THREE.Texture | null>(null);

  useEffect(() => {
    new TextureLoader().load('assets/earthspec1k.jpg', texture => {
      setEarthTexture(texture as any);
    });
  }, []);

  return (
    <mesh ref={earthRef} position={[0, 0, 0]}>
      <Sphere args={[earthRadius, 64, 64]}>
        {earthTexture && (
          <meshStandardMaterial map={earthTexture} />
        )}
      </Sphere>
    </mesh>
  );
};

const CameraController = () => {
  const { camera } = useThree();
  const controls = useRef<any>(null);
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

  return <OrbitControls ref={controls as any} autoRotate enablePan={false} />;
};
const generateUniqueId = () => '_' + Math.random().toString(36).substr(2, 9);

const Graph3D = () => {
  const [enableAutoRotate, setEnableAutoRotate] = useState(true);
  const [selectedNode, setSelectedNode] = useState(null);

  const [delayOffset, setdelayOffset] = useState<number>(0);

  useEffect(() => {
    if (delayOffset == 0) {
      setdelayOffset(Math.random()* 1000);
    }
  }, [delayOffset]);

  
  const handleOrbitControlsChange = () => {
    setEnableAutoRotate(false);
  };

  const handleNodeClick = (nodeInfo: any) => { // この型も具体的なオブジェクトの形状に合わせてください
    setSelectedNode(nodeInfo);
  };

  const handleAnimationComplete = (nodeId: string) => {
    setNodeData(prev => prev.filter(node => node.id !== nodeId));
  };

  const japanPosition = calculateSpherePoint(35.6895, 139.6917, earthRadius);
  const NoneSpherePosition = calculateSpherePoint(35.6895 + 2, 139.6917, earthRadius); // 日本の上空に位置
  const scaledNoneSpherePosition = NoneSpherePosition.map(coordinate => coordinate * 3) as [number, number, number]
  const [nodeData, setNodeData] = useState([{id:generateUniqueId(), IPaddr: "0.0.0.0", lat: 40.7128, lon: -74.0060, info: 'USA', color: 'white', delay: 0 ,action: "Sender"}]);
  useEffect(() => {
    const socket: Socket = io("http://192.168.2.195:8080");
    // サーバーからメッセージを受信したときの処理
    socket.on("message", (data: any) => {
      // console.log("Received data from server:", data);
      if (data["TALO"] != 0 || data["FIRE"] != 0){
        console.log("WARRNING:: ", data)
        data["color"] = "red"
      }
      if (document.visibilityState === 'visible') {
        setNodeData(prevNodeData => {
          if (prevNodeData.length > 100) {
            const filteredData = prevNodeData.filter((node, index, self) => {
              return self.findIndex(t => t.IPaddr === node.IPaddr  && t.action === node.action) === index;
            });
            return [...filteredData, {id:generateUniqueId(), IPaddr: data["IPaddr"], lat: data["lat"], lon: data["lon"], info: data["Country"], color: data["color"], delay: data["delay"], action: data["kinds"]}];
          }
          return [...prevNodeData,{id:generateUniqueId(), IPaddr: data["IPaddr"], lat: data["lat"], lon: data["lon"], info: data["Country"], color: data["color"], delay: data["delay"] ,action: data["kinds"]}]
        })
      }
      
    });

    // 接続が開かれたときの処理
    socket.on("connect", () => {
      console.log("Connected to server");
    });

    // 接続が閉じられたときの処理
    socket.on("disconnect", () => {
      console.log("Disconnected from server");
    });

    // コンポーネントがアンマウントされたときにSocketを閉じる
    return () => {
      socket.disconnect();
    };
  },[])
  return (
    <div style={{ position: 'relative', width: '100%', height: '100%' }}>
      <Canvas
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
        
        <Node position={japanPosition} info={{lat: 35.6895, lon: 139.6917, info: 'Japan' }} onClick={handleNodeClick} />
        <Node position={scaledNoneSpherePosition} info={{lat: 35.6895 + 2, lon: 139.6917, info: 'None' }} onClick={handleNodeClick} />
         {nodeData.map((node) => {
        const position = calculateSpherePoint(node.lat, node.lon, earthRadius);
        let start = node.action === 'Sender' ? japanPosition : position;
        let end = node.action === 'Sender' ? position : japanPosition;
        if (node.info === 'None') {
          end = NoneSpherePosition;
        }
        return (
          <React.Fragment key={node.id}>
            <Node position={position} info={node} onClick={handleNodeClick} />
            <Connection start={start} end={end} info={node.info} color={node.color} delay={node.delay} onAnimationComplete={() => handleAnimationComplete(node.id)} />
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
