import React, { useState, useEffect, Component } from "react";
import {Grid, Card, Button, TextField } from "@material-ui/core";
import { Autocomplete } from "@material-ui/lab";
import getAuthHeader from "./auth";
import Navbar from "./Navbar";
import ReactApexChart from "react-apexcharts";

export default function HistoricPage() {
  const [selectedArtists, setSelectedArtists] = useState([]) // str
  const [artists, setArtists] = useState([]); // [{name: str, id: str}]
  const [artistsData, setArtistsData] = useState([]); // [{id: str, name: str, popularity: [{date: str, value: int}], releases: [{track: str, date: str}]}]
  const [plottedArtistsData, setPlottedArtistsData] = useState([]) // same as artistsDAta

  useEffect(() => {
    getArtists().then(data => setArtists(data));
  }, [])

  async function getArtists() {
    return fetch("/api/artists-all", {headers: getAuthHeader()})
      .then(response => response.json())
      .then(data => {return data});
    // return Promise.resolve([{name: "maria", id: "1"},{name: "nicki", id: "2"}])
  }

  async function getArtistData(artistId) {
    return await fetch('/api/artist-historic/' + artistId, {headers: getAuthHeader()})
      .then(response => response.json())
      .then(data => {return data})
  }

  async function searchButtonClick() {
    let newPlottedData = []
    for (const a of selectedArtists) {
      if (!artistsData.map(d => d.id).includes(a.id)) {
        await getArtistData(a.id)
          .then(data => {return {...data, name: a.name}})
          .then(data => {setArtistsData(prevData => [...prevData, data]); return data})
          .then(data => newPlottedData.push(data))
      } else {
        newPlottedData.push(artistsData[artistsData.findIndex(d => d.id === a.id)]);
      }
    }
    setPlottedArtistsData(newPlottedData);
  }

  return (
    <Card>
      <Navbar />
      <Grid container alignItems="center">
        <Grid item direction="column" justifyContent="flex-start" alignItems="center" xs={2}>
          <Autocomplete
            multiple
            id="search-artists"
            options={artists}
            value={selectedArtists}
            getOptionLabel={option => option.name}
            filterSelectedOptions
            getOptionSelected={(option, value) => option.id === value.id}
            style={{ width: 300 }}
            renderInput={params => (
              <TextField {...params} label="Artists" variant="outlined" />
            )}
            onChange={(event, newArtists) => {setSelectedArtists([...newArtists])}}
          />
          <Button onClick={searchButtonClick}>Search artists</Button>
        </Grid>
        <Grid item align="center" xs={10}>
          <HistoryPlot data={plottedArtistsData} />
        </Grid>
      </Grid>
    </Card>
  )
}


function HistoryPlot({data: data}) {

  function calculateYLimits(rawData) {
    if (rawData.length === 0){
      return {min: 0, max: 1}
    }
    let values = rawData.map(f => f['popularity'].map(p => p.value)).flat();
    let min = Math.min.apply(Math, values);
    let max = Math.max.apply(Math, values);
    let range = max - min
    return {min: min - range*0.2, max: max + range*0.2}
  }

  function parseHistory(rawData) {
    return rawData.map(a => {return {
      name: a.name, type: "line",
      data: a['popularity'].map(p => {return {
        x: new Date(p.date).getTime(), y: p.value
      }})
    }});
  }

  function parseReleases(rawData) {
    console.log(rawData);
    return rawData.map(a => {return {
      name: " ", type: "scatter",
      data: a['releases'].map(r => {return {
        x: new Date(r.date).getTime(),
        y: r.popularity,
        z: r.track
      }}),
    }})
  }
  function getColors(n) {
    return ["#00FF00","#0000FF","#FF7F50","#00FFFF"].slice(0, n)
  }

  return (
      <div id="chart">
        <ReactApexChart
          series={[...parseHistory(data), ...parseReleases(data)]}
          options={{
            chart: {type: 'line', width: "100%"},
            title: {text: "Popularity index", align: "center"},
            // fill: {type:'solid',},
            colors: getColors(data.length).concat(Array(data.length).fill("#FFFFFF")),
            markers: {
              size: Array(data.length).fill(0).concat(Array(data.length).fill(8)),
              colors: getColors(data.length).concat(getColors(data.length))
            },
            yaxis: {...calculateYLimits(data), tooltip: {enabled: false}},
            xaxis: {type: "datetime"},
            tooltip: {
              shared: false,
              intersect: true,
              // custom: function({series, seriesIndex, dataPointIndex, w}) {
              //   let point = w.globals.initialSeries[seriesIndex].data[dataPointIndex];
              //   return '<div class="arrow_box"><span>' + point.track + '</span></div>'
              // }
              y: {show: false, title: {formatter: (seriesName) => "Popularity:"}},
              z: {title: "Track name:"},
            },
            legend: {
              show: true,
            },
            }}
        />
      </div>
  )
}