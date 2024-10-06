import json
import logging
import time
from opensearchpy import OpenSearch, helpers, OpenSearchException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Search:
    def __init__(self, host="localhost", port=50770, use_ssl=False, http_auth=None):
        self.client = OpenSearch(
            hosts=[{'host': host, 'port': port}],
            http_compress=True,
            http_auth=http_auth or ('admin', 't0bHTN@>YHN3'),
            use_ssl=use_ssl,
            verify_certs=False,
            ssl_assert_hostname=False,
            ssl_show_warn=False,
        )
        self.index_name = 'clinical_trials'

    def find(self, body):
        try:
            return self.client.search(body=body, index=self.index_name)
        except OpenSearchException as e:
            logger.error(f"Error during search: {e}")
            return None

    def index(self, file_path='data/ctg-studies.json'):
        index_body = {
            "mappings": {
                "properties": {
                    "nctId": {"type": "keyword"},
                    "briefTitle": {"type": "text"},
                    "officialTitle": {"type": "text"},
                    "overallStatus": {"type": "keyword"},
                    "startDate": {"type": "date"},
                    "completionDate": {"type": "date"},
                    "conditions": {"type": "keyword"},
                    "interventions": {
                        "type": "nested",
                        "properties": {
                            "type": {"type": "keyword"},
                            "name": {"type": "text"}
                        }
                    },
                    "eligibilityCriteria": {"type": "text"},
                    "healthyVolunteers": {"type": "boolean"},
                    "gender": {"type": "keyword"},
                    "minimumAge": {"type": "integer"},
                    "maximumAge": {"type": "integer"},
                    "locations": {
                        "type": "nested",
                        "properties": {
                            "facility": {"type": "text"},
                            "city": {"type": "keyword"},
                            "state": {"type": "keyword"},
                            "country": {"type": "keyword"}
                        }
                    }
                }
            }
        }

        try:
            # Create index if it doesn't exist
            if not self.client.indices.exists(index=self.index_name):
                self.client.indices.create(index=self.index_name, body=index_body)
                logger.info(f"Created index: {self.index_name}")
            else:
                logger.info(f"Index {self.index_name} already exists")

            # Inject data into OpenSearch
            success, failed = helpers.bulk(self.client, self._read_clinical_trials(file_path))
            logger.info(f"Successfully indexed {success} documents")
            if failed:
                logger.warning(f"Failed to index {len(failed)} documents")
        except OpenSearchException as e:
            logger.error(f"Error during indexing: {e}")

    def _read_clinical_trials(self, file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
            for trial in data:
                yield {
                    "_index": self.index_name,
                    "_source": self._extract_trial_data(trial)
                }

    def _extract_trial_data(self, trial):
        protocol_section = trial.get('protocolSection', {})
        identification_module = protocol_section.get('identificationModule', {})
        status_module = protocol_section.get('statusModule', {})

        return {
            "nctId": identification_module.get('nctId'),
            "briefTitle": identification_module.get('briefTitle'),
            "officialTitle": identification_module.get('officialTitle', ''),
            "conditions": protocol_section.get('conditionsModule', {}).get('conditions', []),
            "overallStatus": status_module.get('overallStatus'),
            "startDate": self._get_date(status_module, 'startDateStruct'),
            "completionDate": self._get_date(status_module, 'completionDateStruct'),
            "interventions": self._get_interventions(protocol_section),
            "eligibilityCriteria": protocol_section.get('eligibilityModule', {}).get('eligibilityCriteria', ''),
            "healthyVolunteers": protocol_section.get('eligibilityModule', {}).get('healthyVolunteers', False),
            "gender": protocol_section.get('eligibilityModule', {}).get('sex', ''),
            "minimumAge": self._parse_age(protocol_section.get('eligibilityModule', {}).get('minimumAge', '0 Years')),
            "maximumAge": self._parse_age(protocol_section.get('eligibilityModule', {}).get('maximumAge', '999 Years')),
            "locations": self._get_locations(protocol_section)
        }

    def _get_date(self, module, date_struct_key):
        return module.get(date_struct_key, {}).get('date')

    def _get_interventions(self, protocol_section):
        return [
            {"type": intervention.get("type"), "name": intervention.get("name")}
            for intervention in protocol_section.get('armsInterventionsModule', {}).get('interventions', [])
        ]

    def _get_locations(self, protocol_section):
        return [
            {
                "facility": location.get("facility", ""),
                "city": location.get("city", ""),
                "state": location.get("state", ""),
                "country": location.get("country", "")
            }
            for location in protocol_section.get('contactsLocationsModule', {}).get('locations', [])
        ]

    def _parse_age(self, age_string):
        try:
            return int(age_string.split()[0])
        except (ValueError, IndexError):
            return 0

    def delete_index(self):
        try:
            self.client.indices.delete(index=self.index_name)
            logger.info(f"Deleted index: {self.index_name}")
        except OpenSearchException as e:
            logger.error(f"Error deleting index: {e}")

    def get_index_stats(self):
        try:
            return self.client.indices.stats(index=self.index_name)
        except OpenSearchException as e:
            logger.error(f"Error getting index stats: {e}")
            return None
