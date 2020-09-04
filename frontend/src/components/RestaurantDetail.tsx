import {SiteInfo} from "../Restaurant";
import * as React from "react";
import makeStyles from "@material-ui/core/styles/makeStyles";
import Button from "@material-ui/core/Button";
import CardContent from "@material-ui/core/CardContent";
import {Typography} from "@material-ui/core";


const useStyles = makeStyles({
    container: {
        margin: 10
    },
    buttonMargin: {
        marginBottom: 10
    },
    newSiteMargin: {
        marginBottom: 25
    }
});


export function RestaurantDetail(props: {siteInfo: SiteInfo, site: string}) {
    const classes = useStyles();

    return <div className={classes.container}>
            <Button className={classes.buttonMargin} target="_blank" href={props.siteInfo.link} variant="outlined">{props.site}</Button>
            <Typography className={classes.newSiteMargin} variant="body2" color="textSecondary"> {props.siteInfo.number_of_reviews} reviews | {props.siteInfo.rating/2}/5  stars </Typography>
    </div>
}