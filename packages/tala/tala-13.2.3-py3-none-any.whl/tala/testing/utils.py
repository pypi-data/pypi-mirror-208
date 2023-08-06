from tala.config import BackendConfig
from tala.log import logger


class EqualityAssertionTestCaseMixin:
    def assert_eq_returns_true_and_ne_returns_false_symmetrically(self, object1, object2):
        assert object1 == object2
        assert not (object1 != object2)
        assert object2 == object1
        assert not (object2 != object1)

    def assert_eq_returns_false_and_ne_returns_true_symmetrically(self, object1, object2):
        assert object1 != object2
        assert not (object1 == object2)
        assert object2 != object1
        assert not (object2 == object1)


def load_mockup_travel(component_set_loader):
    load_internal_ddds(component_set_loader, ["mockup_travel"], "tala")


def load_internal_ddds(component_set_loader, ddds, package, rerank_amount=None):
    rerank_amount = rerank_amount or BackendConfig.DEFAULT_RERANK_AMOUNT
    test_logger = logger.configure_and_get_test_logger()
    component_set_loader.ensure_ddds_loaded(
        ddds, path=f"{package}/ddds", logger=test_logger, rerank_amount=rerank_amount
    )
