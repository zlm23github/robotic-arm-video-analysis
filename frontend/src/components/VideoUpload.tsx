import { message, Button, Input, Space, Spin } from "antd";
import { useState, useRef } from "react";
import { UploadOutlined, LinkOutlined } from "@ant-design/icons";
import { uploadVideo, uploadVideoUrl } from "../api/api";


const VideoUpload: React.FC = () => {
    const [loading, setLoading] = useState(false);
    const [videoUrl, setVideoUrl] = useState("");
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (!file) return;

        try {
            setLoading(true);
            const response = await uploadVideo(file);
            message.success("Video uploaded successfully");
            console.log(response);
        } catch (error) {
            message.error("Error uploading video: " + error);
            console.error("Error uploading video:", error);
        } finally {
            setLoading(false);
            // reset file input
            if (fileInputRef.current) {
                fileInputRef.current.value = "";
            }
        }
    };

    const handleUploadUrl = async () => {
        if (!videoUrl) {
            message.error("Please enter a video URL");
            return;
        }
        try {
            setLoading(true);
            const response = await uploadVideoUrl(videoUrl);
            message.success("Video uploaded successfully");
            console.log(response);
            setVideoUrl("");
            return response;
        } catch (error) {
            message.error("Error uploading video: " + error);
            console.error("Error uploading video:", error);
        } finally {
            setLoading(false);
        }
    };


    return (
        <Spin spinning={loading} tip="Uploading...">
            <Space direction="vertical" size="middle">
                <div>
                    <input
                        type="file"
                        accept="video/*"
                        onChange={handleUpload}
                        ref={fileInputRef}
                        style={{ display: 'none' }}
                    />
                    <Button 
                        icon={<UploadOutlined />} 
                        onClick={() => fileInputRef.current?.click()}
                    >
                        Upload Video
                    </Button>
                </div>
                
                <>Or</>
                
                <Space>
                    <Input
                        placeholder="Enter video URL"
                        value={videoUrl}
                        onChange={(e) => setVideoUrl(e.target.value)}
                        style={{ width: 300 }}
                    />
                    <Button 
                        icon={<LinkOutlined />} 
                        onClick={handleUploadUrl}
                    >
                        Upload from URL
                    </Button>
                </Space>
                
            </Space>
        </Spin>
    );
};

export default VideoUpload;