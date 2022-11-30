## First-Party Sets Submission Guidelines ## 
Overview
First-Party Sets ("FPS") provides a framework for developers to declare relationships among sites, to enable limited cross-site cookie access for specific, user-facing purposes. This framework may help user agents, such as the Chrome browser ("Chrome"), to decide when to allow or deny a site access to their cookies when in a third-party context.

FPS is a Privacy Sandbox proposal being incubated in the W3C's WICG. For a full overview, consult the explainer. The First-Party Sets Submission Guidelines ("Guidelines") are put forth by Chrome to define requirements and expectations for sets submitted by developers. Chrome remains committed to pursuing standardization of FPS through engaging with developers, other browser vendors, and other interested parties.
Definitions
A First-Party Set, or set, is a collection of domains that is subject to the formation requirements, has passed the validation requirements, and has been successfully submitted to the canonical FPS list. 

A subset is a defined use case within a set. Set members, or domains, will always be part of a subset. 

A set primary is the domain a set submitter has identified as the representative of its set. Other domains within the set have a defined relationship with the primary. 

A set member is a domain that is part of a set that is not the primary. A set member will always be part of a subset within the set.

The canonical FPS list is a publicly viewable list in a JSON file format housed in the FPS GitHub repository that is the source-of-truth for all sets that are subject to the formation requirements and have passed the validation requirements. Browsers, such as Chrome, can consume this file to apply to their behavior.

A pull request (PR), is the method of requesting a change on GitHub (like adding or modifying a set to the canonical FPS list). 

A submission is an addition or modification to the canonical FPS list submitted by the submitter that is subject to the formation and the validation requirements.

A submitter is the individual or, if an individual is acting on behalf of their organization, the organization that has submitted a pull request against the canonical FPS list to create or modify a set for validation.

An equivalent domain is the primary, service, or associated domain in a set for which there is a ccTLD variant in the same set. The equivalent domain has the same effective second-level domain (eSLD, or eTLD+1 minus eTLD) as a ccTLD variant in the same set.
Set Formation Requirements
The table below describes the types of subset that FPS currently supports, including requirements to help prevent misuse of the subset. 

All submissions are subject to the formation requirements detailed in this section as well as the technical validation requirements in the next section. 

| Subset Type | Subset Definition |
| ----------- | ----------------- |
|   Service   | <ul><li>Domains that serve another set member to support functionality or security needs.</li><li>Service domains should not be the entry point to a user's journey on a site, but may be surfaced to a user as part of their journey.</li><li>Service domains must share a common owner with the set primary.</li><li>Submitters must provide an explanation of how each domain in this subset supports functionality or security needs.</li><li>Service domains must have a registered DNS entry</li>|
|  Associated | <ul><li>Domains whose affiliation with the set primary is clearly presented to users.</li><li>Submitters must provide an explanation of how they clearly present the affiliation across domains to users and why users would expect their domains to be affiliated (e.g., an About page, header or footer, shared branding or logo, etc).</li>|
| ccTLD (country code top-level domain) | <ul><li>Domains that represent variations for a particular country or a geographical area. </li><li>ccTLD variants must share an identical eSLD with its equivalent domain.</li><li>The eTLD of each ccTLD variant must be present in the ccTLD section of the Public Suffix List (PSL).</li><li>ccTLD variants must share a common owner with its equivalent domain.</li>|

Set submissions

New submissions to the canonical FPS list must be filed as pull requests (PRs) on GitHub. Submitters should ensure that submissions follow the schema template provided below. Anyone with a GitHub account may make a submission.

Modifications to existing sets, including deletions, must also be submitted as new PRs against the canonical FPS list.
The canonical FPS list will be validated against this schema whenever a user files their PR:
```json
{
   "type": "object",
   "properties": {
       "sets":  {
           "type": "array",
           "items": {
               "type": "object",
               "properties": {
                   "ccTLDs": {
                       "type":"object",
                       "additionalProperties":{
                           "type": "array",
                           "items":{
                               "type": "string"
                           }
                       }
                   },
                   "primary" : {"type":"string"},
                   "associatedSites": {
                       "type": "array",
                       "items":{
                           "type": "string"
                       }
                   },
                   "serviceSites": {
                       "type":"array",
                       "items":{
                           "type": "string"
                       }
                   },
                   "rationaleBySite": {
                       "type":"object",
                       "additionalProperties":{
                           "type": "string"
                       }
                   }
               },
               "required": ["primary"],
               "dependentRequired": {
                   "associatedSites": ["rationaleBySite"],
                   "serviceSites": ["rationaleBySite"]
               },
           },
       }
   }
}
```
A hypothetical example of the FPS canonical list is provided below for reference. A submission should follow the structure below, with new submissions being added as items to the "sets" list.
```json
{
 "sets": [
   {
     "primary": "https://primary.com", 

    "associatedSites": ["https://associate1.com", "https://associate2.com", "https://associate3.com"], 

     "serviceSites": ["https://servicesite1.com"], 

     "ccTLDs": {
       "https://associate1.com": ["https://associate1.ca", "https://associate1.co.uk", "https://associate1.de"],
       "https://associate2.com": ["https://associate2.ru", "https://associate2.co.kr", "https://associate2.fr"],
       "https://primary.com": ["https://primary.co.uk"]
     }
   },
  {
     "primary": "https://primary2.com", 

    "associatedSites": ["https://associateA.com", "https://associateB.com"], 

     "serviceSites": ["https://servicesiteA.com"],

     "rationaleBySite": {
       "https://associateA.com": "rationale for site",
       "https://associateB.com": "rationale for site",
       "https://serviceSiteA.com": "rationale for site"
      },

     "ccTLDs": {
       "https://associateA.com": ["https://associateA.ca", "https://associateA.co.uk"],
       "https://associateB.com": ["https://associateB.ru", "https://associateB.co.kr"],
       "https://primary2.com": ["https://primary2.co.uk"]
     }
   }
 ]
}
```
Set Validation Requirements

It is important that users' interests are protected from invalid submissions, and that web browsers use objective methods to validate submissions. As such, Chrome will rely on several technical methods to validate submissions. These technical checks, comprising both set-level checks and subset-level checks, will be conducted on GitHub, where results will be accessible and viewable by the public. 
Set-level technical validation

Upon submission of a PR, a series of technical checks will run on GitHub to verify the following; 
Each domain must be prefixed by the https:// scheme. Sets may only include domains served over secure (https://) schemes. 
Each domain must be a registrable domain (i.e., eTLD+1 using a snapshot (refreshed every 6 months) of the Public Suffix List (PSL) to determine eTLD) at the time of submission. 
Each domain must not already be present in the canonical FPS list.
Each domain must satisfy the /.well-known/ metadata requirement:
The /.well-known/ metadata requirement demonstrates that the submitter has administrative access to the domains present in the set, since administrative access is required to modify the /.well-known/ file. This will help prevent unauthorized actors from adding domains to a set. 
The primary domain must serve a JSON file at /.well-known/first-party-set". The contents of the file must be identical to the submission. Each member domain must serve a JSON file at /.well-known/first-party-set". The contents of the file must name the primary domain.
Example for  primary.com/.well-known/first-party-set:
```json
{
"primary": "https://primary.com",
 "associatedSites": ["https://associate1.com", "https://associate2.com", "https://associate3.com", "https://associate4.com"],
 "serviceSites": ["https://servicesite1.com"],
 "rationaleBySite": {
       "https://associate1.com": "rationale for site",
       "https://associate2.com": "rationale for site",
       "https://associate3.com": "rationale for site",
       "https://serviceSite1.com": "rationale for site"
      },

"ccTLDs": {
     "https://associate1.com": ["https://associate1.ca", "https://associate1.co.uk", "https://associate1.de"],
     "https://associate2.com": ["https://associate2.ru", "https://associate2.co.kr", "https://associate2.fr"],
     "https://primary.com": ["https://primary.co.uk"]
}
```
The /.well-known/first-party-set file for the set primary must follow the schema specified below:
```json
{
               "type": "object",
               "properties": {
                   "ccTLDs": {
                       "type":"object",
                       "additionalProperties":{
                           "type": "array",
                           "items":{
                               "type": "string"
                           }
                       }
                   },
                   "primary" : {"type":"string"},
                   "associatedSites": {
                       "type": "array",
                       "items":{
                           "type": "string"
                       }
                   },
                   "serviceSites": {
                       "type":"array",
                       "items":{
                           "type": "string"
                       }
                   },
                   "rationaleBySite": {
                       "type":"object",
                       "additionalProperties":{
                           "type": "string"
                       }
                   }
               },
               "required": ["primary"],
               "dependentRequired": {
                   "associatedSites": ["rationaleBySite"],
                   "serviceSites": ["rationaleBySite"]
               },
           }
```
Example for associate1.com/.well-known/first-party-set:
```json
{
   "primary":"https://primary.com"
}
```
The /.well-known/first-party-set file for set members must follow the schema specified below:
```json
{ 
	"type": "object",
	"properties": {
           "primary" : {"type":"string"}
       },
	"required": ["primary"]
}
```
Subset-level technical validation

Additionally, more granular technical checks will also run on GitHub for service domains and ccTLD variants in the submissions. 
service domains must satisfy the following conditions:
Must not have robots.txt, or have a robots.txt with a "no index" header. 
Must not have ads.txt.
Must have a homepage that redirects to a different domain or results in 4xx (client error) or 5xx (server error).

ccTLD variants must satisfy the following conditions:
Must be present on ICANN's list of known ccTLDs.
Must share a common eSLD with the primary domain, 'service' domain, or 'associated' domain in the same set.

Validation success

If a set submission passes all technical checks successfully, the submitter will be notified that their PR was successful on GitHub. At this time, approved PRs will be manually merged in batches to the canonical FPS list once per week (Tuesdays at 12pm Eastern Time (ET)). 

Validation failure

A submission may fail for the following reasons:
A domain fails to pass any of the set-level technical checks.
A domain fails to pass any of the subset-level technical checks.
In the case of submission failure, the submitter will be notified through a PR failure on GitHub. The PR failure notification may also provide additional information on why the submission may have failed. All technical checks governing set submissions are conducted on GitHub, and consequently all submission failures resulting from technical checks will be viewable on GitHub. 

If you feel that a specific technical check has mistakenly caused a submission failure, leave a comment on the failed PR after consulting the error log. The Chrome team will investigate and reach out if further action is required.
Browser Behavior
When the submission process launches for General Availability in Chrome, Chrome will consume the canonical FPS list on a regular basis (e.g., every 2 weeks) and ship it to clients as an updateable component. Individual clients (with internet access) will refresh the list they apply each time they restart, or on start-up, if newly downloaded. 

In addition to the formation requirements and validation requirements above, sets are subject to subset-level limitations imposed by the browser to help prevent misuse of subsets. The table below describes how Chrome will treat each subset. 

Subset Type
Browser Behavior
Service
No limit on number of domains.
Only other domains in the same set may call requestStorageAccessFor on behalf of a service domain. 
This access will be auto-granted. 
A service domain calling requestStorageAccess for itself, or calling requestStorageAccessFor for any other domain, will be auto-rejected.
Associated
requestStorageAccess will be auto-granted for up to three domains in the order listed.
requestStorageAccess will be auto-rejected for any domain beyond the third listed. 

While there is no limit on the number of ccTLDs that may be associated with a single associated or service domain in the same set, a ccTLD variant inherits the restrictions imposed on its equivalent domain. For example, requestStorageAccess calls will be auto-rejected when called by a ccTLD variant which is an alias of a service domain.
To test this behavior in Chrome, please consult the First-Party Sets testing instructions.
Set Lifetime
Submitters should expect that sets will be subject to expiration and / or renewal requirements. This prevents sets from becoming stale, as technical checks improve, additional subsets are created, and / or alternative technologies are introduced over time. For example, sets created during the testing period will need to be refreshed at the time of third-party cookie deprecation in Chrome. At that time, submitters may expect additional clarity around set renewal requirements.
Responsibilities of the Submitter
The submitter is responsible for maintaining the integrity of their set(s) and should be able to demonstrate conformance with the formation requirements above.
For example, in the case that conformance with ownership requirements (for ccTLD variants and service domains) must be demonstrated, submitters should use resources verifiable by public documentation, or recognized in filing documentation with an incorporating or registration agency in the submitter's jurisdiction of incorporation or registration, or created or recognized by a government agency. Alternatively, in some cases, conformance with ownership requirements may be attested to by a professional opinion letter signed by a lawyer or public notary. The person signing the legal opinion should have a valid license within the jurisdiction of the country in which the main entity is operating by maintaining an office or residence.
Enforcement Activities

At this time, validation of set submissions will be based on the methods described in these Guidelines, and Chrome will not apply additional enforcement activity governing set submissions, however Chrome reserves the right to act in cases of egregious and blatant disregard of these Guidelines. All submissions are publicly visible and subject to the scrutiny of the broader web community, including users, civil society, and other interested parties.

Chrome will continue to evaluate how best to maintain the appropriate guardrails for set submissions, including developing more rigorous technical checks and introducing additional enforcement mechanisms. If Chrome determines that additional verification steps are necessary to provide a safe and reliable ecosystem for users, the team will notify developers with the appropriate notice. 
Feedback 
Chrome is committed to engaging and receiving feedback from the broader ecosystem, including through the W3C (World Wide Web) Consortium, on the future development of the First-Party Sets standard and this version of the First-Party Sets Submission Guidelines.

For feedback on the First-Party Sets standard, please engage on GitHub or on WICG calls. For feedback or questions on these Guidelines, please file an issue in this repository.

