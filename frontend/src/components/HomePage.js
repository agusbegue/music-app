import React, { Component } from "react";
import { BrowserRouter as Router, Switch, Route, Redirect } from "react-router-dom";
import { PrivateRoute } from "./auth";
import LoginPage from "./LoginPage";
import ChartsPage from "./ChartsPage";
import PlaylistsPage from "./PlaylistsPage";
import HistoricPage from "./HistoricPage";

export default class HomePage extends Component {
  constructor(props) {
    super(props);
  }

  render() {
    return (
      <Router>
        <Switch>
          <Route exact path="/login" component={LoginPage} />
          <Route exact path="/" render={() => {
              return <Redirect to='/charts' />}}
          />
          <PrivateRoute path="/charts" component={ChartsPage} />
          <PrivateRoute path="/playlists" component={PlaylistsPage} />
          <PrivateRoute path="/historic" component={HistoricPage} />
          {/*<PrivateRoute path="/time-series" component={TimeSeriesPAge} />*/}
        </Switch>
      </Router>
    );
  }
}





