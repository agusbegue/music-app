import React, { useState, useEffect } from "react";
import {Grid, Card, Typography} from "@material-ui/core";
import Navbar from "./Navbar";
import ChartsTable from "./ChartsTable"
import getAuthHeader from "./auth";

export default function ChartsPage() {
  const [tableSize, setTableSize] = useState(20);
  const [timeRanges, setTimeRanges] = useState(['short_term','medium_term','long_term']);
  const [chartData, setChartData] = useState([]);

  useEffect(() => {
    getTableInformation()
    .then(data => {console.log(data); return data})
        .then(data => processTableInformation(data))
        .then(data => setChartData(data));
    // setTopTracks([{'shortTerm': 'Malefica', 'mediumTerm': 'Acaramelao', 'longTerm': 'High'}])
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
    let newChartData = [];
    for (let i=0; i<tableSize; i++) {
      newChartData.push({
        'tracks': {
          'shortTerm': topTracksTmp['short_term'][i],
          'mediumTerm': topTracksTmp['medium_term'][i],
          'longTerm': topTracksTmp['long_term'][i]
        },
        'artists': {
          'shortTerm': topArtistsTmp['short_term'][i],
          'mediumTerm': topArtistsTmp['medium_term'][i],
          'longTerm': topArtistsTmp['long_term'][i],
        }
      })
    }
    return newChartData
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
        <Typography>We asked Spotify, and these are some of your favourite artists and tracks...</Typography>
        <Grid container alignItems="flex-start">
          <Grid item align="center">
            <ChartsTable data={chartData} />
          </Grid>
        </Grid>
      </Card>
  )
}