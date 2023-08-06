from abc import ABC, abstractmethod


class TransactionManager(ABC):
    @abstractmethod
    def create_transaction(self):
        pass


class PostgresTransactionManager(TransactionManager):

    def test(self):
        pass
