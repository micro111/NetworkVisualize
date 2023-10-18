import './NodeInfoBox.css'; // CSSファイルをインポート

interface NodeInfoBoxProps {
  selectedNode: any; // この型は具体的なオブジェクトの形状に合わせてください
}
const NodeInfoBox: React.FC<NodeInfoBoxProps> = ({ selectedNode }) => {
  return (
    <div className="node-info-box">
      <div className="node-info-box-header">
        Node Information
      </div>
      <div className="node-info-box-content">
        {selectedNode ? (
          <>
            <p>Country: {selectedNode.info}</p>
            <p>Latitude: {selectedNode.lat}</p>
            <p>Longitude: {selectedNode.lon}</p>
          </>
        ) : (
          <p>Click a node to see information.</p>
        )}
      </div>
    </div>
  );
};

export default NodeInfoBox;