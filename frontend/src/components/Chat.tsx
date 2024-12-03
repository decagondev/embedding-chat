import React, { useState } from "react";

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<{ role: string, content: string }[]>([]);
  const [userInput, setUserInput] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const handleUserInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setUserInput(event.target.value);
  };

  const handleSendMessage = async () => {
    if (!userInput.trim()) return;

    const userMessage = { role: "user", content: userInput };
    setMessages([...messages, userMessage]);
    setUserInput("");
    setIsLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:5001/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query: userInput, messages: messages }),
      });

      const data = await response.json();
      const assistantMessage = { role: "assistant", content: data.response || "No response received." };

      setMessages((prevMessages) => [...prevMessages, assistantMessage]);
    } catch (error) {
      console.error("Error fetching chat response:", error);
      setMessages((prevMessages) => [
        ...prevMessages,
        { role: "assistant", content: "An error occurred while fetching the response." },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center p-6 max-w-lg mx-auto bg-white rounded-lg shadow-md">
      <h1 className="text-2xl font-semibold mb-6">Chat with the Assistant</h1>
      
      <div className="w-full h-64 border p-4 mb-4 overflow-auto bg-gray-100 rounded-lg">
        <div className="flex flex-col space-y-4">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`p-2 max-w-xs rounded-lg ${message.role === "user" ? "bg-blue-500 text-white" : "bg-gray-200"}`}
              >
                {message.content}
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="p-2 max-w-xs bg-gray-300 text-gray-700 rounded-lg">Loading...</div>
            </div>
          )}
        </div>
      </div>

      <div className="flex w-full">
        <input
          type="text"
          value={userInput}
          onChange={handleUserInputChange}
          className="p-2 w-full border border-gray-300 rounded-l-lg"
          placeholder="Type your message..."
        />
        <button
          onClick={handleSendMessage}
          className="px-4 py-2 bg-blue-500 text-white font-medium rounded-r-lg hover:bg-blue-600 focus:outline-none"
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default Chat;
