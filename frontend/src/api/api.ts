import axios from "axios";

const API_BASE_URL = "http://localhost:8000";

export const uploadVideo = async (file: File) => {
    const formData = new FormData();
    formData.append("video", file);
    const response = await axios.post(`${API_BASE_URL}/video/upload`, formData);
    return response.data;
};


export const uploadVideoUrl = async (url: string) => {
    const response = await axios.post(`${API_BASE_URL}/video/upload-url`, { url });
    return response.data;
};


export const analyzeVideo = async (filename: string) => {
    const response = await axios.post(`${API_BASE_URL}/video/analyze/${filename}`);
    return response.data;
};

export const getVideoFiles = async () => {
    const response = await axios.get(`${API_BASE_URL}/video/files`);
    return response.data;
};