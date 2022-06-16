import React, { useState, useEffect, Component } from "react";
import {Grid, Card, Button, Typography, TableRow, TableCell} from "@material-ui/core";
import Navbar from "./Navbar";
import ReactApexChart from "react-apexcharts";

export default function Dashboard() {
  const [playlists, setPlaylists] = useState([])
  const [playlistsData, setPlaylistsData] = useState({})

  useEffect(() => {
    getUserPlaylists().then(data => setPlaylists(data.map((p) => {return {...p, clicked: false}})));
  }, [])

  async function getUserPlaylists() {
    return fetch("/api/user-playlists")
        .then((response) => response.json())
        .then((data) => {return data});
  }
  async function getPlaylistData(playlist_id) {
    return fetch('/api/playlist-boxplot/' + playlist_id)
        .then((response) => response.json())
        .then((data) => {return data})
  }
  async function playlistButtonClick(event) {
    let data = getPlaylistData(event.target.value);
    setPlaylistsData({...playlistsData, data});
    let newPlaylists = playlists
    newPlaylists[newPlaylists.findIndex(p => p.id === event.target.value)].clicked = true
    setPlaylists(newPlaylists)
  }

  return (
      <Card>
        <Navbar />
        <Grid container alignItems="center">
          <Grid item align="center" xs={2}>
            {playlists?.map((p) => (
                <Button value={p.id} onclick={playlistButtonClick} disabled={p.clicked} variant="outlined">{p.name}</Button>
              ))}
          </Grid>
          <Grid container align="center" xs={10}>
            <Grid item align="center" xs={6}>
              {['popularity','danceability', 'energy', 'loudness', 'speechiness'].map((f) => {
                return <BoxPlot name={f} data={playlistsData.map((p) => {
                  return {x: p.name, y: p[f]}
                })}/>
              })}
            </Grid>
            <Grid item align="center" xs={6}>
              {['acousticness', 'instrumentalness', 'liveness', 'tempo', 'valence'].map((f) => {
                return <BoxPlot name={f} data={playlistsData.map((p) => {
                  return {x: p.name, y: p[f]}
                })}/>
              })}
            </Grid>
          </Grid>
        </Grid>
      </Card>
  )
}

function BoxPlot(name, data) {
  function parseBoxFeatures(rawData) {
    return rawData.map((p) => {return {
      x: p.x, y: ['whiskerLow','quartile1','quartile2','quartile3','whiskerHigh'].map((val) => {return p.y[val]})
    }})
  }

  return (
      <div id="chart">
        <ReactApexChart
            series={[{type: 'boxPlot', data: parseBoxFeatures(data)}]}
            options={{
              chart: {type: 'boxPlot', height: 200},
              title: {text: name, align: 'center'},
              plotOptions: {boxPlot: {colors: {upper: '#5C4742', lower: '#A5978B'}}}
            }} />
      </div>
  )
}