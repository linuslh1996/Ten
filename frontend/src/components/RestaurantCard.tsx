import React from "react";
import {Restaurant} from "../Restaurant";
import {Card} from "@material-ui/core";
import CardContent from "@material-ui/core/CardContent";
import Typography from "@material-ui/core/Typography";
import CardActions from "@material-ui/core/CardActions";
import Button from "@material-ui/core/Button";
import makeStyles from "@material-ui/core/styles/makeStyles";

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

    return   <Card variant="outlined">
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
            <Button size="small">Learn More</Button>
        </CardActions>
    </Card>
}