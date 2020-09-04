import React, {useLayoutEffect, useRef} from 'react';
import { makeStyles } from '@material-ui/core/styles';
import GridList from '@material-ui/core/GridList';
import GridListTile from '@material-ui/core/GridListTile';
import GridListTileBar from '@material-ui/core/GridListTileBar';
import IconButton from '@material-ui/core/IconButton';
import {Restaurant} from "../Restaurant";
import * as blobUtil from "blob-util";
import {isWidthUp, useMediaQuery} from "@material-ui/core";
import {Breakpoint} from "@material-ui/core/styles/createBreakpoints";
import useTheme from "@material-ui/core/styles/useTheme";

const useStyles = makeStyles((theme) => ({
    root: {
        display: 'flex',
        flexWrap: 'wrap',
        justifyContent: 'space-around',
        overflow: 'hidden',
        backgroundColor: theme.palette.background.paper,
    },
    gridList: {
        flexWrap: 'nowrap',
        // Promote the list into his own layer on Chrome. This cost memory but helps keeping high FPS.
        transform: 'translateZ(0)',
    },

}));


/**
 * The example data is structured as follows:
 *
 * import image from 'path/to/image.jpg';
 * [etc...]
 *
 * const tileData = [
 *   {
 *     img: image,
 *     title: 'Image',
 *     author: 'author',
 *   },
 *   {
 *     [etc...]
 *   },
 * ];
 */

function getImageURL(base64Encoded: string): string {
    const testBlob = blobUtil.base64StringToBlob(base64Encoded,"image/jpeg");
    const url: string = URL.createObjectURL(testBlob);
    return url
}



export default function ImageViewer(props: {images: Array<string>}) {
    const imagesWithUrl: Array<string> = props.images.map(image => getImageURL(image));

    const classes = useStyles();


    return (
        <div className={classes.root}>
            <GridList className={classes.gridList} cellHeight={350} cols={2.5}>
                {imagesWithUrl.map((image) => (
                   <GridListTile key={image} >
                            <img src={image} />
                    </GridListTile>
                ))}
            </GridList>
        </div>
    );
}