import React, {SyntheticEvent, useState} from "react";
import TextField from "@material-ui/core/TextField";
import {AppBar, Toolbar, Typography} from "@material-ui/core";
import {makeStyles} from "@material-ui/core/styles";
import Autocomplete from '@material-ui/lab/Autocomplete';


const useStyles = makeStyles(theme => ({
    container: {
        textAlign: "center",
        width: "100%",
        height: "100%",
        flexGrow: 1
    },
    textField: {
        width: "50%",
        required: false,
        margin: 8
    },
    logo: {
        fontWeight: 500,
        marginLeft: 10
    }
}));


export function SearchBar(props: {onEnter: (searchTerm: string) => void, availableTowns: Array<string>}) {
    const [searchTerm, setSearchTerm] = useState("");
    const classes = useStyles();


    const enterSubmit = (event: SyntheticEvent) => {
        event.preventDefault();
        props.onEnter(searchTerm);
    };

    const updateSearchTerm = (event, value: string, reason: string) => {
        setSearchTerm(value)
    };

    return <AppBar position="sticky" color="inherit" >
            <Toolbar>
            <Typography className={classes.logo} variant="h4">
                Ten
            </Typography>
            <Autocomplete className={classes.container}
                          freeSolo = {true}
                          options={props.availableTowns}
                          onChange={updateSearchTerm}
                          onInputChange={updateSearchTerm}
                          renderInput={(params) => (
                              <div>
                                  <form style={{margin: 0}} onSubmit={enterSubmit} >
                                      <TextField {...params} className={classes.textField} label="Search..."
                                                 variant="outlined" margin="normal"
                                      />
                                  </form>
                              </div>
                          )}
            />
        </Toolbar>


    </AppBar>
}