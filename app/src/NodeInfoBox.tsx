import './NodeInfoBox.css'; // CSSファイルをインポート

const NodeInfoBox = ({ selectedNode }) => {
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