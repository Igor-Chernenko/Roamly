import { useState } from "react";

function ChatSidebar({ isOpen, onClose }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSend = async () => {
    const query = input.trim();
    if (!query) return;
    if (query.length > 500) {
      setMessages([...messages, { from: "system", text: " Query too long." }]);
      return;
    }

    const token = localStorage.getItem("token");
    if (!token) return;

    setMessages((prev) => [...prev, { from: "user", text: query }]);
    setInput("");
    setIsLoading(true);

    try {
      const res = await fetch("http://3.23.70.81:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ query }),
      });

      const data = await res.json();
      setMessages((prev) => [...prev, { from: "ai", text: data.response }]);
    } catch (err) {
      setMessages((prev) => [...prev, { from: "system", text: " Failed to fetch response." }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div
      className={`fixed top-0 right-0 h-full w-80 bg-white shadow-lg transform transition-transform duration-300 z-50
        ${isOpen ? "translate-x-0" : "translate-x-full"}`}
    >
      <div className="p-4 border-b flex justify-between items-center">
        <h2 className="text-lg font-semibold text-blue-700">Roamly Rabbit</h2>
        <button onClick={onClose} className="text-xl">
          ×
        </button>
      </div>

      {/* Vancouver Island disclaimer */}
      <div className="text-xs text-gray-500 px-4 py-2 border-b">
        As of Right now, you can only ask questions about hikes on Vancouver Island.
      </div>

      {/* Messages */}
      <div className="flex flex-col p-4 space-y-2 overflow-y-auto h-[70%]">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`px-3 py-2 rounded-lg max-w-[80%] ${
              msg.from === "user"
                ? "self-end bg-blue-500 text-white"
                : msg.from === "ai"
                ? "self-start bg-gray-200 text-gray-800"
                : "self-center text-red-500"
            }`}
          >
            {msg.text.split("\n").map((line, i) => (
              <p key={i}>{line}</p>
            ))}
          </div>
        ))}

        {/*Typing indicator */}
        {isLoading && (
          <div className="self-start text-sm text-gray-400 italic animate-pulse">
            Roamly Rabbit is thinking...
          </div>
        )}
      </div>

      {/* Input */}
      <div className="p-4 border-t flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a hiking question..."
          className="flex-1 p-2 border rounded"
        />
        <button
          onClick={handleSend}
          className="bg-blue-600 text-white px-3 py-2 rounded hover:bg-blue-700"
          disabled={isLoading}
        >
          Send
        </button>
      </div>
    </div>
  );
}

export default ChatSidebar;
