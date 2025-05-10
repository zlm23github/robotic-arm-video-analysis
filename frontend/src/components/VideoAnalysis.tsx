import { Card, Spin, Typography, Button } from 'antd';
import { useState } from 'react';
import { analyzeVideo } from '../api/api';

const { Text } = Typography;

interface VideoAnalysisProps {
    selectedFile: string | null;
}

const parseDescriptionList = (desc: string) => {
    const match = desc.match(/```json\s*([\s\S]*?)\s*```/) || desc.match(/```[\s\S]*?```/);
    let jsonStr = match ? match[1].trim() : desc.trim();

    // parse jsonStr to array
    try {
        const arr = JSON.parse(jsonStr);
        if (Array.isArray(arr)) {
            return arr.map(
                (item: any) =>
                    `${item.start_time} - ${item.end_time} : ${item.description}`
            );
        }
    } catch (e) {
        return ["Not able to parse jsonStr to array", jsonStr];
    }
    return [jsonStr];
};

const VideoAnalysis: React.FC<VideoAnalysisProps> = ({ selectedFile }) => {
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<any>(null);
    const [error, setError] = useState<string | null>(null);

    const handleAnalyze = async () => {
        if (!selectedFile) return;

        try {
            setLoading(true);
            setError(null);
            const response = await analyzeVideo(selectedFile);
            setResult(response);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
            setResult(null);
        } finally {
            setLoading(false);
        }
    };

    if (!selectedFile) {
        return (
            <Card>
                <Text type="secondary">Please select a video file to analyze</Text>
            </Card>
        );
    }

    let displayLines: string[] = [];
    if (result && result.results && result.results[0]?.description) {
        displayLines = parseDescriptionList(result.results[0].description);
    }

    return (
        <Spin spinning={loading}>
            <Card>
                <Button 
                    type="primary" 
                    onClick={handleAnalyze}
                    loading={loading}
                >
                    Analyze Video
                </Button>
                
                {error ? (
                    <div style={{ marginTop: 16 }}>
                        <Text type="danger">{error}</Text>
                    </div>
                ) : displayLines.length > 0 ? (
                    <div style={{ marginTop: 16 }}>
                        {displayLines.map((line, idx) => (
                            <div key={idx} style={{ fontFamily: 'monospace' }}>{line}</div>
                        ))}
                    </div>
                ) : (
                    <div style={{ marginTop: 16 }}>
                        <Text>Click the button above to start analysis</Text>
                    </div>
                )}
            </Card>
        </Spin>
    );
};

export default VideoAnalysis;