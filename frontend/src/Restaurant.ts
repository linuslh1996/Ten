export enum RatingSite {
    TRIP_ADVISOR = "trip_advisor",
    GOOGLE_MAPS = "google_maps"
}


export interface SiteInfo {
    name: string;
    link: string;
    number_of_reviews: bigint;
    rating: number;
    site: RatingSite
}


export interface Restaurant {
    name: string;
    review: string;
    score: number;
    all_sites: Array<SiteInfo>;
}