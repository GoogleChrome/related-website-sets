# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
class FpsSet:
    """Stores the data of a First Party Set

  Attributes:
    primary: A string of the primary domain for a first party set 
    associated_sites: a list containing domains associated with the 
    FPS' primary domain
    service_sites: a list containing necessary service sites for the
    primary domain and/or service sites and ccTLD sites.
    ccTLDs: a list of domains that are country code variants of other
    members of the first party set. 
    relevant_fields_dict: a dictionary mapping the JSON field equivalents
    of each field to their value within the object. 
  """
    def __init__(self, ccTLDs, primary, associated_sites=None, service_sites=None):
        self.ccTLDs = ccTLDs
        self.primary = primary
        self.associated_sites = associated_sites
        self.service_sites = service_sites
        self.relevant_fields_dict = {'ccTLDs': ccTLDs, 
                                     'primary': primary,
                                     'associatedSites': associated_sites, 
                                     'serviceSites': service_sites}
    
    def __eq__(self, obj):
      if isinstance(obj, FpsSet) and self.primary == obj.primary:
        if self.ccTLDs == obj.ccTLDs:
          if self.associated_sites == obj.associated_sites:
            if self.service_sites == obj.service_sites:
              return True
      return False
    
    def includes(self, domain, with_ccTLDs=True):
       if (self.primary == domain or
                   domain in (self.associated_sites or []) or
                   domain in (self.service_sites or [])):
           return True
       if with_ccTLDs:
           return domain in (variant for variant_list in self.ccTLDs.values() for variant in variant_list)
       return False