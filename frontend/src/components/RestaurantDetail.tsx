import {SiteInfo} from "../Restaurant";
import * as React from "react";
import makeStyles from "@material-ui/core/styles/makeStyles";


const useStyles = makeStyles({
    capital: {
        textTransform: "capitalize"
    }
});


export function RestaurantDetail(props: {siteInfo: SiteInfo}) {
    const name: string = "Google Maps";
    const styles = useStyles();

    return <div>
            <p> <a href={props.siteInfo.link} target="_blank" rel="noopener noreferrer" className={styles.capital}>{name}</a>:
            <i> {props.siteInfo.number_of_reviews} Reviews. {props.siteInfo.rating}/10 stars </i> </p>
    </div>
}