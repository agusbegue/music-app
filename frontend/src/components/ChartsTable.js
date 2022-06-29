import React from "react";
import { Grid, Button, Typography } from "@material-ui/core";
import Navbar from "./Navbar";
import {Box, List, ListItem} from '@material-ui/core';
import {Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper} from '@material-ui/core';


export default function ChartsTable({'data': data}) {

  return (
    <Box sx={{ width: '50%' }}>
      <TableContainer component={Paper}>
          <Table sx={{ minWidth: 300 }} size='small' aria-label="a dense table">
            <TableHead>
              <TableRow>
                <TableCell align="center" colSpan={1}> </TableCell>
                <TableCell align="center" colSpan={3}>
                  Tracks
                </TableCell>
                <TableCell align="center" colSpan={3}>
                  Artists
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell>Rank</TableCell>
                <TableCell>Short term</TableCell>
                <TableCell>Medium term</TableCell>
                <TableCell>Long term</TableCell>
                <TableCell>Short term</TableCell>
                <TableCell>Medium term</TableCell>
                <TableCell>Long term</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {data?.map((values, index) => (
                <TableRow sx={{ '&:last-child td, &:last-child th': { border: 0 } }}>
                  <TableCell>{index+1}</TableCell>
                  <TableCell>{values?.tracks.shortTerm}</TableCell>
                  <TableCell>{values?.tracks.mediumTerm}</TableCell>
                  <TableCell>{values?.tracks.longTerm}</TableCell>
                  <TableCell>{values?.artists.shortTerm}</TableCell>
                  <TableCell>{values?.artists.mediumTerm}</TableCell>
                  <TableCell>{values?.artists.longTerm}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
      </TableContainer>
    </Box>
  );
}