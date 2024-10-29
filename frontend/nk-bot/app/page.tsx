"use client";
import Image from 'next/image'

import React, { useState, useRef, useEffect } from 'react';
import Button from './components/Button'; // Import the custom button
import "./globals.css";
import ReactMarkdown from 'react-markdown'

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

    var target_api_url = 'http://23.21.39.159:8501/chat';
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
    setMessages([{ sender: 'bot', text: '🐶 주인님, 만나서 반가워요!' }]);
  }, []);

  const startRecognition = () => {
    if (recognitionRef.current) {
      setIsListening(true);
      recognitionRef.current.start();
    }
  };

  const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter') {
      console.log('Enter key pressed');
      event.preventDefault();
      handleSend();
    } else {
      console.log(event.key);
    }
  };

  return (
    <div className="flex flex-col min-h-screen h-full items-center justify-center bg-gradient-to-b from-white to-pink-50 rounded-lg overflow-y-scroll no-scrollbar">
      <div className="flex fixed inset-0 items-end justify-end pr-10 pb-16">
        <Image
          className='rounded-lg'
          src="/pup_front.png"
          width={200}
          height={200}
          style={{ objectFit: "contain", opacity: 0.3 }}
          alt="background" />
      </div>

      <div className="flex-1 h-full w-full max-w-xl bg-transparent mt-8">
        <div className="flex-col justify-center mb-3 h-100"
          ref={chatContainerRef}
        >
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex items-center mb-3 ${message.sender === "user" ? "justify-end" : "justify-start"
                }`}
            >
              <div
                className={`max-w-[70%] p-4 rounded-lg ${message.sender === "user"
                  ? "bg-orange-100"
                  : "bg-transparent"
                  }`}
              >
                <div className="text-black whitespace-pre-line">
                  {message.text.split('\\n').map((line, index) => (
                    <p key={index}>{line}</p>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="fixed bottom-8 text-center mx-16">
          <div className="flex justify-center">
            <div className="bg-orange-50 bg-opacity-50 rounded-2xl shadow-lg p-2 flex items-center space-x-2 w-full max-w-md">
              {/* 입력 텍스트 박스 - 배경은 흰색 */}
              <input
                type="text"
                placeholder="복슬이한테 말하기"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                className="flex-grow bg-white text-gray-700 outline-none px-4 py-2 rounded-full"
              />
              {/* 마이크 버튼 - 오렌지 계열 투명 색상 */}
              <button className="text-black rounded-full p-2"
                onClick={startRecognition}>
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-6 w-6"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M12 14v7m0 0h-3m3 0h3m-6-7a3 3 0 106 0V7a3 3 0 10-6 0v7z"
                  />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
