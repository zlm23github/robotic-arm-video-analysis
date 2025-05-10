import { Layout, Typography, Card, Space } from 'antd';
import VideoUpload from './components/VideoUpload';
import VideoSelect from './components/VideoSelect';
import VideoAnalysis from './components/VideoAnalysis';
import { useState } from 'react';
import './App.css';

const { Header, Content } = Layout;
const { Title } = Typography;

function App() {
  const [selectedFile, setSelectedFile] = useState<string | null>(null);

  const handleFileSelect = (filename: string) => {
    setSelectedFile(filename);
  };

  return (
    <Layout>
      <Header>
        <Title level={3} style={{ color: 'white'}}>
          Analysis Video
        </Title>
      </Header>
      <Content style={{ padding: '24px' }}>
        <Space direction="vertical" size="large" style={{ width: '100%'}}>
          <Card title="Upload Video">
            <VideoUpload />
          </Card>
          <Card title="Select Video for Analysis">
            <VideoSelect onSelect={handleFileSelect} />
          </Card>
          <Card title="Preview Selected Video">
            {selectedFile ? (
              <video
                src={`http://localhost:8000/uploads/${selectedFile}`}
                controls
                style={{ width: '100%', maxHeight: 400, background: '#000' }}
              />
            ) : (
              <div style={{ color: '#888' }}>No video selected</div>
            )}
          </Card>
          <Card title="Analysis Result">
            <div >
              <VideoAnalysis selectedFile={selectedFile} />
            </div>
          </Card>
        </Space>
      </Content>
    </Layout>
  );
}

export default App;
