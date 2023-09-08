from hypothesis import strategies as strategy


class TestDataGenerator:
    @staticmethod
    def generate_comm_id():
        return strategy.text(min_size=6, max_size=6)

    @staticmethod
    def generate_participant():
        return strategy.sampled_from(["relay", "user"])

    @staticmethod
    def generate_participant_id():
        return strategy.text(min_size=1, max_size=10)

    @staticmethod
    def generate_text():
        return strategy.text(min_size=1, max_size=1000)

    @staticmethod
    def generate_payload():
        payload_email_body = strategy.text(min_size=1, max_size=500)

        return strategy.builds(
            lambda kb, email, ttl, secret, actions, channel, context, message, revision, attachment, notificationsEnable: {
                "kb": kb,
                "email": email,
                "ttl": ttl,
                "secret": secret,
                "actions": actions,
                "channel": channel,
                "context": context,
                "message": message,
                "revision": revision,
                "attachment": attachment,
                "notificationsEnable": notificationsEnable,
            },
            kb=strategy.none(),
            email=strategy.builds(lambda body: {"body": body}, body=payload_email_body),
            ttl=strategy.none(),
            secret=strategy.text(min_size=32, max_size=32),
            actions=strategy.lists(strategy.integers()),
            channel=strategy.just("email"),
            context=strategy.fixed_dictionaries(
                {
                    "to": strategy.text(),
                    "from": strategy.text(),
                }
            ),
            message=strategy.text(),
            revision=strategy.none(),
            attachment=strategy.none(),
            notificationsEnable=strategy.none(),
        )

    @staticmethod
    def generate_created():
        return strategy.datetimes()

    @classmethod
    def generate_transcript(cls):
        return strategy.lists(
            strategy.builds(
                lambda comm_id, participant, participant_id, text, payload, created: {
                    "comm_id": comm_id,
                    "participant": participant,
                    "participant_id": participant_id,
                    "text": text,
                    "payload": payload,
                    "created": created.strftime("%Y-%m-%d %H:%M:%S"),
                },
                comm_id=cls.generate_comm_id(),
                participant=cls.generate_participant(),
                participant_id=cls.generate_participant_id(),
                text=cls.generate_text(),
                payload=cls.generate_payload(),
                created=cls.generate_created(),
            )
        )
