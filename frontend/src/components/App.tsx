import React, {useState} from "react";
import {SearchBar} from "./SearchBar";
import {Container} from "@material-ui/core";
import Grid from "@material-ui/core/Grid";
import {RestaurantCard} from "./RestaurantCard";
import {Restaurant} from "../Restaurant";




export function App() {

    const [restaurants, setRestaurants] = useState([]);

    const onEnter = () => {
        const restaurantTest: Array<Restaurant> = require("../data.json");
        setRestaurants(restaurantTest);
    };

    const restaurantItems: Array<JSX.Element> = restaurants.map(restaurant => {
        return <Grid item sm={12}>
            <RestaurantCard restaurant={restaurant} />
        </Grid>
    });

    return <Container maxWidth="md">
            <Grid container justify="center" spacing={3}>
                <Grid item sm={12}>
                    <SearchBar onEnter={onEnter}/>
                </Grid>
                {restaurantItems}
            </Grid>
        </Container>
}
