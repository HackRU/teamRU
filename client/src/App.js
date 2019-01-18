import React, { Component } from "react";
//import logo from "./logo.svg";
import "./App.css";
import Login from "./components/Login.js";
import { BrowserRouter as Router, Route } from "react-router-dom";

class App extends Component {
  render() {
    return (
      <div className="App">
        <header className="App-header">
          <h1>TeamRU</h1>
          <Login />
        </header>
      </div>
    );
  }
}

export default App;
