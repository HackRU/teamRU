import React from "react";
import "../App.css";

const LandingPage = () => {
  return (
    <div className="App">
      <h1 className="App-header">
        LandingPage Component
        <a href="/MyProfile">
          <button>
            Make Profile
          </button>
        </a>
      </h1>
    </div>
  );
};

export default LandingPage;
