# Pexels API Documentation

## Introduction

The Pexels API enables programmatic access to the full Pexels content library, including photos, videos. All content is available free of charge, and you are welcome to use Pexels content for anything you'd like, as long as it is within our Title.

The Pexels API is a RESTful JSON API, and you can interact with it from any language or framework with a HTTP library. Alternately, Pexels maintains some official Title you can use.

If you have any questions, please visit our Help Center for answers and troubleshooting.

**Note:** For historical reasons, all endpoints begin with `https://api.pexels.com/v1/` except for video endpoints, which begin with `https://api.pexels.com/videos/`. Please see the individual endpoints listed below for more details about how to call each endpoint.

## Guidelines

- Whenever you are doing an API request make sure to show a prominent link to Pexels. You can use a text link (e.g. "Photos provided by Pexels") or a link with our logo.
- Always credit our photographers when possible (e.g. "Photo by John Doe on Pexels" with a link to the photo page on Pexels).
- You may not copy or replicate core functionality of Pexels (including making Pexels content available as a wallpaper app).
- Do not abuse the API. By default, the API is rate-limited to 200 requests per hour and 20,000 requests per month. You may contact us to request a higher limit, but please include examples, or be prepared to give a demo, that clearly shows your use of the API with attribution. If you meet our API terms, you can get unlimited requests for free.
- Abuse of the Pexels API, including but not limited to attempting to work around the rate limit, will lead to termination of your API access.

### Linking back to Pexels

```html
<a href="https://www.pexels.com">Photos provided by Pexels</a>

<!-- or show our white logo -->
<a href="https://www.pexels.com">
  <img src="https://images.pexels.com/lib/api/pexels-white.png" />
</a>

<!-- or show our black logo -->
<a href="https://www.pexels.com">
  <img src="https://images.pexels.com/lib/api/pexels.png" />
</a>
```

### Linking back to a Photo

```html
This <a href="https://www.pexels.com/photo/food-dinner-lunch-meal-4147875">Photo</a> was taken by <a href="https://www.pexels.com/@daria">Daria</a> on Pexels.
```

## Client Libraries

Pexels maintains a number of official API client libraries that you can use to interact with the Pexels API:

| Language   | Package           | Github        | Changelog   | Version |
|------------|-------------------|---------------|-------------|---------|
| Ruby       | rubygems          | pexels-ruby   | changelog   | 0.3.0   |
| Javascript | npm               | pexels-javascript | changelog   | 1.2.1   |
| .net       | nuget             | PexelsDotNetSDK | changelog   | 1.0.6   |

Please read the documentation for the client library you'd like to use for more information about syntax (code samples for each library are available on this documentation). Issues and Pull Requests on Github are also welcome!

If you have created an unofficial Pexels API library for a different language please feel free to let us know about it!

## Authorization

Authorization is required for the Pexels API. Anyone with a Pexels account can request an API key, which you will receive instantly.

All requests you make to the API will need to include your key. This is provided by adding an `Authorization` header.

**Example of Authorization**
```bash
curl -H "Authorization: YOUR_API_KEY" \
  "https://api.pexels.com/v1/search?query=people"
```

## Request Statistics

To see how many requests you have left in your monthly quota, successful requests from the Pexels API include three HTTP headers:

| Response Header       | Meaning                                           |
|-----------------------|---------------------------------------------------|
| `X-Ratelimit-Limit`     | Your total request limit for the monthly period   |
| `X-Ratelimit-Remaining` | How many of these requests remain               |
| `X-Ratelimit-Reset`     | UNIX timestamp of when the currently monthly period will roll over |

**Note:** These response headers are only returned on successful (2xx) responses. They are not included with other responses, including 429 Too Many Requests, which indicates you have exceeded your rate limit. Please be sure to keep track of `X-Ratelimit-Remaining` and `X-Ratelimit-Reset` in order to manage your request limit.

**Example of Rate Limit Headers**
```
X-Ratelimit-Limit: 20000
X-Ratelimit-Remaining: 19684
X-Ratelimit-Reset: 1590529646
```

## Pagination

Most Pexels API requests return multiple records at once. All of these endpoints are paginated, and can return a maximum of 80 requests at one time. Each paginated request accepts the same parameters and returns the same pagination data in the response.

**Note:** The `prev_page` and `next_page` response attributes will only be returned if there is a corresponding page.

**Pagination Request Parameters**
`GET https://api.pexels.com/v1/curated?page=2&per_page=40`

**Pagination Response Attributes**
```json
{
  "page": 2,
  "per_page": 40,
  "total_results": 8000,
  "next_page": "https://api.pexels.com/v1/curated?page=3&per_page=40",
  "prev_page": "https://api.pexels.com/v1/curated?page=1&per_page=40"
}
```

## The Photo Resource

The Photo resource is a JSON formatted version of a Pexels photo. The Photo API endpoints respond with the photo data formatted in this shape.

**Response Attributes**
- `id` (integer): The id of the photo.
- `width` (integer): The real width of the photo in pixels.
- `height` (integer): The real height of the photo in pixels.
- `url` (string): The Pexels URL where the photo is located.
- `photographer` (string): The name of the photographer who took the photo.
- `photographer_url` (string): The URL of the photographer's Pexels profile.
- `photographer_id` (integer): The id of the photographer.
- `avg_color` (string): The average color of the photo. Useful for a placeholder while the image loads.
- `src` (object): An assortment of different image sizes that can be used to display this Photo.
- `alt` (string): Text description of the photo for use in the alt attribute.

**Example Photo Resource**
```json
{
  "id": 2014422,
  "width": 3024,
  "height": 3024,
  "url": "https://www.pexels.com/photo/brown-rocks-during-golden-hour-2014422/",
  "photographer": "Joey Farina",
  "photographer_url": "https://www.pexels.com/@joey",
  "photographer_id": 680589,
  "avg_color": "#978E82",
  "src": {
    "original": "https://images.pexels.com/photos/2014422/pexels-photo-2014422.jpeg",
    "large2x": "https://images.pexels.com/photos/2014422/pexels-photo-2014422.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "large": "https://images.pexels.com/photos/2014422/pexels-photo-2014422.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    "medium": "https://images.pexels.com/photos/2014422/pexels-photo-2014422.jpeg?auto=compress&cs=tinysrgb&h=350",
    "small": "https://images.pexels.com/photos/2014422/pexels-photo-2014422.jpeg?auto=compress&cs=tinysrgb&h=130",
    "portrait": "https://images.pexels.com/photos/2014422/pexels-photo-2014422.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=1200&w=800",
    "landscape": "https://images.pexels.com/photos/2014422/pexels-photo-2014422.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=627&w=1200",
    "tiny": "https://images.pexels.com/photos/2014422/pexels-photo-2014422.jpeg?auto=compress&cs=tinysrgb&dpr=1&fit=crop&h=200&w=280"
  },
  "liked": false,
  "alt": "Brown Rocks During Golden Hour"
}
```

## API Endpoints

### Search for Photos
`GET https://api.pexels.com/v1/search`

This endpoint enables you to search Pexels for any topic that you would like.

**Parameters**
- `query` (string, required): The search query.
- `orientation` (string, optional): `landscape`, `portrait`, or `square`.
- `size` (string, optional): `large`(24MP), `medium`(12MP), or `small`(4MP).
- `color` (string, optional): `red`, `orange`, etc., or a hex code.
- `locale` (string, optional): e.g., 'en-US'.
- `page` (integer, optional): The page number. Default: 1.
- `per_page` (integer, optional): Number of results per page. Default: 15, Max: 80.

### Curated Photos
`GET https://api.pexels.com/v1/curated`

This endpoint enables you to receive real-time photos curated by the Pexels team.

**Parameters**
- `page` (integer, optional): The page number. Default: 1.
- `per_page` (integer, optional): Number of results per page. Default: 15, Max: 80.

### Get a Photo
`GET https://api.pexels.com/v1/photos/:id`

Retrieve a specific Photo from its id.

**Parameters**
- `id` (integer, required): The id of the photo.

---

*This documentation is a summary for project reference. For the most up-to-date information, always consult the official Pexels API documentation.*
