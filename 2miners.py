"""2miners exporter"""

import os
import time
from prometheus_client import start_http_server, Gauge, Info, Summary, Enum
import requests
import logging

addy = os.environ.get('MINING-ADDRESS')
name = os.environ.get('RIG-NAME')

class AppMetrics:
    """
    Representation of Prometheus metrics and loop to fetch and transform
    application metrics into Prometheus metrics.
    """

    def __init__(self, app_port=80, polling_interval_seconds=5):
        self.app_port = app_port
        self.polling_interval_seconds = polling_interval_seconds
        # Prometheus metrics to collect
        self.dayreward_number = Gauge("dayreward_number", "24hnumreward")
        self.dayreward = Gauge("dayreward", "24hreward")
        self.currentHashrate = Gauge("hashrate_current", "currentHashrate")
        self.reportedHashrate = Gauge("hashrate_reported", "reportedHashrate")
        self.current_luck = Gauge('current_luck', 'currentLuck')
        self.hashrate = Gauge('hashrate', 'Hashrate')
        self.payments_total = Gauge('payments_total', 'paymentsTotal')
        self.round_shares = Gauge('round_shares', 'roundShares')
        self.shares_stale = Gauge('shares_stale', 'sharesStale')
        self.shares_valid = Gauge('shares_valid', 'sharesValid')
        self.current_balance = Gauge('current_balance','stats_balance')

    def run_metrics_loop(self):
        """Metrics fetching loop"""

        while True:
            self.fetch()
            time.sleep(self.polling_interval_seconds)

    def fetch(self):
        """
        Get metrics from application and refresh Prometheus metrics with
        new values.
        """

        # Fetch raw status data from the application
        resp = requests.get(url=f"https://eth.2miners.com/api/accounts/{addy}")
        status_data = resp.json()

        # Update Prometheus metrics with application metrics
        self.dayreward_number.set(status_data["24hnumreward"])
        self.dayreward.set(status_data["24hreward"])
        self.currentHashrate.set(status_data["currentHashrate"])
        self.reportedHashrate.set(status_data['workers'][f'{name}']['rhr'])
        self.current_luck.set(status_data["currentLuck"])
        self.hashrate.set(status_data["hashrate"])
        self.payments_total.set(status_data["paymentsTotal"])
        self.round_shares.set(status_data["roundShares"])
        self.shares_valid.set(status_data["sharesValid"])
        self.current_balance.set(status_data['stats']['balance'])

def main():
    """Main entry point"""

    polling_interval_seconds = int(os.getenv("POLLING_INTERVAL_SECONDS", "5"))
    app_port = int(os.getenv("APP_PORT", "80"))
    exporter_port = int(os.getenv("EXPORTER_PORT", "9877"))

    app_metrics = AppMetrics(
        app_port=app_port,
        polling_interval_seconds=polling_interval_seconds
    )
    start_http_server(exporter_port)
    app_metrics.run_metrics_loop()

if __name__ == "__main__":
    main()
