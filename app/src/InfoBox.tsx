import React from 'react';
import './InfoBox.css';

interface DNSItem {
  name: string;
  connections: number;
  port: number;
}

const InfoBox: React.FC = () => {
  const dnsList: DNSItem[] = [
    { name: "Google", connections: 10, port: 80 },
    { name: "Google1", connections: 15, port: 443 },
    { name: "Google2", connections: 20, port: 8080 },
    { name: "Google3", connections: 25, port: 80 },
    { name: "Google4", connections: 30, port: 443 },
    { name: "Google5", connections: 35, port: 8080 },
    { name: "Google95", connections: 480, port: 80 },
    { name: "Google96", connections: 485, port: 443 },
    { name: "Google97", connections: 490, port: 8080 },
    { name: "Google98", connections: 495, port: 80 },
    { name: "Google99", connections: 500, port: 443 },
    { name: "Google95", connections: 480, port: 80 },
    { name: "Google96", connections: 485, port: 443 },
    { name: "Google97", connections: 490, port: 8080 },
    { name: "Google98", connections: 495, port: 80 },
    { name: "Google99", connections: 500, port: 443 },
    { name: "Google95", connections: 480, port: 80 },
    { name: "Google96", connections: 485, port: 443 },
    { name: "Google97", connections: 490, port: 8080 },
    { name: "Google98", connections: 495, port: 80 },
    { name: "Google99", connections: 500, port: 443 },
    { name: "Google95", connections: 480, port: 80 },
    { name: "Google96", connections: 485, port: 443 },
    { name: "Google97", connections: 490, port: 8080 },
    { name: "Google98", connections: 495, port: 80 },
    { name: "Google99", connections: 500, port: 443 },
    { name: "Google100", connections: 505, port: 8080 }
  ];

  return (
    <div className="info-box">
        <div className="info-box-header">
        <h3>接続先DNSリスト</h3>
        </div>
        <div className="info-box-content">
        <table>
            <thead>
            <tr>
                <th>名前</th>
                <th>接続回数</th>
                {/* <th>ポート番号</th> */}
            </tr>
            </thead>
            <tbody>
            {dnsList.map((item, index) => (
                <tr key={index}>
                <td>{item.name}</td>
                <td>{item.connections}</td>
                {/* <td>{item.port}</td> */}
                </tr>
            ))}
            </tbody>
        </table>
        </div>
    </div>
);
};

export default InfoBox;