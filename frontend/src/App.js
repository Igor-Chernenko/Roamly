
import React, { useEffect, useState, useCallback } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
  useParams,
  useNavigate,
  useLocation,
  Outlet,
} from "react-router-dom";
import EditAdventurePage from "./components/EditAdventurePage";

const API_BASE = "http://127.0.0.1:8000";

function useAuth() {
  const token = localStorage.getItem("token");
  return !!token;
}
function RequireAuth() {
  const isAuthenticated = useAuth();
  const location = useLocation();
  return isAuthenticated ? <Outlet /> : <Navigate to="/user/login" state={{ from: location }} replace />;
}

function Sidebar({ isOpen, onClose }) {
  const navigate = useNavigate();
  const isSignedIn = useAuth();

  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);

  useEffect(() => {
    if (searchQuery.length < 2) {
      setSearchResults([]);
      return;
    }

    const delay = setTimeout(async () => {
      const res = await fetch(`http://127.0.0.1:8000/user?username=${encodeURIComponent(searchQuery)}&limit=5`);
      if (res.ok) {
        const data = await res.json();
        setSearchResults(data);
      }
    }, 300); // debounce

    return () => clearTimeout(delay);
  }, [searchQuery]);

  return (
    <div className={`fixed top-0 left-0 h-full w-64 bg-white shadow transform transition-transform duration-300 z-50 ${isOpen ? "translate-x-0" : "-translate-x-full"}`}>
      <div className="p-4 border-b flex justify-between items-center">
        <h2 className="text-lg font-semibold">Menu</h2>
        <div className="flex items-center space-x-2">
          <span className={`h-3 w-3 rounded-full ${isSignedIn ? "bg-green-500" : "bg-gray-400"}`}></span>
          <span className="text-sm">{isSignedIn ? "Signed in" : "Signed out"}</span>
        </div>
        <button onClick={onClose} className="text-xl">×</button>
      </div>

      <div className="p-4 space-y-4">
        {/* 🧭 Search bar */}
        <div>
          <input
            type="text"
            placeholder="Find Roamers..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-3 py-2 border rounded shadow-sm"
          />
          {searchResults.length > 0 && (
            <ul className="mt-2 bg-white border rounded shadow z-10 max-h-40 overflow-y-auto">
              {searchResults.map((user) => (
                <li
                  key={user.user_id}
                  onClick={() => {
                    navigate(`/user/${user.user_id}/profile`);
                    onClose();
                    setSearchQuery("");
                    setSearchResults([]);
                  }}
                  className="px-4 py-2 hover:bg-gray-100 cursor-pointer"
                >
                  @{user.username}
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Menu buttons */}
        <button onClick={() => { navigate("/about"); onClose(); }} className="text-blue-600 font-semibold w-full text-left">About</button>
        <button onClick={() => { navigate("/user/login"); onClose(); }} className="text-blue-600 font-semibold w-full text-left">Login</button>

        {isSignedIn && (
          <button
            onClick={() => {
              const token = localStorage.getItem("token");
              if (token) {
                const payload = JSON.parse(atob(token.split(".")[1]));
                navigate(`/user/${payload.user_id}/profile`);
                onClose();
              }
            }}
            className="text-blue-600 font-semibold w-full text-left"
          >
            View Profile
          </button>
        )}

        <button onClick={() => { navigate("/create-adventure"); onClose(); }} className="bg-blue-600 text-white rounded px-4 py-2 w-full">
          Create Adventure
        </button>
      </div>
    </div>
  );
}
function BackButton() {
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from;

  return (
    <button
      onClick={() => navigate(from || "/")}
      className="mb-4 text-blue-600 hover:underline text-sm"
    >
      ← Back
    </button>
  );
}

function MenuButton({ onClick }) {
  return (
    <button
      onClick={onClick}
      className="fixed top-4 left-4 z-50 p-2 rounded bg-white shadow hover:bg-gray-100"
    >
      <div className="space-y-1">
        <div className="w-6 h-0.5 bg-black"></div>
        <div className="w-6 h-0.5 bg-black"></div>
        <div className="w-6 h-0.5 bg-black"></div>
      </div>
    </button>
  );
}
function CreateAdventurePage({ setNotification }) {
  const navigate = useNavigate();
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [imageCaptionPairs, setImageCaptionPairs] = useState([
  { image: null, caption: "" },
  ]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const token = localStorage.getItem("token");
    if (!token) {
      navigate("/user/login");
      return;
    }

    const formData = new FormData();
    formData.append("title", title);
    formData.append("description", description);

    for (let pair of imageCaptionPairs) {
      if (pair.image) {
        formData.append("images", pair.image);
        formData.append("caption", pair.caption);
      }
    }

    const res = await fetch(`${API_BASE}/adventure/`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: formData,
    });

    if (res.ok) {
      setNotification("✅ Adventure posted!");
      navigate("/");
    } else {
      const err = await res.json();
      setNotification("❌ " + (err.detail || "Submission failed"));
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 py-10 px-6 max-w-2xl mx-auto">
      <BackButton />
      <h2 className="text-2xl font-bold mb-4">Create a New Adventure</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <input className="w-full p-2 border rounded" placeholder="Adventure Title" value={title} onChange={(e) => setTitle(e.target.value)} />
        <textarea className="w-full p-2 border rounded" placeholder="Adventure Description" value={description} onChange={(e) => setDescription(e.target.value)} />
        {imageCaptionPairs.map((pair, index) => (
          <div key={index} className="space-y-2 border p-4 rounded bg-white shadow">
            <input
              type="file"
              accept="image/*"
              onChange={(e) => {
                const file = e.target.files[0];
                setImageCaptionPairs((prev) => {
                  const updated = [...prev];
                  updated[index].image = file;
                  return updated;
                });
              }}
            />
            <textarea
              className="w-full p-2 border rounded"
              placeholder="Image Caption"
              value={pair.caption}
              onChange={(e) => {
                const value = e.target.value;
                setImageCaptionPairs((prev) => {
                  const updated = [...prev];
                  updated[index].caption = value;
                  return updated;
                });
              }}
            />
          </div>
        ))}

        <button
          type="button"
          onClick={() => setImageCaptionPairs([...imageCaptionPairs, { image: null, caption: "" }])}
          className="bg-gray-200 px-4 py-2 rounded hover:bg-gray-300 text-sm"
        >
          + Add Another Image
        </button>

        <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded font-semibold hover:bg-blue-700">Submit Adventure</button>
      </form>
    </div>
  );
}

function Notification({ message, onClose }) {
  useEffect(() => {
    const timer = setTimeout(onClose, 4000);
    return () => clearTimeout(timer);
  }, [onClose]);

  return (
    <div className="fixed top-5 right-5 bg-green-500 text-white px-4 py-2 rounded shadow z-50 flex items-center justify-between">
      <span>{message}</span>
      <button onClick={onClose} className="ml-4 font-bold">×</button>
    </div>
  );
}

function AdventureCard({ id, title, createdAt, owner, isEditable }) {
  const navigate = useNavigate();
  const location = useLocation();

  const cardContent = (
    <div
      onClick={() => navigate(`/adventures/${id}`, { state: { from: location.pathname } })}
      className={`cursor-pointer transition-transform transform hover:-translate-y-1 hover:shadow-lg
                 bg-white border border-gray-300 p-5 shadow-sm ${isEditable ? "rounded-l-lg flex-1 max-w-[80%]" : "rounded-lg w-full"}`}
    >
      <h2 className="text-xl font-semibold text-gray-900">{title}</h2>
      <p className="text-sm text-gray-600 mt-1">by {owner}</p>
      <p className="text-xs text-gray-400 mt-1">{new Date(createdAt).toLocaleString()}</p>
    </div>
  );

  return (
    <div className="flex mb-6">
      {cardContent}
      {isEditable && (
        <button
          onClick={() => navigate(`/adventures/${id}/edit`)}
          className="bg-blue-600 text-white px-4 py-2 rounded-r-lg hover:bg-blue-700 font-semibold flex items-center justify-center"
        >
          Edit
        </button>
      )}
    </div>
  );
}


function Home({ notification, clearNotification }) {
  const [adventures, setAdventures] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  useEffect(() => {
    const url = `${API_BASE}/adventure/?limit=10&search=${searchTerm}`;
    fetch(url)
      .then((res) => res.json())
      .then((data) => setAdventures(data))
      .catch((err) => console.error("Error fetching adventures:", err));
  }, [searchTerm]);

  return (
    <div className="min-h-screen bg-[#F4F4F2] font-[Outfit]">
      <MenuButton onClick={() => setIsSidebarOpen(true)} />
      <Sidebar isOpen={isSidebarOpen} onClose={() => setIsSidebarOpen(false)} />

      {notification && (
        <Notification message={notification} onClose={clearNotification} />
      )}

      <div className="max-w-3xl mx-auto px-6 py-12">
        <h1 className="text-4xl font-extrabold text-[#4A7C59] mb-6 tracking-tight">
          Roamly <span className="text-[#2F2F2F]">— Discover New Adventures</span>
        </h1>

        <input
          type="text"
          placeholder="🔍 Search for trails, peaks, or cities..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full px-4 py-3 mb-8 border border-[#DDE8D8] rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-[#4A7C59] bg-white placeholder:text-gray-400"
        />

        <div className="space-y-6">
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
            <p className="text-[#888] italic text-center">
              No adventures found. Try a different keyword!
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
function LoginPage({ setNotification }) {
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleLogin = async () => {
    const formData = new URLSearchParams();
    formData.append("username", identifier);
    formData.append("password", password);

    const res = await fetch(`${API_BASE}/user/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: formData,
    });

    const data = await res.json();
    if (res.ok) {
      localStorage.setItem("token", data.access_token);
      setNotification("✅ Logged in successfully!");
      navigate("/");
    } else {
      setNotification("❌ " + (data.detail || "Login failed"));
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 py-10 px-6 max-w-md mx-auto">
      <BackButton />
      <h2 className="text-2xl font-bold mb-4">Login</h2>

      <input
        className="w-full p-2 border rounded mb-3"
        placeholder="Email or Username"
        value={identifier}
        onChange={(e) => setIdentifier(e.target.value)}
      />
      <input
        type="password"
        className="w-full p-2 border rounded mb-3"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />

      <button
        onClick={handleLogin}
        className="w-full bg-blue-600 text-white rounded p-2 font-semibold hover:bg-blue-700"
      >
        Log In
      </button>

      <div className="mt-4 text-center">
        <p className="text-sm">Don't have an account?</p>
        <button
          onClick={() => navigate("/create-account")}
          className="text-blue-600 font-semibold mt-1"
        >
          Create a New Account
        </button>
      </div>
    </div>
  );
}


function ImageCarousel({ images }) {
  const [currentIndex, setCurrentIndex] = useState(0);

  const handlePrev = () => {
    setCurrentIndex((prevIndex) =>
      prevIndex === 0 ? images.length - 1 : prevIndex - 1
    );
  };

  const handleNext = () => {
    setCurrentIndex((prevIndex) =>
      prevIndex === images.length - 1 ? 0 : prevIndex + 1
    );
  };

  if (images.length === 0) return <p>No images found.</p>;

  return (
    <div className="relative w-full max-w-xl mx-auto mt-6">
      <img
        src={images[currentIndex].url}
        alt="Adventure"
        className="w-auto max-w-full max-h-[80vh] mx-auto object-contain rounded shadow mb-2"
      />
      <p className="text-center text-gray-700 italic mb-4">
        {images[currentIndex].caption || "No caption"}
      </p>
      <div className="flex justify-between">
        <button
          onClick={handlePrev}
          className="bg-blue-600 text-white px-4 py-1 rounded hover:bg-blue-700"
        >
          ← Prev
        </button>
        <button
          onClick={handleNext}
          className="bg-blue-600 text-white px-4 py-1 rounded hover:bg-blue-700"
        >
          Next →
        </button>
      </div>
    </div>
  );
}

function CreateAccountPage({ setNotification }) {
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

    const handleCreateAccount = async () => {
      const res = await fetch(`${API_BASE}/user/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, username, password }),
      });

      let data;
      try {
        data = await res.json();
      } catch (err) {
        data = { detail: "Unknown error" };
      }

      if (res.ok) {
        localStorage.setItem("token", data.jwt_token);
        setNotification("✅ Account created successfully!");
        navigate("/");
      } else {
        let message = "Failed to create account";
        if (Array.isArray(data.detail)) {
          // Pydantic-style validation errors
          message = data.detail.map((e) => `• ${e.msg}`).join("\n");
        } else if (typeof data.detail === "string") {
          message = data.detail;
        }
        setNotification("❌ " + message);
      }
    };


  return (
    <div className="min-h-screen bg-gray-100 py-10 px-6 max-w-md mx-auto">
      <BackButton />
      <h2 className="text-2xl font-bold mb-4">Create Account</h2>

      <input
        className="w-full p-2 border rounded mb-3"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <input
        className="w-full p-2 border rounded mb-3"
        placeholder="Username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
      />
      <input
        type="password"
        className="w-full p-2 border rounded mb-3"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />

      <button
        onClick={handleCreateAccount}
        className="w-full bg-blue-600 text-white rounded p-2 font-semibold hover:bg-blue-700"
      >
        Create User Account
      </button>
    </div>
  );
}
function AdventureDetail() {
  const { id } = useParams();
  const [adventure, setAdventure] = useState(null);
  const [images, setImages] = useState([]);
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState("");

  const fetchComments = useCallback(() => {
    fetch(`${API_BASE}/adventure/${id}/comments`)
      .then((res) => res.json())
      .then((data) => setComments(data))
      .catch((err) => console.error("Error fetching comments:", err));
  }, [id]);

  useEffect(() => {
    fetch(`${API_BASE}/adventure/${id}`)
      .then((res) => {
        if (!res.ok) throw new Error("Not found");
        return res.json();
      })
      .then((data) => setAdventure(data))
      .catch((err) => console.error("Error fetching adventure:", err));

    fetch(`${API_BASE}/adventure/images/${id}`)
      .then((res) => res.json())
      .then((data) => setImages(data))
      .catch((err) => console.error("Error fetching images:", err));

    fetchComments();
  }, [id, fetchComments]);
  const navigate = useNavigate();

  const handleAddComment = async () => {
    const token = localStorage.getItem("token");
    if (!token) {
      navigate("/user/login", { state: { from: `/adventures/${id}` } }); // optional: save redirect
      return;
    }

    if (!newComment.trim()) return;

    const res = await fetch(`${API_BASE}/adventure/${id}/comments`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ comment: newComment }),
    });

    if (res.ok) {
      setNewComment("");
      fetchComments();
    } else {
      const err = await res.json();
      alert(err.detail || "Failed to post comment");
    }
  };

  if (!adventure) {
    return <p className="text-center mt-10">Loading adventure...</p>;
  }

  return (
    <div className="min-h-screen bg-gray-100 py-10 px-6 max-w-2xl mx-auto">
      <BackButton />
      <h1 className="text-3xl font-bold mb-2">{adventure.title}</h1>
      <p className="text-sm text-gray-600 mb-4">by {adventure.owner.username}</p>
      <p className="text-sm text-gray-400 mb-4">
        Created: {new Date(adventure.created_at).toLocaleString()}
      </p>

      <ImageCarousel images={images} />

      <p className="mt-6 text-base text-gray-700 whitespace-pre-line">
        {adventure.description}
      </p>

      <h2 className="text-2xl font-semibold mt-10 mb-4">Comments</h2>

      <div className="mb-6">
        <textarea
          value={newComment}
          onChange={(e) => setNewComment(e.target.value)}
          placeholder="Add a comment..."
          className="w-full p-2 border rounded mb-2"
        />
        <button
          onClick={handleAddComment}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          Post Comment
        </button>
      </div>

      <div className="space-y-4">
        {comments.length > 0 ? (
          comments.map((comment) => (
            <div key={comment.comment_id} className="p-4 bg-white rounded shadow">
              <p className="text-sm font-semibold">@{comment.owner.username}</p>
              <p className="text-gray-700 mt-1">{comment.comment}</p>
            </div>
          ))
        ) : (
          <p className="text-gray-500">No comments yet.</p>
        )}
      </div>
    </div>
  );
}

function AboutPage() {
  return (
    <div className="min-h-screen bg-gray-50 py-10 px-6 max-w-3xl mx-auto">
      <BackButton />

      <div className="flex items-center space-x-4 mb-6">
          <img
            src="https://roamly-user-content.s3.us-west-2.amazonaws.com/Static/IMG_8061.jpg"
            alt="Igor Chernenko"
            style={{ width: "120px", height: "180px" }}
            className="rounded-[60%] object-contain shadow"
          />
        <div>
          <h1 className="text-3xl font-bold text-blue-800">About the Creator</h1>
          <p className="text-gray-600 text-sm italic">Igor Chernenko • Software Engineering @ UVic</p>
        </div>
      </div>

      <p className="mb-4 text-gray-700">
        I'm a third-year Software Engineering student at the University of Victoria. I built <strong>Roamly</strong> as a personal project to push myself beyond low-level programming into full-stack web development.
      </p>

      <ul className="list-disc list-inside mb-6 text-gray-700">
        <li>Built using FastAPI, PostgreSQL, and React</li>
        <li>Hosted on AWS (S3, EC2, RDS)</li>
        <li>Explores clean RESTful architecture</li>
        <li>Foundation for future Kafka / PySpark integrations</li>
      </ul>

      <p className="text-gray-700 mb-6">
        Roamly is a social platform where Roamers can post photos and stories of their outdoor adventures — and discover similar journeys from others.
      </p>

      <div className="bg-white rounded-lg p-4 shadow mb-6">
        <h3 className="text-xl font-semibold text-blue-700 mb-2">Contributing</h3>
        <p className="text-gray-700 mb-2">
          This is a solo developer project for now, but I’d love to connect with people interested in:
        </p>
        <ul className="list-disc list-inside text-gray-700">
          <li>FastAPI best practices</li>
          <li>Good frontend design (clearly it needs it)</li>
          <li>Kafka / PySpark data engineering</li>
          <li>Cloud-native architecture on AWS</li>
        </ul>
      </div>

      <div className="bg-white rounded-lg p-4 shadow">
        <h3 className="text-xl font-semibold text-blue-700 mb-2">Contact</h3>
        <p className="text-gray-700">Feel free to reach out if you’re a recruiter, engineer, or someone who just enjoys clever software:</p>
        <ul className="mt-2 text-blue-800">
          <li>Email: <a href="mailto:Igorchernenko1928@gmail.com" className="underline">Igorchernenko1928@gmail.com</a></li>
          <li>LinkedIn: <a href="https://linkedin.com/in/igor--chernenko" target="_blank" rel="noopener noreferrer" className="underline">linkedin.com/in/igor--chernenko</a></li>
          <li>GitHub: <a href="https://github.com/Igor-Chernenko" target="_blank" rel="noopener noreferrer" className="underline">@Igor-Chernenko</a></li>
        </ul>
      </div>
    </div>
  );
}

function UserProfilePage() {
  const { id } = useParams();
  const [adventures, setAdventures] = useState([]);
  const [userInfo, setUserInfo] = useState(null);
  const [error, setError] = useState(null);
  const [isOwnProfile, setIsOwnProfile] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("token");
    let currentUserId = null;

    try {
      if (token) {
        const payload = JSON.parse(atob(token.split(".")[1]));
        currentUserId = String(payload.user_id);
        if (currentUserId === id) {
          setIsOwnProfile(true);
        }
      }
    } catch (err) {
      console.warn("Invalid or missing JWT:", err);
    }

    fetch(`${API_BASE}/user/${id}`)
      .then((res) => {
        if (!res.ok) throw new Error("User not found");
        return res.json();
      })
      .then(setUserInfo)
      .catch((err) => setError(err.message));

    fetch(`${API_BASE}/user/${id}/adventures`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch adventures");
        return res.json();
      })
      .then(setAdventures)
      .catch((err) => setError(err.message));
  }, [id]);

  if (error) return <div className="text-red-500 text-center">{error}</div>;
  if (!userInfo) return <p className="text-center mt-10">Loading user...</p>;

  return (
    <div className="max-w-2xl mx-auto p-4">
      <BackButton />
      <h1 className="text-2xl font-bold mb-4">
        {isOwnProfile ? "Your Adventures" : `@${userInfo.username}'s Adventures`}
      </h1>
      {adventures.length === 0 ? (
        <p>No adventures posted yet.</p>
      ) : (
        adventures.map((adv) => (
          <AdventureCard
            key={adv.adventure_id}
            id={adv.adventure_id}
            title={adv.title}
            createdAt={adv.created_at}
            owner={userInfo.username}
            isEditable={isOwnProfile}
          />
        ))
      )}
    </div>
  );
}


function App() {
  const [notification, setNotification] = useState("");
  const clearNotification = () => setNotification("");
  useEffect(() => {
    localStorage.removeItem("token");
  }, []);
  return (
    <Router>
      {notification && <Notification message={notification} onClose={clearNotification} />}
      <Routes>
        <Route path="/" element={<Home notification={notification} clearNotification={clearNotification} />} />
        <Route path="/about" element={<AboutPage />} />
        <Route path="/user/login" element={<LoginPage setNotification={setNotification} />} />
        <Route path="/create-account" element={<CreateAccountPage setNotification={setNotification} />} />
        <Route element={<RequireAuth />}>
          <Route path="/create-adventure" element={<CreateAdventurePage setNotification={setNotification} />} />
        </Route>
        <Route element={<RequireAuth />}>
          <Route path="/user/:id/profile" element={<UserProfilePage />} />
          <Route path="/create-adventure" element={<CreateAdventurePage setNotification={setNotification} />} />
          <Route path="/adventures/:id/edit" element={<EditAdventurePage />} />
        </Route>
        <Route path="/adventures/:id" element={<AdventureDetail />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App;