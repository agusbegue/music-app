import React, { useState, useEffect } from "react";
import { Grid, Card } from "@material-ui/core";
import Navbar from "./Navbar";
import UserTopsTable from "./UserTopsTable"
import getAuthHeader from "./auth";

export default function ChartsPage() {
  const [tableSize, setTableSize] = useState(30);
  const [timeRanges, setTimeRanges] = useState(['short_term','medium_term','long_term']);
  const [topTracks, setTopTracks] = useState([]);
  const [topArtists, setTopArtists] = useState([]);

  useEffect(() => {
    // getTableInformation()
    // .then(data => {console.log(data); return data})
    //     .then(data => processTableInformation(data))
    //     .then(data => {
    //       setTopTracks(data['topTracks']);
    //       setTopArtists(data['topArtists']);
    //     });
    setTopTracks([{'shortTerm': 'Malefica', 'mediumTerm': 'Acaramelao', 'longTerm': 'High'}])
  }, [])

  async function getTableInformation() {
    let topTracksTmp = {};
    let topArtistsTmp = {};
    for (let i = 0; i < 3; i++) {
      topTracksTmp[timeRanges[i]] = await getUserTopTracks(timeRanges[i]);
      topArtistsTmp[timeRanges[i]] = await getUserTopArtists(timeRanges[i]);
    }
    return {'topTracks': topTracksTmp, 'topArtists': topArtistsTmp}
  }

  async function processTableInformation(data) {
    let topTracksTmp = data['topTracks'];
    let topArtistsTmp = data['topArtists'];
    let newTopTracks = [];
    let newTopArtists = [];
    for (let i=0; i<tableSize; i++) {
      newTopTracks.push({
        'shortTerm': topTracksTmp['short_term'][i],
        'mediumTerm': topTracksTmp['medium_term'][i],
        'longTerm': topTracksTmp['long_term'][i],
      })
      newTopArtists.push({
        'shortTerm': topArtistsTmp['short_term'][i],
        'mediumTerm': topArtistsTmp['medium_term'][i],
        'longTerm': topArtistsTmp['long_term'][i],
      })
    }
    return {'topArtists': newTopArtists, 'topTracks': newTopTracks}
  }

  async function getUserTopTracks(timeRange) {
    return await fetch("/api/user-top-tracks?" + new URLSearchParams({
      time_range: timeRange,
      amount: tableSize,
    }), {headers: getAuthHeader()})
        .then(response => response.json())
        .then(data => {
          return data
        });
  }
  async function getUserTopArtists(timeRange) {
    return fetch("/api/user-top-artists?" + new URLSearchParams({
      time_range: timeRange,
      amount: tableSize,
    }), {headers: getAuthHeader()})
        .then(response => response.json())
        .then(data => {
            return data
        });
  }

  return (
      <Card>
        <Navbar />
        <Grid container alignItems="center">
          <Grid item align="center" xs={4}>
            <UserTopsTable name='Artists' data={topArtists}/>
          </Grid>
          <Grid item align="center" xs={8}>
            <UserTopsTable name='Tracks' data={topTracks}/>
          </Grid>
        </Grid>
      </Card>
  )
}