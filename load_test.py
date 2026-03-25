import asyncio
import aiohttp
import time
from statistics import mean

BASE_URL = "http://127.0.0.1:8000/api"
TOTAL_REQUESTS = 1000  # Общее количество запросов
CONCURRENT_USERS = 10  # Количество одновременных "пользователей"

class LoadTestResult:
    """Результаты нагрузочного теста"""
    def __init__(self, endpoint: str):
        self.endpoint = endpoint
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.response_times = []
        self.start_time = None
        self.end_time = None

    @property
    def avg_response_time(self) -> float:
        return mean(self.response_times) if self.response_times else 0

    @property
    def min_response_time(self) -> float:
        return min(self.response_times) if self.response_times else 0

    @property
    def max_response_time(self) -> float:
        return max(self.response_times) if self.response_times else 0

    @property
    def requests_per_second(self) -> float:
        duration = (self.end_time - self.start_time) if self.end_time and self.start_time else 0
        return self.total_requests / duration if duration > 0 else 0

    @property
    def success_rate(self) -> float:
        return (self.successful_requests / self.total_requests * 100) if self.total_requests > 0 else 0

    def __str__(self):
        return f"""
Эндпоинт: {self.endpoint}

Всего запросов: {self.total_requests}
Успешных ответов: {self.successful_requests}
Ошибок: {self.failed_requests}
% успешных ответов: {self.success_rate:.2f}

Среднее время ответа: {self.avg_response_time:.2f}
Мин. время: {self.min_response_time:.2f}
Макс. время: {self.max_response_time:.2f}

Запросов в секунду: {self.requests_per_second:.2f}
Длительность теста: {(self.end_time - self.start_time):.2f} сек
"""

async def make_request(
    session: aiohttp.ClientSession,
    method: str,
    url: str,
    result: LoadTestResult,
    data: dict = None,
    headers: dict = None
) -> None:
    """Выполнение одного запроса"""
    start = time.perf_counter()
    
    try:
        async with session.request(method, url, json=data, headers=headers) as response:
            elapsed = (time.perf_counter() - start) * 1000  # мс
            result.response_times.append(elapsed)
            result.total_requests += 1
            
            if 200 <= response.status < 300:
                result.successful_requests += 1
            else:
                result.failed_requests += 1
                
    except Exception as e:
        result.total_requests += 1
        result.failed_requests += 1
        print(f"Ошибка запроса: {e}")


async def load_test_endpoint(
    session: aiohttp.ClientSession,
    method: str,
    endpoint: str,
    num_requests: int) -> LoadTestResult:
    """Нагрузочное тестирование одного endpoint"""
    url = f"{BASE_URL}{endpoint}"
    result = LoadTestResult(endpoint)
    result.start_time = time.time()
    
    semaphore = asyncio.Semaphore(CONCURRENT_USERS)
    
    async def limited_request():
        async with semaphore:
            await make_request(session, method, url, result)
    
    tasks = [limited_request() for _ in range(num_requests)]
    await asyncio.gather(*tasks)
    
    result.end_time = time.time()
    return result


async def run_load_tests():
    """Запуск всех нагрузочных тестов""" 
    async with aiohttp.ClientSession() as session:
        tests_endpoints = ["/doctors/", "/reservations/", "/notifications/", "/user/info/"]
        
        for endpoint in tests_endpoints:
            result = await load_test_endpoint(session, "GET", endpoint, TOTAL_REQUESTS)
            print(result)

        # print("Тест GET /api/doctors/ (получение списка врачей)")
        # result = await load_test_endpoint(session, "GET", "/doctors/", TOTAL_REQUESTS)
        # print(result)
        
        # print("Тест GET /api/reservations/ (получение списка записей)")
        # result = await load_test_endpoint(session, "GET", "/reservations/", TOTAL_REQUESTS)
        # print(result)
        
        # print("Тест GET /api/notifications/ (получение уведомлений)")
        # result = await load_test_endpoint(session, "GET", "/notifications/", TOTAL_REQUESTS)
        # print(result)
        
        # print("Тест GET /api/user/info/ (информация о пользователе)")
        # result = await load_test_endpoint(session, "GET", "/user/info/", TOTAL_REQUESTS)
        # print(result)


if __name__ == "__main__":
    asyncio.run(run_load_tests())
