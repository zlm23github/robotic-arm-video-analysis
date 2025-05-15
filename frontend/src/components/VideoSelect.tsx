import { Select, Spin } from 'antd';
import { useEffect, useState } from 'react';
import { getVideoFiles } from '../api/api';

interface VideoSelectProps {
    onSelect: (filename: string) => void;
    refreshTrigger?: number;
}

const VideoSelect: React.FC<VideoSelectProps> = ({ onSelect, refreshTrigger = 0 }) => {
    const [files, setFiles] = useState<string[]>([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        const fetchFiles = async () => {
            try {
                setLoading(true);
                const response = await getVideoFiles();
                setFiles(response.files || []);
            } catch (error) {
                console.error('Error fetching video files:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchFiles();
    }, [refreshTrigger]);

    return (
        <Spin spinning={loading}>
            <Select
                style={{ width: 300 }}
                placeholder="Select a video file"
                onChange={onSelect}
                options={files.map(file => ({
                    label: file,
                    value: file
                }))}
            />
        </Spin>
    );
};

export default VideoSelect; 