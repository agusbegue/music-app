import React from "react";
import { Grid, Button, Typography } from "@material-ui/core";
import Navbar from "./Navbar";
import {Box, List, ListItem} from '@material-ui/core';
import {Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper} from '@material-ui/core';


export default function UserTopsTable({'name': name, 'data': data}) {

  return (
    <Box sx={{ width: '50%' }}>
        <Typography component="h5" variant="h5">
          {name}
        </Typography>
      <TableContainer component={Paper}>
          <Table sx={{ minWidth: 300 }} size='small' aria-label="a dense table">
            <TableHead>
              <TableRow>
                <TableCell>Rank</TableCell>
                <TableCell>Short term</TableCell>
                <TableCell>Medium term</TableCell>
                <TableCell>Long term</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {data?.map((values, index) => (
                <TableRow sx={{ '&:last-child td, &:last-child th': { border: 0 } }}>
                  <TableCell>{index+1}</TableCell>
                  <TableCell>{values?.shortTerm}</TableCell>
                  <TableCell>{values?.mediumTerm}</TableCell>
                  <TableCell>{values?.longTerm}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
      </TableContainer>
    </Box>
  );
}