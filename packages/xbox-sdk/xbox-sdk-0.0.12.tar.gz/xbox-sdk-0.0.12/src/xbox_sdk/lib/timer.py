from time import sleep


class Timer:
    def __init__(self, client):
        self.__client = client
        rate = self.__client.calls_remaining()
        self.reset_timer = int(rate['X-RateLimit-Reset'])
        self.limit = int(rate['X-RateLimit-Limit'])
        self.remaining = int(rate['X-RateLimit-Remaining']) - 1

    def is_limit_reset(self):
        rate = self.__client.calls_remaining()
        self.remaining = int(rate['X-RateLimit-Remaining'])
        if self.remaining > 0:
            self.remaining -= 1
            self.reset_timer = int(rate['X-RateLimit-Reset'])
            return True
        return False

    def start_timeout(self):
        self.remaining = 0
        message = "\033[31;1m[Limit Exceeded]\033[0;32m Time Until Reset: \033[92m{:02d}:{:02d}\033[0m"
        while self.reset_timer >= 0:# and not self.is_limit_reset():
            print(message.format(self.reset_timer // 60, self.reset_timer % 60), end='\r')
            sleep(1)
            self.reset_timer -= 1
        print()
