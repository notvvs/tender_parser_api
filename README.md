# Tender Parser API

Парсер тендеров с zakupki.gov.ru

## Запуск

```bash
docker-compose up
```

## API

### Эндпоинт
```
POST /api/v1/parser/parse
```

### Заголовки
```
X-API-Key: secret_api_key
Content-Type: application/json
```

### Тело запроса
```json
{
  "url": "https://zakupki.gov.ru/epz/order/notice/ea20/view/common-info.html?regNumber=0123456789012345678"
}
```

### Пример curl
```bash
curl -X POST "http://localhost:8000/api/v1/parser/parse" \
  -H "X-API-Key: secret_api_key" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://zakupki.gov.ru/epz/order/notice/ea20/view/common-info.html?regNumber=0123456789012345678"}'
```

### Ответ
```json
{
  "tenderInfo": {
    "tenderName": "Поставка оборудования",
    "tenderNumber": "0123456789012345678",
    "customerName": "ФГБУ Заказчик",
    "purchaseType": "Электронный аукцион",
    "maxPrice": {
      "amount": 1000000.0,
      "currency": "RUB"
    },
    "deliveryInfo": {
      "deliveryAddress": "г. Москва, ул. Ленина, д. 1",
      "deliveryTerm": "Начало: 01.01.2025; Окончание: 31.12.2025",
      "deliveryConditions": "Требуется обеспечение исполнения контракта: 5%"
    },
    "paymentInfo": {
      "paymentTerm": "В течение 30 дней",
      "paymentMethod": "Безналичный расчет",
      "paymentConditions": "ИНН 1234567890 КПП 123456789 р/с 40702810000000000000"
    }
  },
  "items": [
    {
      "id": 1,
      "name": "Ноутбук",
      "okpd2Code": "26.20.11.110",
      "ktruCode": "26.20.11.110-00000001",
      "quantity": 10,
      "unitOfMeasurement": "шт",
      "unitPrice": {
        "amount": 50000.0,
        "currency": "RUB"
      },
      "totalPrice": {
        "amount": 500000.0,
        "currency": "RUB"
      },
      "characteristics": [
        {
          "id": 1,
          "name": "Процессор",
          "value": "Intel Core i5",
          "unit": null,
          "type": "Качественная",
          "required": true,
          "changeable": false
        }
      ]
    }
  ],
  "generalRequirements": {
    "warrantyRequirements": "Гарантия 12 месяцев"
  },
  "attachments": [
    {
      "name": "Техническое задание",
      "type": "pdf",
      "url": "https://zakupki.gov.ru/epz/filestore/public/2.0/download/...",
      "description": null
    }
  ]
}
```

### Коды ошибок
- `400` - Невалидный URL
- `401` - Нет API ключа
- `403` - Неверный API ключ
- `404` - Тендер не найден
- `500` - Ошибка парсинга

## Документация
- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc