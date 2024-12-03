import React, { useState } from "react";

const FileUpload: React.FC = () => {
  const [selectedFiles, setSelectedFiles] = useState<FileList | null>(null);
  const [message, setMessage] = useState<string>("");
  const [isError, setIsError] = useState<boolean>(false);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      setSelectedFiles(event.target.files);
      setMessage("");
    }
  };

  const handleUpload = async () => {
    if (!selectedFiles) {
      setMessage("Please select a files to upload.");
      setIsError(true);
      return;
    }

    for (let i = 0; i < selectedFiles.length; i++) {
        const formData = new FormData();
        formData.append("file", selectedFiles[i]);
        
        try {
          const response = await fetch("http://127.0.0.1:5001/upload", {
            method: "POST",
            body: formData,
          });
    
          const result = await response.json();
    
          if (response.ok) {
            setMessage(result.message || "File uploaded successfully.");
            setIsError(false);
          } else {
            setMessage(result.error || "Failed to upload the file.");
            setIsError(true);
          }
        } catch (error) {
          console.error("Error uploading file:", error);
          setMessage("An error occurred while uploading the file.");
          setIsError(true);
        }
    }

  };

  return (
    <div className="flex flex-col items-center p-6 max-w-lg mx-auto bg-white rounded-lg shadow-md">
      <h1 className="text-2xl font-semibold mb-6">Upload a Text File</h1>
      <input
        type="file"
        accept=".txt"
        onChange={handleFileChange}
        className="mb-4 p-2 border border-gray-300 rounded-lg"
        multiple
      />
      <button
        onClick={handleUpload}
        className="px-4 py-2 bg-blue-500 text-white font-medium rounded-lg hover:bg-blue-600 focus:outline-none"
      >
        Upload
      </button>
      {message && (
        <p className={`mt-4 text-lg ${isError ? "text-red-500" : "text-green-500"}`}>
          {message}
        </p>
      )}
    </div>
  );
};

export default FileUpload;
