import React, {useState} from 'react';
import { makeStyles } from '@material-ui/core/styles';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';
import IconButton from '@material-ui/core/IconButton';
import Grid from "@material-ui/core/Grid";
import MenuIcon from '@material-ui/icons/Menu';
import {Button} from "@material-ui/core";
import ArrowBack from "@material-ui/icons"
import Link from "@material-ui/core"
import Cookies from "js-cookie"
import SpotifyLogoBlack from "../../static/images/spotify-logo-black.png";

const useStyles = makeStyles((theme) => ({
  titleLink: {
    flexGrow: 1,
    textAlign: "left",
    justifyContent: "center",
    alignItems: "center",
    textDecoration: "none"
  },
  title: {
    textAlign: "center",
    fontSize: 30,
    color: "black"
  },
  button: {
    alignContent: "right",
    color: "black"
  },
  navbar: {
    background: '#1DB954',
    position: "sticky"
  }
}));

export default function Navbar() {
  const classes = useStyles();

  function userLogout() {
    const csrftoken = Cookies.get('csrftoken');
    const requestOptions = {
      method: "POST",
      headers: { "Content-Type": "application/json", 'X-CSRFToken': csrftoken},
      body: "{}",
    };
    fetch("/spotify/logout", requestOptions)
      .then((response) => {
        if (response.ok) {
          window.location.replace('/');
        }
      })
  }

  return (
    <div className={classes.root}>
      <AppBar className={classes.navbar}>
        <Toolbar>
          <a href="/" className={classes.titleLink}>
            <img src={SpotifyLogoBlack} alt="spotify-logo" height="25" width="25" />
            <text className={classes.title}> MusicParty</text>
          </a>
          <Button className={classes.button} onClick={userLogout}>Logout</Button>
        </Toolbar>
      </AppBar>
    </div>
  );
}