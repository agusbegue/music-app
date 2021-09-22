import React, { Component } from "react";
import { render } from "react-dom";
import HomePage from "./HomePage";
import Toolbar from "@material-ui/core/Toolbar";
import IconButton from "@material-ui/core/IconButton";
import MenuIcon from "@material-ui/icons/Menu";
import {Button, CssBaseline, Typography} from "@material-ui/core";
import AppBar from "@material-ui/core/AppBar";

export default class App extends Component {
  constructor(props) {
    super(props);
  }

  render() {
    return (
      <HomePage />
    );
  }
}

const appDiv = document.getElementById("app");
render(<App />, appDiv);
