import React, {useState} from "react";
import {SearchBar} from "./SearchBar";
import {Container} from "@material-ui/core";
import Grid from "@material-ui/core/Grid";
import {RestaurantCard} from "./RestaurantCard";
import {Restaurant} from "../Restaurant";
import axios, {AxiosRequestConfig, AxiosResponse} from "axios"


async function getDataForTown(town: string): Promise<Array<Restaurant>> {
    const url: string = "http://localhost:5000/restaurants";
    const options: AxiosRequestConfig = {
        url: url,
        method: "GET",
        params: {
            town: town
        },
        headers: {
            'Access-Control-Allow-Origin': "*"
        }
    };
    const response: AxiosResponse = await axios(options);
    const restaurants: Array<Restaurant> = response.data;
    console.log(restaurants);
    return restaurants
}


export function App() {

    const [restaurants, setRestaurants] = useState([]);

    const onEnter = async (town: string) => {
        const restaurantTest: Array<Restaurant> = await getDataForTown(town);
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
