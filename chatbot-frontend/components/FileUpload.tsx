'use client';
import { useState } from 'react';
import { fileAPI } from '@/lib/api';

export default function FileUpload() {
  const [uploading, setUploading] = useState(false);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    try {
      await fileAPI.upload(file);
      alert('File uploaded successfully!');
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div>
      <input
        type="file"
        id="file-upload"
        accept=".pdf,.docx,.txt"
        onChange={handleFileChange}
        className="hidden"
      />
      <label
        htmlFor="file-upload"
        className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg cursor-pointer inline-block"
      >
        {uploading ? 'Uploading...' : '📎 Upload'}
      </label>
    </div>
  );
}
