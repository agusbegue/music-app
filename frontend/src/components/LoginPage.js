import React from "react";
import { Grid, Typography } from "@material-ui/core";
import Helmet from "react-helmet";
import SpotifyLoginButton from "./SpotifyLoginButton";
import SpotifyLogo from "../../static/images/spotify-neon.jpg";


export default function LoginPage() {

  function authenticateSpotify() {
    fetch("/spotify/get-auth-url")
      .then((response) => response.json())
      .then((data) => {
        window.location.replace(data.url);
    });
  }
  return (
    <Grid container spacing={6}>
      <Helmet>
        <style>{'body { background-color: black; }'}</style>
      </Helmet>
      <Grid item xs={12} align="center">
        <img src={SpotifyLogo} alt="spotify-logo-home" height="200" width="200" />
      </Grid>
      <Grid item xs={12} align="center">
        <h1>
          Music Party
        </h1>
      </Grid>
      <Grid item xs={12} align="center">
        <SpotifyLoginButton onClick={authenticateSpotify}/>
      </Grid>
      {/*<Grid item xs={12} align="center">*/}
      {/*  <ButtonGroup disableElevation variant="contained" color="primary">*/}
      {/*    <Button color="primary" to="/join" component={Link}>*/}
      {/*      Join a Room*/}
      {/*    </Button>*/}
      {/*    <Button color="default" to="/info" component={Link}>*/}
      {/*      Info*/}
      {/*    </Button>*/}
      {/*    <Button color="secondary" to="/create" component={Link}>*/}
      {/*      Create a Room*/}
      {/*    </Button>*/}
      {/*  </ButtonGroup>*/}
      {/*</Grid>*/}
    </Grid>
  )
}