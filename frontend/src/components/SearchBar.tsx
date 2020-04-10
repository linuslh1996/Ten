import React from "react";
import TextField from "@material-ui/core/TextField";
import {Restaurant} from "../Restaurant";


export function SearchBar(props: {onEnter: Function}) {
    const enterSubmit = (event) => {
        event.preventDefault();
        props.onEnter();
    };

    return <form onSubmit={enterSubmit} >
                <TextField id="outlined-basic" label="Search..." variant="outlined" margin="normal" fullWidth={true} />
            </form>
}