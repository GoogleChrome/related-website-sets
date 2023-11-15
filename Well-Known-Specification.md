# The "related-website-set.json" Well-Known Resource Identifier

This page describes the use and content of URIs with the path
`/.well-known/related-website-set.json`.
## Use

A site may demonstrate intentional opt-in to participation in a Related Website
Set (RWS) by hosting a specific JSON file at the URI with a path of
`/.well-known/related-website-set.json`.
## Content

The `/.well-known/related-website-set.json` file for the set primary of an RWS
must follow the schema specified below:
```json
{
  "type": "object",
  "properties": {
    "ccTLDs": {
      "type": "object",
      "additionalProperties": {
        "type": "array",
        "items": {
          "type": "string"
        }
      }
    },
    "primary": { "type": "string" },
    "associatedSites": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "serviceSites": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "rationaleBySite": {
      "type": "object",
      "additionalProperties": {
        "type": "string"
      }
    }
  },
  "required": ["primary"],
  "dependentRequired": {
    "associatedSites": ["An explanation of how you clearly present the 
    affiliation across domains to users and why users would expect your 
    domains to be affiliated"],
    "serviceSites": ["An explanation of how each domain in this subset 
    supports functionality or security needs."]
  }
}
```
The `/.well-known/related-website-set.json` file for non-primary members of an
RWS must follow the schema specified below:
```json
{
  "type": "object",
  "properties": {
    "primary": { "type": "string" }
  },
  "required": ["primary"]
}
```