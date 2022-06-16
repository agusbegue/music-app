import React, { Component } from "react";
import RoomJoinPage from "./RoomJoinPage";
import CreateRoomPage from "./CreateRoomPage";
import Playlists from "./PlaylistsPage";
import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link,
  Redirect,
} from "react-router-dom";
import LoginPage from "./LoginPage";
import ChartsPage from "./ChartsPage";
import MyMusicPage from "./MyMusicPage";

export default class HomePage extends Component {
  constructor(props) {
    super(props);
    this.state = {
      authenticated: false,
    };
    this.checkAuthentication = this.checkAuthentication.bind(this)
  }

  async componentWillMount() {
    this.checkAuthentication()
  }

  checkAuthentication() {
    fetch("/spotify/is-authenticated")
    .then((response) => response.json())
    .then((data) => {
      this.setState({authenticated: data.is_authenticated});
    })
  }


  render() {
    return (
      <Router>
        <Switch>
          <Route exact path="/" render={() => {
              return this.state.authenticated
                ? <ChartsPage />
                : <LoginPage />}}
          />
          <PrivateRoute path="/playlists" component={Playlists} auth={this.state.authenticated} props={this.state}/>
          <PrivateRoute path="/join" component={RoomJoinPage} auth={this.state.authenticated} props={this.state}/>
          <PrivateRoute path="/create" component={CreateRoomPage} props={this.state}/>
          <PrivateRoute path="/my-music" component={MyMusicPage} props={this.state}/>
          {/*<PrivateRoute*/}
          {/*  path="/room/:roomCode"*/}
          {/*  render={(props) => {*/}
          {/*    return <Room {...props} leaveRoomCallback={} />;*/}
          {/*  }}*/}
          {/*/>*/}
        </Switch>
      </Router>
    );
  }
}

function PrivateRoute ({'component': Component, 'auth': authorized, ...rest}) {
  return (
    <Route {...rest}
      render={(props) => authorized === true
        ? <Component {...props} />
        : <Redirect to={{pathname: '/', state: {from: props.location}}} />}
    />
  )
}





