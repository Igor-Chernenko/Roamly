//  File: frontend/src/App.js
// This is the main app component. It fetches and displays the latest adventures

import { useEffect, useState } from "react";
import { BrowserRouter as Router, Route, Routes, Link } from "react-router-dom";

// A basic styled card that links to the full adventure page
function AdventureCard({ id, title, createdAt, owner }) {
  return (
    <div
      onClick={() => window.location.href = `/adventures/${id}`}
      className="cursor-pointer transition-transform transform hover:-translate-y-1 hover:shadow-lg
                 bg-white border border-gray-300 rounded-lg p-5 mb-6 shadow-sm"
    >
      <h2 className="text-xl font-semibold text-gray-900">{title}</h2>
      <p className="text-sm text-gray-600 mt-1">by {owner}</p>
      <p className="text-xs text-gray-400 mt-1">{new Date(createdAt).toLocaleString()}</p>
    </div>
  );
}

function Home() {
  const [adventures, setAdventures] = useState([]); // list of adventures
  const [searchTerm, setSearchTerm] = useState(""); // search input

  useEffect(() => {
    const url = `http://127.0.0.1:8000/adventure/?limit=10&search=${searchTerm}`;
    fetch(url)
      .then((res) => res.json())
      .then((data) => setAdventures(data))
      .catch((err) => console.error("Error fetching adventures:", err));
  }, [searchTerm]);

  return (
    <div className="min-h-screen bg-gray-100 py-10">
      <div className="max-w-2xl mx-auto px-6">
        <h1 className="text-3xl font-bold mb-6">Roamly - Explore Adventures</h1>

        <input
          type="text"
          placeholder="Search adventures..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full p-2 border mb-6 rounded"
        />

        {adventures.map((adv) => (
          <AdventureCard
            key={adv.adventure_id}
            id={adv.adventure_id}
            title={adv.title}
            createdAt={adv.created_at}
            owner={adv.owner.username}
          />
        ))}

        {adventures.length === 0 && (
          <p className="text-gray-500">No adventures found.</p>
        )}
      </div>
    </div>
  );
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        {/* You can later define the full adventure page here */}
      </Routes>
    </Router>
  );
}

export default App;