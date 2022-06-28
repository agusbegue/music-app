import React, {useState} from 'react';
import { makeStyles } from '@material-ui/core/styles';
import {Button, AppBar, Toolbar} from "@material-ui/core";
import Cookies from "js-cookie"
import SpotifyLogoBlack from "../../static/images/spotify-logo-black.png";
import getAuthHeader, {logoutFrontend} from "./auth";

const useStyles = makeStyles((theme) => ({
  toolBarTabs: {
    flexGrow: 1,
    textAlign: "left",
    alignItems: "center"
  },
  title: {
    textAlign: "center",
    fontSize: 36,
    color: "black",
    justifyContent: "center",
    alignItems: "center",
    textDecoration: "none",
    padding: "10px"
  },
  tab: {
    textAlign: "center",
    fontSize: 18,
    padding: "10px",
    color: "black"
  },
  logoutButton: {
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


  function logoutClick() {
    const csrftoken = Cookies.get('csrftoken');
    const requestOptions = {
      method: "POST",
      headers: { "Content-Type": "application/json", 'X-CSRFToken': csrftoken, ...getAuthHeader()},
      body: "{}",
    };
    fetch("/spotify/logout", requestOptions)
      .then((response) => {
        if (response.ok) {
          window.location.replace('/');
        }
      })
    logoutFrontend();
    window.location.replace('/login')
  }

  return (
    <div className={classes.root}>
      <AppBar className={classes.navbar}>
        <Toolbar>
          <div className={classes.toolBarTabs}>
            <a href="/" className={classes.title} >
              <img src={SpotifyLogoBlack} alt="spotify-logo" height="25" width="25" />
              <text className={classes.title}>MUSICALLY</text>
            </a>
            <a href='/charts' className={classes.tab} id="CHARTS">
              <text>MY CHARTS</text></a>
            <a href="/playlists" className={classes.tab} id="PLAYLISTS">
              <text>PLAYLISTS</text></a>
            <a href="/historic" className={classes.tab} id="HISTORIC">
              <text>HISTORIC</text></a>
          </div>
          <Button className={classes.logoutButton} onClick={logoutClick}>Logout</Button>
        </Toolbar>
      </AppBar>
    </div>
  );
}