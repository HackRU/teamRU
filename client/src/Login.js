import React, { Component } from "react";
import { httpClient } from "./handlers/axiosConfig.js";
import Cookies from "universal-cookie";
//import axios from "axios";

export default class Login extends Component {
  constructor() {
    super();
    this.state = {
      login: "",
      password: ""
    };
  }

  handleChange = event => {
    this.setState({
      [event.target.id]: event.target.value
    });
  };

  handleSubmit = event => {
    event.preventDefault();
    const request_data = {
      email: this.state.login,
      password: this.state.password
    };
    httpClient
      .post("/login", request_data)
      .then(response => {
        if (response.data.statusCode === 200) {
          //extract the body of the request
          const parsedData = JSON.parse(response.data.body);
          const cookies = new Cookies();
          //set cookies to now allow using the auth token from now on
          cookies.set("auth", parsedData.token, { path: "/" });
          cookies.set("email", request_data.email, { path: "/" });
          this.props.history.push({
            pathname: "/profile",
            state: { data: parsedData }
          });
        } else {
          alert(response.data.body);
        }
      })
      .catch(err => {
        console.error("An error occured while making the request");
      });
  };

  render() {
    return (
      <div className="LoginForm">
        <form onSubmit={this.handleSubmit}>
          <label>
            Username:
            <input
              type="text"
              id="username"
              name="username"
              value={this.state.login}
              onChange={this.handleChange}
            />
          </label>
          <br />
          <label>
            Password:
            <input
              type="password"
              id="password"
              name="password"
              value={this.state.password}
              onChange={this.handleChange}
            />
          </label>
          <br />
          <input type="submit" value="Submit" />
        </form>
        <h4>
          New user?
          <a
            href="https://hackru.org/signup"
            target="_blank"
            rel="noopener noreferrer"
          >
            Create an account.
          </a>
        </h4>
      </div>
    );
  }
}
