import React, { useState, useEffect, Component } from "react";
import {Grid, Card, Button } from "@material-ui/core";
import getAuthHeader from "./auth";
import Navbar from "./Navbar";
import ReactApexChart from "react-apexcharts";

export default function PlaylistsPage() {
  const [playlists, setPlaylists] = useState([])
  const [playlistsData, setPlaylistsData] = useState([])

  useEffect(() => {
    getUserPlaylists().then(data => setPlaylists(data.map((p) => {return {...p, clicked: false}})));
  }, [])

  async function getUserPlaylists() {
    return fetch("/api/user-playlists", {headers: getAuthHeader()})
      .then(response => response.json())
      .then(data => {return data});
  }
  function getPlaylistData(playlist_id) {
    return fetch('/api/playlist-boxplot/' + playlist_id, {headers: getAuthHeader()})
      .then(response => response.json())
      .then(data => {return data})
  }
  function playlistButtonClick(event) {
    let playlistId = event.currentTarget.value;
    let currPlaylist = playlists[playlists.findIndex(p => p.id === playlistId)];
    currPlaylist.clicked = true;
    setPlaylists(playlists);
    getPlaylistData(playlistId)
      .then(data => {setPlaylistsData(prevPlaylistData => [...prevPlaylistData, {...data, name: currPlaylist.name}])})
  }

  return (
      <Card>
        <Navbar />
        <Grid container alignItems="center">
          <Grid container direction="column" justifyContent="flex-start" alignItems="center" xs={2}>
            {playlists?.map((p) => (
                <Button value={p.id} onClick={playlistButtonClick} disabled={p.clicked} variant="outlined">{p.name}</Button>
              ))}
          </Grid>
          <Grid container align="center" xs={10}>
            <Grid item align="center" xs={4}>
              {['popularity','danceability'].map(f => {
                return <BoxPlot name={f} data={playlistsData.map(p => {
                  return {x: p.name, y: p[f]}
                })}/>
              })}
            </Grid>
            <Grid item align="center" xs={4}>
              {['acousticness', 'instrumentalness'].map(f => {
                return <BoxPlot name={f} data={playlistsData.map(p => {
                  return {x: p.name, y: p[f]}
                })}/>
              })}
            </Grid>
            <Grid item align="center" xs={4}>
              {['energy', 'speechiness'].map(f => {
                return <BoxPlot name={f} data={playlistsData.map(p => {
                  return {x: p.name, y: p[f]}
                })}/>
              })}
            </Grid>
          </Grid>
        </Grid>
      </Card>
  )
}

function BoxPlot({name: name, data: data}) {

  function calculateYLimits(rawData) {
    if (rawData.length === 0){
      return {min: 0, max: 1}
    }
    let min = Math.min.apply(Math, rawData.map(f => {return f.y['whiskerLow']}));
    let max = Math.max.apply(Math, rawData.map(f => {return f.y['whiskerHigh']}));
    let range = max - min
    return {min: min - range*0.1, max: max + range*0.1}
  }

  function parseBoxFeatures(rawData) {
    if (rawData.length!==0) {
      return rawData.map(p => {return {
        x: p.x, y: ['whiskerLow', 'quartile1', 'quartile2', 'quartile3', 'whiskerHigh'].map((val) => {
          return p.y[val]
        })
      }})
    } else {
      return []
    }
  }

  return (
      <div id="chart">
        <ReactApexChart
            series={[{type: 'boxPlot', data: parseBoxFeatures(data)}]}
            options={{
              chart: {type: 'boxPlot', height: 200},
              title: {text: name, align: 'center'},
              colors: ['#1DB954'],
              plotOptions: {boxPlot: {colors: {upper: '#8DD358', lower: '#A7E17C'}}},
              yaxis: {...calculateYLimits(data)}
            }} />
      </div>
  )
}