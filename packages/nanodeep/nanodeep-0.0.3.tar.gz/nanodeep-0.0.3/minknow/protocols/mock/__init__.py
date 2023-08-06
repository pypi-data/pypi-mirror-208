from minknow.protocols import ProtocolHandler


class MockProtocolHandler(ProtocolHandler):
    """
    A protocol handler that returns dummy data
    """

    def start(self, args, extra_args):
        """
        Do nothing
        """
        return 0

    def __init__(self):
        """
        Generate dummy protocol data - multiple entries using the same script
        name but different tags and identifiers.  Will create entries for
        two scripts; each script will have the same three possible combinations
        of tags.
        """
        super(MockProtocolHandler, self).__init__()
        tags1 = {
            "kit": "LSK001",
            "expn": "EX02",
            "experiment type": "SEQUENCING",
            "base calling": "true",
            "flow cell": "BLAH",
        }
        self._add_protocol("EXPERIMENT_BaseLine_Sequencing", "12345678", tags1)

        tags2 = {
            "kit": "LSK009",
            "expn": "EX02",
            "experiment type": "SEQUENCING",
            "base calling": "true",
            "flow cell": "BLAH",
        }
        self._add_protocol("EXPERIMENT_BaseLine_Sequencing", "23456789", tags2)

        tags3 = {
            "kit": "LSK009",
            "expn": "EX01",
            "experiment type": "SEQUENCING",
            "base calling": "true",
            "flow cell": "BLAH",
        }
        self._add_protocol("EXPERIMENT_BaseLine_Sequencing", "34567890", tags3)

        self._add_protocol("EXPERIMENT_static_flicking_Sequencing", "45678901", tags1)
        self._add_protocol("EXPERIMENT_static_flicking_Sequencing", "56789012", tags2)
        self._add_protocol("EXPERIMENT_static_flicking_Sequencing", "67890123", tags3)
