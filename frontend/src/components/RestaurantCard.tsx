import React, {useEffect, useState} from "react";
import {Restaurant} from "../Restaurant";
import {Card} from "@material-ui/core";
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

const useStyles = makeStyles({
    root: {
        minWidth: 275,
    },
    title: {
        fontSize: 24,
    },
    pos: {
        marginBottom: 12,
    },
});




export function RestaurantCard(props: {restaurant: Restaurant}): JSX.Element {
    const classes = useStyles();
    const [expanded, setExpanded] = useState(false);
    const height: number = 500;
    const handleExpandClick = () => {
        setExpanded(!expanded);
    };



    return   <Card variant="outlined">

        <ImageViewer images={props.restaurant.google_maps_info.photos} />

        <CardContent>
            <Typography className={classes.title} color="textPrimary" gutterBottom>
                {props.restaurant.google_maps_info.name}
            </Typography>
            <Typography className={classes.pos} color="textSecondary">
                {props.restaurant.google_maps_info.rating}
            </Typography>
            <Typography variant="body2" component="p" color="textSecondary">
                "{props.restaurant.google_maps_info.reviews[0]}"
            </Typography>
        </CardContent>

        <CardActions>
            <Button size="small" onClick={handleExpandClick}>Learn More</Button>
        </CardActions>

        <Collapse in={expanded}>
            <CardContent>
                    <RestaurantDetail siteInfo={props.restaurant.google_maps_info}/>
            </CardContent>
        </Collapse>
    </Card>
}