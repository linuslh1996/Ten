export enum RatingSite {
    TRIP_ADVISOR = "trip_advisor",
    GOOGLE_MAPS = "google_maps"
}


export interface SiteInfo {
    name: string;
    link: string;
    number_of_reviews: bigint;
    rating: number;
}


export interface Restaurant {
    google_maps_info: GoogleMapsInfo,
    trip_advisor_info: TripAdvisorInfo
}

export interface GoogleMapsInfo {
    name: string
    link: string
    number_of_reviews: bigint
    rating: number
    formatted_address: string
    location_lang: number
    location_lat: number
    photos: Array<string>
    reviews: Array<string>
}

export interface TripAdvisorInfo {
    name: string
    link: string
    number_of_reviews: bigint
    rating: number
}