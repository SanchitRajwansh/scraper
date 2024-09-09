from abc import ABC, abstractmethod

class Notifier(ABC):
    @abstractmethod
    def notify(self, list, email):
        pass

class ConsoleNotifier(Notifier):
    def notify(self, products_length, email = None):
        print(f"Scraped {products_length} products.")

class EmailNotifier(Notifier):
    def notify(self, products_length, email):
        print(f"Email Notified to {email}: Scraped {products_length} products.")