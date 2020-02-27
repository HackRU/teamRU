import React from "react";
import MyNav from "./Components/MyNav";
import { BrowserRouter as Router, Switch, Route } from "react-router-dom";
import LandingPage from "./Components/LandingPage";
import TeamRecommendations from "./Components/Links/TeamRecommendations";
import ViewAllTeams from "./Components/Links/ViewAllTeams";
import MyProfile from "./Components/Links/MyProfile";
import LeaveMyTeam from "./Components/Links/TeamMenu/LeaveMyTeam";
import StartNewTeam from "./Components/Links/TeamMenu/StartNewTeam";
import ViewMyTeam from "./Components/Links/TeamMenu/ViewMyTeam";

function App() {
  return (
    <div>
      <MyNav />
      <Router>
        <div>
          <Switch>
            <Route path="/MyProfile">
              <MyProfile />
            </Route>
            <Route path="/LeaveMyTeam">
              <LeaveMyTeam />
            </Route>
            <Route path="/StartNewTeam">
              <StartNewTeam />
            </Route>
            <Route path="/ViewMyTeam">
              <ViewMyTeam />
            </Route>
            <Route path="/TeamRecommendations">
              <TeamRecommendations />
            </Route>
            <Route path="/ViewAllTeams">
              <ViewAllTeams />
            </Route>
            <Route path="/">
              <LandingPage />
            </Route>
          </Switch>
        </div>
      </Router>
    </div>
  );
}

export default App;
