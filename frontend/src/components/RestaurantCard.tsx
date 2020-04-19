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

function getImageURL(base64Encoded: string): string {
    const testBlob = blobUtil.base64StringToBlob(base64Encoded,"image/png");
    const url: string = URL.createObjectURL(testBlob);
    return url
}




export function RestaurantCard(props: {restaurant: Restaurant}): JSX.Element {
    const classes = useStyles();
    const [expanded, setExpanded] = useState(false);
    const imageURL: string = getImageURL(props.restaurant.images[0]);
    const height: number = 500;
    const handleExpandClick = () => {
        setExpanded(!expanded);
    };



    return   <Card variant="outlined">

        <CardMedia>
            <img src={imageURL} height={height}/>
        </CardMedia>

        <CardContent>
            <Typography className={classes.title} color="textPrimary" gutterBottom>
                {props.restaurant.name}
            </Typography>
            <Typography className={classes.pos} color="textSecondary">
                {props.restaurant.score}
            </Typography>
            <Typography variant="body2" component="p" color="textSecondary">
                "{props.restaurant.review}"
            </Typography>
        </CardContent>

        <CardActions>
            <Button size="small" onClick={handleExpandClick}>Learn More</Button>
        </CardActions>

        <Collapse in={expanded}>
            <CardContent>
                {props.restaurant.all_sites.map(site => {
                    return <RestaurantDetail siteInfo={site}/>
                })}
            </CardContent>
        </Collapse>
    </Card>
}