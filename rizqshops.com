
mumtazmubashir5@gmail.com sent you a conversion tracking tag

The Google Ads user mumtazmubashir5@gmail.com has shared a tracking tag to track conversions on your website. To add this tag to your website, follow the instructions below.

How to use the tag

For conversion tracking to work, you'll need to install the conversion tracking tag, which consists of a global site tag and an event snippet. If installing the tag with Google Tag Manager, follow these instructions instead.

If any of your web pages are built using AMP, you'll need to add tags to both the AMP and HTML versions. Instructions are included for both.

HTML PAGES

Install the global site tag on every page of your website.
Open the HTML for each page.
Choose from the following options:
If you haven't installed the global site tag on your website, copy the tag below and paste it between the head tags (<head></head>):

<!-- Google tag (gtag.js) --> <script async src="https://www.googletagmanager.com/gtag/js?id=AW-11353557507"></script> <script> window.dataLayer = window.dataLayer || []; function gtag(){dataLayer.push(arguments);} gtag('js', new Date()); gtag('config', 'AW-11353557507'); </script>

See more guidelines on setting up the global site tag.

If you installed the global site tag on your website from another Google product (example: Google Analytics) or from another Google Ads account, copy the 'config' command below and add it to every instance of the global site tag, right above the </script> end tag.

gtag('config', 'AW-11353557507');

If you or a manager account already installed the global site tag on your website while setting up the tag for another conversion action, make sure that the tag is on every page of your website and check that the 'config' command has this Google Ads account's conversion ID: AW-11353557507
Save the changes to your webpages.

Install the event snippet on the conversion page. This is the page your customers reach on your website after they've completed a conversion — the "Thank you for your order" page, for example.
Open the HTML for the conversion page.
Copy the snippet below and paste it between the head tags (<head></head>) of the page, right after the global site tag.

<!-- Event snippet for Add to cart conversion page --> <script> gtag('event', 'conversion', {'send_to': 'AW-11353557507/ZkPjCN2o4O4YEIOU5qUq'}); </script>

Save the changes to your webpage.
AMP PAGES

You should follow these instructions for any of the pages built using the AMP framework.

Install the global site tag on every page of your website.
Open the HTML for each page.
Choose from the following options:
If you haven't installed the global site tag on your website, add these two tags:
First, copy the tag below and paste it between the head tags (<head></head>), before the AMP JS library.

<script async custom-element="amp-analytics" src="https://cdn.ampproject.org/v0/amp-analytics-0.1.js"></script>

Then, copy the tag below and paste it between the body tags (<body></body>) of all of your AMP pages

<!-- Google tag (gtag.js) --> <amp-analytics type="gtag" data-credentials="include"> <script type="application/json"> { "vars": { "gtag_id": "AW-11353557507", "config": { "AW-11353557507": { "groups": "default" } } }, "triggers": { } } </script> </amp-analytics>

See more guidelines on setting up the global site tag.
If you installed the global site tag on your website from another Google product (example: Google Analytics) or from another Google Ads account, copy the line below and include it in the "config" section of every instance of the global site tag.

"AW-11353557507": { "groups": "default" }

If you or a manager account already installed the global site tag on your website while setting up the tag for another conversion action, make sure that the tag is on every page of your website and check that the "config" section has this Google Ads account's conversion ID: AW-11353557507
Save the changes to your webpages.

Install the event snippet on the conversion page. This is the page your customers reach on your website after they've completed a conversion — the "Thank you for your order" page, for example.
Open the HTML for the conversion page.
Copy the snippet below and paste it into the "triggers" section of the global site tag.

"C_W74DRiI-Ig0": { "on": "visible", "vars": { "event_name": "conversion", "send_to": ["AW-11353557507/ZkPjCN2o4O4YEIOU5qUq"] } }

Save the changes to your webpage.
Learn more about adding a conversion tracking tag to your website.
