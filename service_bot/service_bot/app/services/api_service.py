import aiohttp
from aiohttp import BasicAuth
from loguru import logger
from app.config.config import API_USERNAME, API_PASSWORD, BASE_URL

class ApiService:

    def __init__(self):
        self.base_url = BASE_URL
        self.auth = BasicAuth(login=API_USERNAME, password=API_PASSWORD)

        self.use_mock_data = False

    async def _make_request(self, method, endpoint, **kwargs):

        if endpoint == "/test":

            if "/test" in self.base_url:

                url = self.base_url
            else:

                url = f"{self.base_url}/test"
        else:

            if endpoint.startswith("/api"):
                url = f"{self.base_url}{endpoint}"
            else:
                url = f"{self.base_url}/api{endpoint}"

        logger.debug(f"Making {method} request to: {url}")

        kwargs['auth'] = self.auth

        try:

            if not self.use_mock_data:
                async with aiohttp.ClientSession() as session:
                    async with session.request(method, url, **kwargs) as response:
                        logger.debug(f"API response status: {response.status}")

                        try:
                            data = await response.json()
                        except:
                            data = await response.text()
                            return {
                                "status": response.status,
                                "data": {"error": "Ошибка формата данных", "message": data}
                            }

                        api_response = self._transform_api_response(data, endpoint)

                        api_response["status"] = response.status
                        return api_response

            else:
                return 0
        except Exception as e:
            logger.error(f"Error while making API request to {url}: {e}")
            return {"status": 500, "data": {"error": "Ошибка соединения с сервером", "message": str(e)}}

    def _transform_api_response(self, data, endpoint):

        if isinstance(data, dict) and "status" in data:
            return data

        result = {"status": 200, "data": data}

        if "/auth/register" in endpoint or "/auth/login" in endpoint:

            if isinstance(data, dict) and "message" in data:

                if "status" in data:
                    result["status"] = data["status"]

                result["data"] = data
                return result

        if "/api/catalog/categories" in endpoint:

            if "/api/catalog/categories/" in endpoint and isinstance(data, dict) and "category" in data:

                category_data = data.get("category", {})
                category_products = data.get("products", [])

                transformed_category = {
                    "id": category_data.get("id", ""),
                    "code": category_data.get("id", ""),  
                    "name": category_data.get("name", "Категория"),
                    "description": category_data.get("description", "")
                }

                transformed_products = []
                for product in category_products:
                    if isinstance(product, dict):
                        transformed_products.append({
                            "id": product.get("Идентификатор", ""),
                            "code": product.get("Код", ""),
                            "name": product.get("Наименование", "Товар"),
                            "price": product.get("Цена", "По запросу"),
                            "description": product.get("Описание", ""),
                            "stock": product.get("КоличествоНаСкладе", 0),
                            "category": product.get("Категория", ""),
                            "category_name": product.get("КатегорияНаименование", "")
                        })

                result["data"] = {
                    "category": transformed_category,
                    "products": transformed_products
                }
                return result

            logger.debug(f"Оригинальный ответ API для категорий: {data}")

            if isinstance(data, dict) and "categories" in data:
                categories = data.get("categories", [])
                if isinstance(categories, list):
                    transformed_categories = []
                    for category in categories:
                        if isinstance(category, dict):

                            transformed_categories.append({
                                "id": category.get("Идентификатор", ""),
                                "code": category.get("Код", ""),  
                                "name": category.get("Наименование", "Категория"),
                                "description": category.get("Описание", "")
                            })
                        elif isinstance(category, str):
                            transformed_categories.append({"id": category, "name": category, "code": category})
                    result["data"] = transformed_categories

            return result

        elif "/api/catalog/products/category/" in endpoint:

            if isinstance(data, dict) and "products" in data:
                products = data.get("products", [])
                if isinstance(products, list):
                    transformed_products = []
                    for product in products:
                        if isinstance(product, dict):

                            transformed_products.append({
                                "id": product.get("Идентификатор", product.get("Код", "")),
                                "name": product.get("Наименование", "Товар"),
                                "price": product.get("Цена", "По запросу"),
                                "description": product.get("Описание", ""),
                                "stock": product.get("КоличествоНаСкладе", 0),
                                "category": product.get("Категория", ""),
                                "category_name": product.get("КатегорияНаименование", "")
                            })
                        elif isinstance(product, str):
                            transformed_products.append({"id": product, "name": product})
                    result["data"] = transformed_products

        elif "/api/catalog/products" in endpoint and not endpoint.startswith("/api/catalog/products/"):

            if isinstance(data, dict) and "products" in data:
                products = data.get("products", [])
                if isinstance(products, list):
                    transformed_products = []
                    for product in products:
                        if isinstance(product, dict):

                            transformed_products.append({
                                "id": product.get("Идентификатор", ""),
                                "code": product.get("Код", ""),  
                                "name": product.get("Наименование", "Товар"),
                                "price": product.get("Цена", "По запросу"),
                                "description": product.get("Описание", ""),
                                "stock": product.get("КоличествоНаСкладе", 0),
                                "category": product.get("Категория", ""),
                                "category_name": product.get("КатегорияНаименование", "")
                            })
                        elif isinstance(product, str):
                            transformed_products.append({"id": product, "name": product, "code": product})
                    result["data"] = transformed_products

        elif endpoint.startswith("/api/catalog/products/"):

            if isinstance(data, dict) and "product" in data:
                product = data.get("product", {})
                if isinstance(product, dict):

                    transformed_product = {
                        "id": product.get("Идентификатор", ""),
                        "code": product.get("Код", ""),
                        "name": product.get("Наименование", "Без названия"),
                        "price": product.get("Цена", 0),
                        "description": product.get("Описание", "Описание отсутствует"),
                        "stock": product.get("КоличествоНаСкладе", 0),
                        "category": product.get("Категория", ""),
                        "category_name": product.get("КатегорияНаименование", ""),
                        "in_stock": product.get("ВНаличии", False),
                        "min_stock": product.get("МинимальныйЗапас", 0),
                        "supplier": product.get("ПоставщикНаименование", "")
                    }
                    result["data"] = transformed_product
                    return result
                else:
                    logger.error(f"Получен некорректный формат продукта: {product}")
            else:
                logger.error(f"В ответе API отсутствует объект product: {data}")

        elif "/api/catalog/services" in endpoint:

            if isinstance(data, dict) and "services" in data:
                services = data.get("services", [])
                if isinstance(services, list):
                    transformed_services = []
                    for service in services:
                        if isinstance(service, dict):

                            transformed_services.append({
                                "id": service.get("Идентификатор", service.get("Код", "")),
                                "name": service.get("Наименование", "Услуга"),
                                "price": service.get("Цена", "По запросу"),
                                "description": service.get("Описание", ""),
                                "category": service.get("Категория", ""),
                                "category_name": service.get("КатегорияНаименование", "")
                            })
                        elif isinstance(service, str):                            
                            transformed_services.append({"id": service, "name": service})
                    result["data"] = transformed_services

        elif endpoint.startswith("/api/catalog/services/"):

            if isinstance(data, dict):

                if "service" in data:
                    service = data.get("service", {})
                    if isinstance(service, dict):
                        transformed_service = {
                            "id": service.get("id", service.get("Идентификатор", service.get("Код", ""))),
                            "name": service.get("name", service.get("Наименование", "Услуга")),
                            "price": service.get("price", service.get("Цена", "По запросу")),
                            "description": service.get("description", service.get("Описание", "")),
                            "execution_time": service.get("execution_time", 0),
                            "category_id": service.get("category_id", service.get("Категория", "")),
                            "category_name": service.get("category_name", service.get("КатегорияНаименование", ""))
                        }

                        result["data"] = {"service": transformed_service}

                else:

                    result["data"] = data

        logger.debug(f"Трансформированный ответ API для {endpoint}: {result}")

        return result

    async def test_connection(self):

        return await self._make_request("GET", "/test")

    async def get_categories(self):

        return await self._make_request("GET", "/api/catalog/categories")

    async def get_category_by_id(self, category_id):

        logger.debug(f"Запрос информации о категории по коду: {category_id}")
        return await self._make_request("GET", f"/api/catalog/categories/{category_id}")

    async def get_products(self):

        return await self._make_request("GET", "/api/catalog/products")

    async def get_product_by_id(self, product_id):

        logger.debug(f"Запрос товара по коду: {product_id}")
        return await self._make_request("GET", f"/api/catalog/products/{product_id}")

    async def get_products_by_category(self, category_id):

        logger.debug(f"Запрос товаров по коду категории: {category_id}")
        return await self._make_request("GET", f"/api/catalog/products/category/{category_id}")

    async def get_services(self):

        return await self._make_request("GET", "/api/catalog/services")

    async def get_service_by_id(self, service_id):

        logger.debug(f"Запрос услуги по коду: {service_id}")
        return await self._make_request("GET", f"/api/catalog/services/{service_id}")

    async def register_user(self, user_data):

        logger.debug(f"Вызов register_user с данными: {user_data}")
        return await self._make_request("POST", "/auth/register", json=user_data)

    async def login_user(self, credentials):

        return await self._make_request("POST", "/auth/login", json=credentials)

    async def logout_user(self):

        return await self._make_request("POST", "/auth/logout")
    
    async def get_purchase_history_by_phone(self, phone_number: str):
        logger.debug(f"Запрос истории покупок по номеру телефона: {phone_number}")
        
        token = await self.get_current_token()

        headers = {
            "Authorization": f"Bearer {token}"
        }

        return await self._make_request(
            "GET",
            "/api/history/",
            params={"phone": phone_number},
            headers=headers
        )

    async def get_order_statuses(self):
        """Получает список доступных статусов заказов"""
        return await self._make_request("GET", "/orders/statuses/list")
    
    async def get_order_status(self, order_id, order_type="ЗаказПользователя"):
        """Получает текущий статус заказа с указанным ID
        
        Args:
            order_id: ID заказа
            order_type: тип заказа (ЗаказПользователя или ЗаказСТО)
        """
        return await self._make_request(
            "POST", 
            f"/orders/{order_id}/status",
            json={"type": order_type}
        )
    
    async def update_order_status(self, order_id, status, order_type="ЗаказПользователя"):
        """Обновляет статус заказа с указанным ID
        
        Args:
            order_id: ID заказа
            status: новый статус заказа
            order_type: тип заказа (ЗаказПользователя или ЗаказСТО)
        """
        return await self._make_request(
            "PUT",
            f"/orders/{order_id}/status",
            json={"status": status, "type": order_type}
        )
        
api_service = ApiService()
