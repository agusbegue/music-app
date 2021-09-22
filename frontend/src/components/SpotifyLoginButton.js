import React from "react";
import { Grid, Button, Typography } from "@material-ui/core";
import { withStyles } from '@material-ui/core/styles';
import SpotifyLogoBlack from "../../static/images/spotify-logo-black.png"

const CustomButton = withStyles((theme) => ({
  root: {
    color: theme.palette.getContrastText("#1DB954"),
    backgroundColor: "#1DB954",
    '&:hover': {
      backgroundColor: "#009933",
    },
    fontFamily: "sans-serif",
    // width: "40%",
  },
}))(Button);


function SpotifyLoginButton(props) {
  return (
    <CustomButton to='/' onClick={props.onClick}>
      <Grid item xs={4} align="center">
        <img src={SpotifyLogoBlack} alt="spotify-logo" height="40" width="40" />
      </Grid>
      <Grid item xs={8} align="center">
        <Typography variant="button">
          Login with Spotify
        </Typography>
      </Grid>
    </CustomButton>
  )
}

export default SpotifyLoginButton