from hypothesis import settings

settings.register_profile("ci", max_examples=40, derandomize=True, deadline=1000)
settings.load_profile("ci")
