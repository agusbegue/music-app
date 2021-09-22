import React, { Component } from "react";
import RoomJoinPage from "./RoomJoinPage";
import CreateRoomPage from "./CreateRoomPage";
import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link,
  Redirect,
} from "react-router-dom";
import LandingPage from "./LandingPage";
import Dashboard from "./Dashboard";
import MyMusicPage from "./MyMusicPage";

export default class HomePage extends Component {
  constructor(props) {
    super(props);
    this.state = {
      authenticated: false,
      session_id: null,
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
                ? <Dashboard />
                : <LandingPage />}}
          />
          <PrivateRoute path="/join" component={RoomJoinPage} props={this.state}/>
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

function PrivateRoute ({'component': Component, 'authorized': authorized, props}) {
  return (
    <Route {...props}
      render={(props) => authorized === true
        ? <Component {...props} />
        : <Redirect to={{pathname: '/', state: {from: props.location}}} />}
    />
  )
}





