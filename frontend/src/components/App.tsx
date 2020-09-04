import React, {useState} from "react";
import {SearchBar} from "./SearchBar";
import {CircularProgress, Container} from "@material-ui/core";
import Grid from "@material-ui/core/Grid";
import {RestaurantCard} from "./RestaurantCard";
import {Restaurant} from "../Restaurant";
import axios, {AxiosRequestConfig, AxiosResponse} from "axios"
import {makeStyles} from "@material-ui/core/styles";

const useStyles = makeStyles(theme => ({
    loadingSpinnerContainer: {
        textAlign: "center",
        marginTop: "10px"
    }
}));

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

function useAvailableTowns(): Array<string> {
    const [availableTowns, setAvailableTowns] = useState([]);
    if (availableTowns.length === 0) {
        const url: string = "http://localhost:5000/all_supported_towns";
        const options: AxiosRequestConfig = {
            url: url,
            method: "GET",
            headers: {
                'Access-Control-Allow-Origin': "*"
            }
        };
        axios(options).then(result => {
            setAvailableTowns(result.data)

        });
    }
    return availableTowns
}


export function App() {

    const [restaurants, setRestaurants] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const availableTowns: Array<string> = useAvailableTowns();
    const classes = useStyles();

    const onEnter = async (town: string) => {
        setIsLoading(true);
        const restaurantTest: Array<Restaurant> = await getDataForTown(town);
        setRestaurants(restaurantTest);
        setIsLoading(false);
    };

    const restaurantItems: Array<JSX.Element> = restaurants.map(restaurant => {
        return <Grid item sm={12}>
            <RestaurantCard restaurant={restaurant} />
        </Grid>
    });



    return <div>
        <SearchBar onEnter={onEnter} availableTowns={availableTowns}/>
        {isLoading && <div className={classes.loadingSpinnerContainer}> <CircularProgress /> </div>}
        {!isLoading && <Container maxWidth="md">
            <Grid style={{marginTop: "10px"}} container justify="center" spacing={3}>
                {restaurantItems}
            </Grid>
        </Container>}
    </div>

}
