"use client"

import React, { useState, useRef, useEffect } from 'react';
import "./globals.css";

export default function Experiment() {
  const [messages, setMessages] = useState<{ sender: string, text: string }[]>([]);
  const [input, setInput] = useState('');
  const [isListening, setIsListening] = useState(false);
  const chatContainerRef = useRef<HTMLDivElement>(null);
  const recognitionRef = useRef<SpeechRecognition | null>(null);

  const handleSend = async () => {
    if (input.trim() === '') return;
    console.log('Sending message:', input);
    const newMessage = { sender: 'user', text: input };
    setMessages([...messages, newMessage]);
    setInput('');

    var target_api_url = 'http://localhost:8501/chat'

    try {
      const response = await fetch(target_api_url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ member_id: 1, question: input }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('Web Response:', data);
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

      recognition.onend = () => {
        setIsListening(false);
      };

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
      event.preventDefault(); // 기본 엔터 동작 방지
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-screen">
      {/* <Navigation /> */}
      <div className="flex flex-1 overflow-hidden">
        {/* <div className="flex-8 bg-gray-200 p-4 overflow-y-auto" style={{ flex: 8 }}>
          <Dashboard />
        </div> */}
        <div className="flex-2 flex flex-col items-center justify-start flex-1 bg-white px-5 overflow-y-auto min-w-[400px] hidden sm:flex" style={{ flex: 2 }}>
          <div className="flex-1 w-full max-w-xl overflow-y-auto p-2.5 border border-gray-300 rounded-lg bg-gray-100 mt-5 mb-5" ref={chatContainerRef}>
            {messages.map((message, index) => (
              <div key={index} className={`flex items-center mb-2.5 ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className="mx-2.5">
                  {message.sender === 'user' ? '👤' : '🤖'}
                </div>
                <div className={`max-w-[70%] p-2.5 rounded-lg ${message.sender === 'user' ? 'bg-green-100' : 'bg-red-100'}`}>
                  <p>{message.text}</p>
                </div>
              </div>
            ))}
          </div>
          <div className="flex w-full max-w-xl mb-5">
            <input
              className="flex-1 p-2.5 border border-gray-300 rounded-l-md"
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="메시지를 입력하세요..."
            />
            <button className="p-2.5 bg-gradient-to-r from-white to-mint text-black border-none cursor-pointer" onClick={startRecognition}>
              🎤
            </button>
            <button className="p-2.5 bg-gradient-to-r from-white to-mint text-black border-none rounded-r-md cursor-pointer" onClick={handleSend}>
              전송
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}