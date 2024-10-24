"use client";

import React, { useState, useRef, useEffect } from 'react';
import Button from './components/Button'; // Import the custom button
import "./globals.css";

export default function Chat() {
  const [messages, setMessages] = useState<{ sender: string, text: string }[]>([]);
  const [input, setInput] = useState('');
  const [isListening, setIsListening] = useState(false);
  const chatContainerRef = useRef<HTMLDivElement>(null);
  const recognitionRef = useRef<SpeechRecognition | null>(null);

  const handleSend = async () => {
    if (input.trim() === '') return;
    const newMessage = { sender: 'user', text: input };
    setMessages([...messages, newMessage]);
    setInput('');

    var target_api_url = 'http://localhost:8501/chat';
    try {
      const response = await fetch(target_api_url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ member_id: 2, question: input }),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      const botMessage = { sender: 'bot', text: data.answer_from_ai };
      setMessages((prevMessages) => [...prevMessages, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages]);

  useEffect(() => {
    if ('webkitSpeechRecognition' in window) {
      const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = 'ko-KR';
      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setInput(transcript);
        setIsListening(false);
      };
      recognition.onend = () => setIsListening(false);
      recognitionRef.current = recognition;
    } else {
      console.error('Speech recognition not supported in this browser.');
    }
  }, []);

  useEffect(() => {
    setMessages([{ sender: 'bot', text: '무엇을 도와드릴까요?' }]);
  }, []);

  const startRecognition = () => {
    if (recognitionRef.current) {
      setIsListening(true);
      recognitionRef.current.start();
    }
  };

  const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter') {
      event.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-pink-50 flex items-center justify-center">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-500 to-blue-600 text-white p-6">
        <h1 className="text-2xl font-bold">주인님, 만나서 반가워요!</h1>
        <p>오늘은 어떤 이야기를 나눌까 기대돼요!</p>
      </div>

      {/* Main Content - Grid layout for sections */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 p-6 flex-1">
        {/* Card 1 */}
        <div className="bg-white shadow-md rounded-lg p-6 text-center">
          <h2 className="text-lg font-semibold mb-4">연설문 작성에 도움 얻기</h2>
          <p>효과적인 연설문을 작성하는 데 필요한 자료를 제공합니다.</p>
        </div>
        {/* Card 2 */}
        <div className="bg-white shadow-md rounded-lg p-6 text-center">
          <h2 className="text-lg font-semibold mb-4">Copilot에 메시지 보내기</h2>
          <p>Copilot과 소통하여 아이디어를 발전시켜보세요.</p>
        </div>
        {/* Card 3 */}
        <div className="bg-white shadow-md rounded-lg p-6 text-center">
          <h2 className="text-lg font-semibold mb-4">음성 인식으로 입력하기</h2>
          <Button onClick={startRecognition}>
            {isListening ? "Listening..." : "Start Voice Recognition"}
          </Button>
        </div>
      </div>

      {/* Chat Section */}
      <div className="flex-1 flex flex-col items-center justify-start bg-[#FFFBF6] px-5 overflow-y-auto">
        <div
          className="flex-1 w-full max-w-3xl overflow-y-auto p-5 border border-gray-300 rounded-lg bg-white mt-5 mb-5"
          ref={chatContainerRef}
          style={{ minHeight: "400px" }} // Ensures consistent size
        >
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex items-center mb-3 ${message.sender === "user" ? "justify-end" : "justify-start"
                }`}
            >
              <div
                className={`max-w-[70%] p-4 rounded-lg ${message.sender === "user"
                  ? "bg-green-100"
                  : "bg-red-100"
                  }`}
              >
                <p>{message.text}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Chat Input - Always visible */}
        <div className="flex w-full max-w-3xl mb-5 fixed bottom-0 left-1/2 transform -translate-x-1/2 p-5 bg-[#FFFBF6]">
          <input
            className="flex-1 p-4 border border-gray-300 rounded-l-lg"
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="메시지를 입력하세요..."
          />
          <Button
            className="p-4 bg-blue-500 text-white rounded-r-lg"
            onClick={handleSend}
          >
            전송
          </Button>
        </div>
      </div>
    </div>
  );
}
