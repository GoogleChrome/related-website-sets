# Related Website Sets Submission Guidelines 

Related Website Sets ("RWS") provides a framework for developers to declare relationships among sites, to enable limited cross-site data access for specific, user-facing purposes. This framework may help user agents, such as the Chrome browser ("Chrome"), to decide when to allow or deny a site access to their cookies when in a third-party context.
RWS is a [Privacy Sandbox](https://privacysandbox.com/) proposal being incubated in the W3C's [WICG](https://www.w3.org/community/wicg/). For a full overview, consult the [explainer](https://github.com/privacycg/first-party-sets). The Related Website Sets Submission Guidelines ("Guidelines") are put forth by Chrome to define requirements and expectations for sets submitted by developers. Chrome remains committed to pursuing [standardization](https://www.w3.org/standards/) of RWS through engaging with developers, other browser vendors, and other interested parties.

## Definitions

A **Related Website Set**, or **set**, is a collection of domains that is subject to the <a href="#set-formation-requirements">formation requirements</a>, has passed the <a href="#set-validation-requirements">validation requirements</a>, and has been successfully submitted to the canonical RWS list. 

A **subset** is a defined use case within a set. Set members, or domains, will always be part of a subset. 

A **set primary** is the domain a set submitter has identified as the representative of its set. Other domains within the set have a defined relationship with the primary. 

A **set member** is a domain that is part of a set that is not the primary. A set member will always be part of a subset within the set.

The **canonical RWS list** is a publicly viewable list in a JSON file format housed in the <a href="https://github.com/googlechrome/first-party-sets">RWS GitHub repository</a> that is the source-of-truth for all sets that are subject to the formation requirements and have passed the validation requirements. Browsers, such as Chrome, can consume this file to apply to their behavior.

A **pull request (PR)**, is the method of requesting a change on GitHub (like adding or modifying a set to the canonical RWS list). 

A **submission** is an addition or modification to the canonical RWS list submitted by the submitter that is subject to the formation and the validation requirements.

A **submitter** is the individual or, if an individual is acting on behalf of their organization, the organization that has submitted a pull request against the canonical RWS list to create or modify a set for validation.

An **equivalent domain** is the primary, service, or associated domain in a set for which there is a ccTLD variant in the same set. The equivalent domain has the same effective second-level domain (eSLD, or eTLD+1 minus eTLD) as a ccTLD variant in the same set.

## Set Formation Requirements

The table below describes the types of subsets that RWS currently supports, including requirements to help prevent misuse of the subset.

All submissions are subject to the formation requirements detailed in this section as well as the <a href="#set-validation-requirements">technical validation requirements</a> in the next section.

| Subset Type | Subset Definition |
| ----------- | ----------------- |
|   Service   | <ul><li>Domains that serve another set member to support functionality or security needs.</li><li>Service domains should not be the entry point to a user's journey on a site, but may be surfaced to a user as part of their journey.</li><li>Service domains must share a common owner with the set primary.</li><li>Submitters must provide an explanation of how each domain in this subset supports functionality or security needs.</li><li>Service domains must have a registered DNS entry</li>|
|  Associated | <ul><li>Domains whose affiliation with the set primary is clearly presented to users.</li><li>Submitters must provide an explanation of how they clearly present the affiliation across domains to users and why users would expect their domains to be affiliated (e.g., an About page, header or footer, shared branding or logo, etc).</li>|

ccTLD (country code top-level domain) variants for the subsets above are also supported. The requirements for these domains are as follows:

| ccTLD | <ul><li>Domains that represent variations for a particular country or a geographical area. </li><li>ccTLD variants must share an identical eSLD with its equivalent domain.</li><li>The TLD of each ccTLD variant must be on <a href="https://icannwiki.org/Country_code_top-level_domain#Current_ccTLDs">ICANN's list of country codes</a>.</li><li>ccTLD variants must share a common owner with its equivalent domain.</li>|
| ----------- | :------------ |

### Set submissions

New submissions to the canonical RWS list must be filed as <a href="https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request">pull requests (PRs)</a> on GitHub. Submitters should ensure that submissions follow the schema template provided below. Anyone with a <a href="https://docs.github.com/en/get-started/learning-about-github/types-of-github-accounts">GitHub account</a> may make a submission.

Modifications to existing sets, including deletions, must also be submitted as new PRs against the canonical RWS list.
The canonical RWS list will be validated against [this schema](./SCHEMA.json) whenever a user files their PR.

A hypothetical example of the RWS canonical list is provided below for reference. A submission should follow the structure below, with new submissions being added as items to the "sets" list.

```json
{
  "sets": [
    {
      "contact": "email address or group alias if available",
      "primary": "https://primary1.com",

      "associatedSites": ["https://associateA.com", "https://associateB.com", "https://associateC.com"],

      "serviceSites": ["https://servicesiteA.com"],

      "rationaleBySite": {
        "https://associateA.com": "An explanation of how you clearly present the affiliation across domains to users and why users would expect your domains to be affiliated",
        "https://associateB.com": "An explanation of how you clearly present the affiliation across domains to users and why users would expect your domains to be affiliated",
	 "https://associateC.com": "An explanation of how you clearly present the affiliation across domains to users and why users would expect your domains to be affiliated",
        "https://serviceSiteA.com": "An explanation of how each domain in this subset supports functionality or security needs."
      },

      "ccTLDs": {
        "https://associateA.com": ["https://associateA.ca", "https://associateA.co.uk"],
        "https://associateB.com": ["https://associateB.ru", "https://associateB.co.kr"],
        "https://primary1.com": ["https://primary1.co.uk"]
      }
    }
  ]
}
```

## Set Validation Requirements

It is important that users' interests are protected from invalid submissions, and that web browsers use objective methods to validate submissions. As such, Chrome will rely on several technical methods to validate submissions. These technical checks, comprising both set-level checks and subset-level checks, will be conducted on GitHub, where results will be accessible and viewable by the public. 

### Set-level technical validation

Upon submission of a PR, a series of technical checks will run on GitHub to verify the following: 

- The formatting of the JSON submitted must conform to the output of Python's [json.dumps](https://docs.python.org/3/library/json.html#json.dumps) function with the options `ensure_ascii=False` and `indent=2`.
- Each domain must be prefixed by the https:// scheme. Sets may only include domains served over secure (https://) schemes.
- Each domain must be a <a href="https://github.com/publicsuffix/list/wiki/Format#:~:text=The%20registered%20or%20registrable%20domain%20is%20the%20public%20suffix%20plus%20one%20additional%20label.">registrable domain</a> (i.e., eTLD+1 using a snapshot (refreshed every 6 months) of the <a href="https://publicsuffix.org/">Public Suffix List (PSL)</a> to determine eTLD) at the time of submission. 
- Note that RWS uses the qualification of "eTLD+1 with a secure transport scheme" to determine the boundaries of an entry, meaning that `https://example.com` and `https://a.example.com` should not both exist on `related_website_sets.JSON` as they share the same eTLD+1: `example.com`. However, this should not be an issue for the owner of `https://example.com`, as its and `https://a.example.com`'s cookies are not considered third-party to each other. Cookies are bounded by site, and since `https://a.example.com` is a subdomain of `https://example.com`, both origins have access to the same cookies (modulo the `Domain` attribute) since they are the same site. To learn more about what is considered cross-site vs same-site, [please read this article](https://web.dev/articles/same-site-same-origin).
- Each domain must not already be present in the <a href="https://github.com/googlechrome/first-party-sets/blob/main/related_website_sets.JSON">canonical RWS list.</a>
- Each domain must satisfy the `/.well-known/` metadata requirement:
    - The /.well-known/ metadata requirement demonstrates that the submitter has administrative access to the domains present in the set, since administrative access is required to modify the /.well-known/ file. This will help prevent unauthorized actors from adding domains to a set. 
    - The primary domain must serve a JSON file at `/.well-known/related-website-set.json` (Note: list entries merged before September 15th 2023 may serve their well-known file at `/.well-known/first-party-set.json` instead; however, any changes to those entries will require that the primary and all members of the set must be served at `/.well-known/related-website-set.json` like any other entry). The contents of the file must be identical to the submission. Each member domain must serve a JSON file at /.well-known/related-website-set.json. The contents of the file must name the primary domain. These files must be maintained for the duration of the domain’s inclusion in the set.
    - Any changes to an existing RWS in the <a href="https://github.com/googlechrome/first-party-sets/blob/main/related_website_sets.JSON">canonical RWS list</a>  must also be reflected in that set's JSON files at `/.well-known/related-website-set.json`.
    - If an RWS owner wishes to remove a set entirely from the <a href="https://github.com/googlechrome/first-party-sets/blob/main/related_website_sets.JSON">canonical RWS list,</a> then that set's primary must serve a `404 (Not Found)` status code at their `/.well-known/related-website-set.json` endpoint to demonstrate a deliberate desire to remove the set.
    - Example for  `primary.com/.well-known/related-website-set.json`:
	
```json
{
  "primary": "https://primary.com",
  "associatedSites": ["https://associate1.com", "https://associate2.com", "https://associate3.com", "https://associate4.com"],
  "serviceSites": ["https://servicesite1.com"],
  "rationaleBySite": {
    "https://associate1.com": "An explanation of how you clearly present the affiliation across domains to users and why users would expect your domains to be affiliated",
    "https://associate2.com": "An explanation of how you clearly present the affiliation across domains to users and why users would expect your domains to be affiliated",
    "https://associate3.com": "An explanation of how you clearly present the affiliation across domains to users and why users would expect your domains to be affiliated",
    "https://serviceSite1.com": "An explanation of how each domain in this subset supports functionality or security needs."
  },

  "ccTLDs": {
    "https://associate1.com": ["https://associate1.ca", "https://associate1.co.uk", "https://associate1.de"],
    "https://associate2.com": ["https://associate2.ru", "https://associate2.co.kr", "https://associate2.fr"],
    "https://primary.com": ["https://primary.co.uk"]
  }
}
```
The `/.well-known/related-website-set.json` file for the set primary must follow the schema specified below:
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
    "associatedSites": ["An explanation of how you clearly present the affiliation across domains to users and why users would expect your domains to be affiliated"],
    "serviceSites": ["An explanation of how each domain in this subset supports functionality or security needs."]
  }
}
```

Example for associate1.com/.well-known/related-website-set.json:

```json
{
  "primary":"https://primary.com"
}
```

The `/.well-known/related-website-set.json` file for set members must follow the schema specified below:

```json
{
  "type": "object",
  "properties": {
    "primary": { "type": "string" }
  },
  "required": ["primary"]
}
```

### Subset-level technical validation

Additionally, more granular technical checks will also run on GitHub for service domains and ccTLD variants in the submissions. 

Service Domains must satisfy the following conditions:
	<ul>
		<li>Must not be crawlable. Service domains must have an `X-Robots-Tag` containing a 'noindex' or 'none' [value](https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag#directives).</li>
		<li>Must not have `ads.txt`.</li>
<li>Must have a homepage that redirects to a different domain or results in 4xx (client error) or 5xx (server error).</li>
	</ul>
ccTLD variants must satisfy the following conditions:
	<ul>
		<li>Must be present on <a href="https://icannwiki.org/Country_code_top-level_domain#Current_ccTLDs">ICANN's list</a> of known ccTLDs.</li>
		<ul>
			<li>If the primary domain features a ccTLD like example.co.uk, and the subset domains include a “.com” domain as one of the ccTLD variants such as example.com, Chrome will allow for “.com” to be treated as a ccTLD variant. </li>
		</ul>
<li>Must share a common eSLD with the primary domain, 'service' domain, or 'associated' domain in the same set.</li>
	</ul>

#### Validation success

If a set submission passes all technical checks successfully, the submitter will be notified that their PR was successful on GitHub. At this time, approved PRs will be manually merged in batches to the canonical RWS list once per week (Tuesdays at 12pm Eastern Time (ET)), excluding during holidays. 

#### Validation failure

A submission may fail for the following reasons:
<ul>
<li>A domain fails to pass any of the <a href="#set-level-technical-validation">set-level technical checks</a>.</li>
<li>A domain fails to pass any of the <a href="#subset-level-technical-validation">subset-level technical checks</a>.</li>
</ul>
In the case of submission failure, the submitter will be notified through a PR failure on GitHub. The PR failure notification may also provide additional information on why the submission may have failed. All technical checks governing set submissions are conducted on GitHub, and consequently all submission failures resulting from technical checks will be viewable on GitHub. 

If you feel that a specific technical check has mistakenly caused a submission failure, leave a comment on the failed PR after consulting the error log. The Chrome team will investigate and reach out if further action is required.

If a failing PR is not updated after 30 days, you will be reminded with a comment to take action. If no action is taken within 14 days of the reminder, the PR will be closed. If you would still like to proceed with the RWS submission process, you may choose to reopen your closed PR, or to restart by creating a new PR.

## Browser Behavior

Chrome consumes the canonical RWS list on a regular basis (every 2 weeks) and ships it to clients as an updateable component. Individual clients (with internet access) will refresh the list they apply each time they restart, or on start-up, if newly downloaded.

In addition to the formation requirements and validation requirements above, sets are subject to subset-level limitations imposed by the browser to help prevent misuse of subsets. The table below describes how Chrome treats each subset. 

| Subset Type | Browser Behavior |
| ----------- | ----------------- |
|   Service   | <ul><li>No limit on number of domains.</li><li>If a service domain calls [`requestStorageAccessFor(origin)`](https://github.com/privacycg/requestStorageAccessFor), the call is automatically rejected.</li><li>If any site in the RWS calls [`requestStorageAccess()`](https://github.com/privacycg/storage-access) while embedded under a service domain, the call is handled as a normal authenticated embed scenario (and may prompt).</li><li>If a service domain calls `requestStorageAccess()` while embedded under a primary or associated site, the call is auto-granted.</li>|
|   Associated   | <ul><li>`requestStorageAccess()` and `requestStorageAccessFor(origin)` will be auto-granted for up to five domains in the order listed within the associated subset category.</li><li>`requestStorageAccess()` and `requestStorageAccessFor(origin)` will be auto-rejected for any domain beyond the fifth listed. </li>|

While there is no limit on the number of ccTLDs that may be associated with a single associated or service domain in the same set, a ccTLD variant inherits the restrictions imposed on its equivalent domain. For example, `requestStorageAccessFor(origin)` calls will be auto-rejected when called by a ccTLD variant which is an alias of a service domain.
To test this behavior in Chrome, please consult the [Related Website Sets integration guide](https://developer.chrome.com/en/docs/privacy-sandbox/first-party-sets-integration/).

Note: Browsers may select to use Related Website Set's domain relationships for other purposes. For example, Chrome's [IP Protection](https://github.com/GoogleChrome/ip-protection) proposal includes relying on RWS for the purposes of determining first-party and third-party contexts, but does not change RWS's Subset Types or Validation criteria.

If a submitter is defining related sites for non-browser-storage use cases like IP address, it may be to address network-level performance optimization or access management. In these scenarios, it may be appropriate to utilize the Service subset type, which does not have a domain limit but does have ownership requirements.

## Set Lifetime

As a best practice, submitters should plan to review their sets periodically (e.g., annually).

Submitters should also expect that sets will be subject to expiration and / or renewal requirements. This prevents sets from becoming stale, as technical checks improve, additional subsets are created, and / or alternative technologies are introduced over time. For example, sets will need to be refreshed when Chrome begins phasing out third-party cookies. At that time, submitters may expect additional clarity around set renewal requirements.

## Responsibilities of the Submitter

The submitter is responsible for maintaining the integrity of their set(s) and should be able to demonstrate conformance with the formation requirements above.

For example, in the case that conformance with ownership requirements (for ccTLD variants and service domains) must be demonstrated, submitters should use resources verifiable by public documentation, or recognized in filing documentation with an incorporating or registration agency in the submitter's jurisdiction of incorporation or registration, or created or recognized by a government agency. Alternatively, in some cases, conformance with ownership requirements may be attested to by a professional opinion letter signed by a lawyer or public notary. The person signing the legal opinion should have a valid license within the jurisdiction of the country in which the main entity is operating by maintaining an office or residence.

### Enforcement Activities

At this time, validation of set submissions will be based on the methods described in these Guidelines, and Chrome will not apply additional enforcement activity governing set submissions, however Chrome reserves the right to act in cases of egregious and blatant disregard of these Guidelines. All submissions are publicly visible and subject to the scrutiny of the broader web community, including users, civil society, and other interested parties.

Chrome will continue to evaluate how best to maintain the appropriate guardrails for set submissions, including developing more rigorous technical checks and introducing additional enforcement mechanisms. If Chrome determines that additional verification steps are necessary to provide a safe and reliable ecosystem for users, the team will notify developers with the appropriate notice. 

## Feedback

Chrome is committed to engaging and receiving feedback from the broader ecosystem, including through the W3C (World Wide Web Consortium), on the future development of the Related Website Sets standard and this version of the Related Website Sets Submission Guidelines.

For feedback on the Related Website Sets standard, please engage on GitHub or on [WICG calls](https://docs.google.com/document/d/10dMVqt2x8otohdJx4AZYccdX5Hp_lrxlT7QAO2adcfE/edit#heading=h.uc5qyqdrhfhv). For feedback or questions on these Guidelines, please file an issue in this repository.
