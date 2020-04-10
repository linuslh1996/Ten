import React, {SyntheticEvent, useState} from "react";
import TextField from "@material-ui/core/TextField";


export function SearchBar(props: {onEnter: (searchTerm: string) => void}) {
    const [searchTerm, setSearchTerm] = useState("");


    const enterSubmit = (event: SyntheticEvent) => {
        event.preventDefault();
        props.onEnter(searchTerm);
    };

    const updateSearchTerm = (event) => {
        const value: string = event.target.value;
        setSearchTerm(value)
    };

    return <form onSubmit={enterSubmit} >
                <TextField id="outlined-basic" label="Search..." variant="outlined" margin="normal" fullWidth={true} onChange={updateSearchTerm}/>
            </form>
}