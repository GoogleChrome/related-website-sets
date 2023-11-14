# The "related-website-set.json" Well-Known Resource Identifier

This page describes the use and content of URIs having the path 
`/.well-known/related-website-set.json`.
## Use

A page may be hosted at the URI having the path of 
`/.well-known/related-website-set.json` in order to demonstrate
administrative access to the site when submitted as an entry in a Related 
Website Site (RWS).  
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
The `/.well-known/related-website-set.json` file for set members of an RWS 
must follow the schema specified below:
```json
{
  "type": "object",
  "properties": {
    "primary": { "type": "string" }
  },
  "required": ["primary"]
}
```