// 📁 File: frontend/src/components/EditAdventurePage.jsx
import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

const API_BASE = "http://3.23.70.81:8000";

function EditAdventurePage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [adventure, setAdventure] = useState(null);
  const [images, setImages] = useState([]);
  const [newImages, setNewImages] = useState([{ image: null, caption: "" }]);

  useEffect(() => {
    const token = localStorage.getItem("token");
    fetch(`${API_BASE}/adventure/${id}`)
      .then((res) => res.json())
      .then(setAdventure);

    fetch(`${API_BASE}/adventure/images/${id}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => res.json())
      .then(setImages);
  }, [id]);

  const handleDeleteImage = async (imageId) => {
    const token = localStorage.getItem("token");
    const res = await fetch(`${API_BASE}/adventure/images/${imageId}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` },
    });
    if (res.ok) {
      const updated = await res.json();
      setImages(updated);
    }
  };

  const handleAddImages = async () => {
    const token = localStorage.getItem("token");
    for (let pair of newImages) {
      if (!pair.image) continue;
      const formData = new FormData();
      formData.append("caption", pair.caption);
      formData.append("image", pair.image);

      await fetch(`${API_BASE}/adventure/${id}/images`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });
    }
    navigate(`/adventures/${id}`);
  };
  const handleChangeCaption = async (imageId, newCaption) => {
    const token = localStorage.getItem("token");
    const res = await fetch(`${API_BASE}/adventure/images/${imageId}`, {
        method: "PUT",
        headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ caption: newCaption }),
    });

    if (res.ok) {
        const updatedImages = await res.json();
        setImages(updatedImages);
    } else {
        alert("Failed to update caption.");
    }
    };

  const handleDeleteAdventure = async () => {
    const token = localStorage.getItem("token");
    const res = await fetch(`${API_BASE}/adventure/${id}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` },
    });
    if (res.status === 204) navigate("/");
  };

  if (!adventure) return <p className="text-center mt-10">Loading adventure...</p>;

  return (
    <div className="min-h-screen bg-gray-100 py-10 px-6 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Edit Adventure</h1>

      <div className="mb-6">
        <h2 className="text-lg font-semibold mb-4">Uploaded Images</h2>
        <div className="space-y-4">
            {images.map((img, index) => (
            <div key={img.image_id} className="bg-white p-4 rounded shadow flex flex-col space-y-2">
                <img src={img.url} alt="" className="w-full max-h-64 object-contain rounded border" />
                <p className="text-sm text-gray-700"><strong>Caption:</strong> {img.caption || "No caption"}</p>

                <div className="flex items-center space-x-2">
                <button
                    onClick={() => handleDeleteImage(img.image_id)}
                    className="text-red-600 hover:underline text-sm"
                >
                    Delete
                </button>

                <button
                    onClick={() => {
                    const newCaption = prompt("Enter new caption:", img.caption || "");
                    if (newCaption !== null) {
                        handleChangeCaption(img.image_id, newCaption);
                    }
                    }}
                    className="text-blue-600 hover:underline text-sm"
                >
                    Change Caption
                </button>
                </div>
            </div>
            ))}
        </div>
        </div>

      <div className="mb-6">
        <h2 className="text-lg font-semibold mb-2">Add New Images</h2>
        {newImages.map((pair, i) => (
          <div key={i} className="space-y-2 mb-4 bg-white p-4 rounded shadow">
            <input
              type="file"
              accept="image/*"
              onChange={(e) => {
                const updated = [...newImages];
                updated[i].image = e.target.files[0];
                setNewImages(updated);
              }}
            />
            <textarea
              className="w-full p-2 border rounded"
              placeholder="Image caption"
              value={pair.caption}
              onChange={(e) => {
                const updated = [...newImages];
                updated[i].caption = e.target.value;
                setNewImages(updated);
              }}
            />
          </div>
        ))}
        <button onClick={() => setNewImages([...newImages, { image: null, caption: "" }])} className="bg-gray-300 px-4 py-2 rounded text-sm">
          + Add Another Image
        </button>
      </div>

      <div className="flex justify-between mt-6">
        <button onClick={handleAddImages} className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
          Save New Images
        </button>
        <button onClick={handleDeleteAdventure} className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700">
          Delete Adventure
        </button>
      </div>
    </div>
  );
}

export default EditAdventurePage;
