import React from 'react';
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
    tile: {
        width: "100%",
        overflow: "hidden"
    },
    title: {
        color: theme.palette.primary.light,
    },
    titleBar: {
        background:
            'linear-gradient(to top, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0.3) 70%, rgba(0,0,0,0) 100%)',
    },
    imgStyle: {
        height: "100%"
    },
    fullHeight: {
        width: "100%"
    },
    fullWidth: {
        height: "100%",
        width: "auto"
    }
}));

function getGridListCols(width: Breakpoint) {
    if (isWidthUp('xl', width)) {
        return 4;
    }

    if (isWidthUp('lg', width)) {
        return 2.1;
    }

    if (isWidthUp('md', width)) {
        return 2.1;
    }

    return 0.9;
}

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

function useWidth() {
    const theme = useTheme();
    const keys = [...theme.breakpoints.keys].reverse();
    return (
        keys.reduce((output, key) => {
            // eslint-disable-next-line react-hooks/rules-of-hooks
            const matches = useMediaQuery(theme.breakpoints.up(key));
            return !output && matches ? key : output;
        }, null) || 'xs'
    );
}


export default function ImageViewer(props: {images: Array<string>}) {
    const imagesWithUrl: Array<string> = props.images.map(image => getImageURL(image));

    const classes = useStyles();

    return (
        <div className={classes.root}>
            <GridList className={classes.gridList} cellHeight={300} cols={getGridListCols(useWidth())}>
                {imagesWithUrl.map((image) => (
                    <GridListTile key={image} >
                            <img  src={image} />
                    </GridListTile>
                ))}
            </GridList>
        </div>
    );
}