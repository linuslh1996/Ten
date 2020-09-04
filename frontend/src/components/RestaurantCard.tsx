import React, {useEffect, useState} from "react";
import {Restaurant} from "../Restaurant";
import {Card, createMuiTheme, ThemeProvider} from "@material-ui/core";
import CardContent from "@material-ui/core/CardContent";
import Typography from "@material-ui/core/Typography";
import CardActions from "@material-ui/core/CardActions";
import Button from "@material-ui/core/Button";
import makeStyles from "@material-ui/core/styles/makeStyles";
import Collapse from "@material-ui/core/Collapse";
import {RestaurantDetail} from "./RestaurantDetail";
import * as blobUtil from "blob-util";
import CardMedia from "@material-ui/core/CardMedia";
import ImageViewer from "./ImageViewer";
import withStyles from "@material-ui/core/styles/withStyles";

const useStyles = makeStyles({
    quotationMarks: {
        fontFamily: "Arial",
        fontSize: 80,
        fontStyle: "italic",
        color: "lightgrey",
        marginBottom: -40
    },
    review: {
        marginLeft: 15
    }
});

const theme = createMuiTheme({
    typography: {
        h1: {
            fontSize: 32,
            fontWeight: 400
        },
        h4: {
            marginTop: 20,
            marginBottom: 20
        },
        body2: {
            fontSize: 20,
        }
    }});





export function RestaurantCard(props: {restaurant: Restaurant}): JSX.Element {
    const classes = useStyles();
    const [expanded, setExpanded] = useState(false);
    const handleExpandClick = () => {
        setExpanded(!expanded);
    };

    const reviewToDisplay = props.restaurant.google_maps_info.reviews.sort((review_1, review_2) => {
        if (review_1.length > review_2.length) {
            return -1
        } else {
            return 1
        }
    })[0];



    return  <Card variant="outlined">
        {/* Show Image and Review*/}
        <ImageViewer images={props.restaurant.google_maps_info.photos} />
        <ThemeProvider theme={theme}>
        <CardContent>
            <Typography variant="h1" color="textPrimary" gutterBottom>
                {props.restaurant.google_maps_info.name}
            </Typography>
            <div className={classes.quotationMarks}>"</div>
            <Typography className={classes.review} variant="body2" color="textSecondary">
                {reviewToDisplay}"
            </Typography>
        </CardContent>
        {/* Expand Action */}
        <CardActions>
            <Button size="small" onClick={handleExpandClick}>Learn More</Button>
        </CardActions>
        {/* Data When Expanded */}
        <Collapse in={expanded}>
        <CardContent>
            <Typography variant="h4"> Reviews: </Typography>
                <RestaurantDetail siteInfo={props.restaurant.google_maps_info} site="Google Maps"/>
                <RestaurantDetail siteInfo={props.restaurant.trip_advisor_info} site="Trip Advisor"/>
            <Typography variant="h4"> Address: </Typography>
                <Typography variant="body2" color="textSecondary">
                    {props.restaurant.google_maps_info.formatted_address}
                </Typography>
        </CardContent>
        </Collapse>
        </ThemeProvider>
    </Card>
}