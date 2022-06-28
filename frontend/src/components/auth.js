import React, {Component} from "react";
import { Route } from "react-router-dom";
import Cookies from 'js-cookie'

const getAccessToken = () => Cookies.get('api_access_token')
const isAuthenticated = () => !!getAccessToken()
export default function getAuthHeader() {return {"Authorization": "Token " + getAccessToken()}}
export const logoutFrontend = () => Cookies.remove('api_access_token')

const authenticate = async () => {
  if (isAuthenticated()) {
      return true
  } else {
      window.location.replace('/login');
      return false
  }
}

export function PrivateRoute ({'component': Component, path, ...rest}) {
  return (
    <Route path={path} exact={rest.exact ? rest.exact : true} {...rest}
      render={(props) => isAuthenticated()
        ? <Component {...props} />
        : <AuthenticateBeforeRender render={() => <Component {...props} />} />
      }
    />
  )
}

class AuthenticateBeforeRender extends Component {
  state = { isAuthenticated: false }
  componentDidMount() {
    authenticate().then(isAuthenticated => {
      this.setState({ isAuthenticated })
    })
  }
  render() {
    return this.state.isAuthenticated ? this.props.render() : null
  }
}